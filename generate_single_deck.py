#!/usr/bin/env python3
import os
import re
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import sys

def clean_card_name(name):
    """Convert card name to match image filename format"""
    # Remove parenthetical content
    name = re.sub(r'\s*\([^)]*\)', '', name)
    # Remove numbers at the beginning (like "1. ")
    name = re.sub(r'^\d+\.\s*', '', name)
    # Replace apostrophes with hyphens
    name = name.replace("'", '-')
    # Replace spaces with hyphens
    name = name.replace(' ', '-')
    # Remove other special characters except hyphens
    name = re.sub(r'[^\w\-]', '', name)
    # Clean up multiple hyphens
    name = re.sub(r'-+', '-', name)
    # Remove trailing hyphens
    name = name.rstrip('-')
    return name

def find_image_file(card_name, image_dir, edopro_id=None):
    """Find the image file for a card"""
    
    # For Rush-Cards-Deviant-Art folder, use cleaned name matching
    clean_name = clean_card_name(card_name)
    
    # Try the exact clean name first
    filename = f"{clean_name}.jpg"
    filepath = os.path.join(image_dir, filename)
    if os.path.exists(filepath):
        return filepath
    
    # If not found, try variations
    variations = [
        f"{clean_name}.png",
        f"{clean_name}.jpeg",
    ]
    
    for var in variations:
        filepath = os.path.join(image_dir, var)
        if os.path.exists(filepath):
            return filepath
    
    return None

def parse_deck_new_format(filename):
    """Parse deck files using the new Blue Eyes-style format"""
    cards = []
    current_type = None
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        
        # Check for section headers
        if line == 'EXTRA DECK:':
            current_type = 'Monster'  # Treat Extra Deck monsters as monsters for PDF layout
            continue
        elif line == 'MONSTER CARDS:':
            current_type = 'Monster'
            continue
        elif line == 'FUSION MONSTERS:':
            current_type = 'Monster'  # Legacy support - treat as monsters
            continue
        elif line == 'RITUAL MONSTERS:':
            current_type = 'Monster'  # Treat ritual monsters as monsters for PDF layout
            continue
        elif line == 'SPELL CARDS:':
            current_type = 'Spell'
            continue
        elif line == 'TRAP CARDS:':
            current_type = 'Trap'
            continue
        elif line.startswith('**') or line == '' or line.startswith('Yu-Gi-Oh!') or line.startswith('Card List') or line.startswith('Set Code') or line.startswith('Release Date') or line.startswith('Format'):
            continue
        
        # Parse card lines - look for format like "1. Card Name (EDOPro: 123456789)"
        match = re.match(r'^\d+\.\s+(.+?)\s+\(EDOPro:\s*(\d+)\)', line)
        if match and current_type:
            card_name = match.group(1).strip()
            edopro_id = match.group(2) if match.group(2) else None
            
            # Skip cards marked as UNKNOWN or missing
            if not edopro_id or edopro_id == "UNKNOWN":
                continue
                
            card = {
                'name': card_name,
                'type': current_type,
                'edopro_id': edopro_id
            }
            cards.append(card)
    
    return cards

def create_pdf_with_text_fallback(output_file, cards, image_dir):
    """Create PDF with images or text descriptions"""
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter
    
    # Group cards by type
    monsters = [card for card in cards if card['type'] == 'Monster']
    spells = [card for card in cards if card['type'] == 'Spell']
    traps = [card for card in cards if card['type'] == 'Trap']
    
    all_groups = [
        ("MONSTER CARDS", monsters),
        ("SPELL CARDS", spells), 
        ("TRAP CARDS", traps)
    ]
    
    current_page = 0
    
    for section_name, card_group in all_groups:
        if not card_group:
            continue
            
        # Process cards in groups of 4 (2x2 grid)
        for i in range(0, len(card_group), 4):
            if current_page > 0:
                c.showPage()
            
            # Add section title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, section_name)
            
            # Get up to 4 cards for this page
            page_cards = card_group[i:i+4]
            
            # Define positions for 2x2 grid
            positions = [
                (50, height - 450),    # Top left
                (width/2 + 25, height - 450),  # Top right
                (50, height - 750),    # Bottom left
                (width/2 + 25, height - 750)   # Bottom right
            ]
            
            card_width = width/2 - 75
            card_height = 250
            
            for j, card in enumerate(page_cards):
                x, y = positions[j]
                
                # Try to find image
                image_path = find_image_file(card['name'], image_dir, card.get('edopro_id'))
                
                if image_path and os.path.exists(image_path):
                    try:
                        # Draw image
                        img = Image.open(image_path)
                        img_aspect = img.width / img.height
                        
                        # Calculate scaled dimensions
                        if img_aspect > (card_width / card_height):
                            # Image is wider - fit to width
                            scaled_width = card_width
                            scaled_height = card_width / img_aspect
                        else:
                            # Image is taller - fit to height
                            scaled_height = card_height
                            scaled_width = card_height * img_aspect
                        
                        # Center the image in the allocated space
                        centered_x = x + (card_width - scaled_width) / 2
                        centered_y = y + (card_height - scaled_height) / 2
                        
                        c.drawImage(image_path, centered_x, centered_y, 
                                  width=scaled_width, height=scaled_height)
                        
                        # Add card name below image
                        c.setFont("Helvetica", 10)
                        c.drawString(x, y - 20, card['name'])
                        
                        print(f"✓ Added image for: {card['name']}")
                        
                    except Exception as e:
                        print(f"✗ Error loading image for {card['name']}: {e}")
                        # Fall back to text
                        c.setFont("Helvetica", 12)
                        c.drawString(x, y + card_height/2, f"Card: {card['name']}")
                        c.setFont("Helvetica", 10)
                        c.drawString(x, y + card_height/2 - 20, f"EDOPro ID: {card.get('edopro_id', 'Unknown')}")
                        c.drawString(x, y + card_height/2 - 40, f"Type: {card['type']}")
                
                else:
                    # Text fallback
                    print(f"✗ Image not found for: {card['name']} (EDOPro: {card.get('edopro_id', 'Unknown')})")
                    c.setFont("Helvetica", 12)
                    c.drawString(x, y + card_height/2, f"Card: {card['name']}")
                    c.setFont("Helvetica", 10)
                    c.drawString(x, y + card_height/2 - 20, f"EDOPro ID: {card.get('edopro_id', 'Unknown')}")
                    c.drawString(x, y + card_height/2 - 40, f"Type: {card['type']}")
            
            current_page += 1
    
    c.save()
    print(f"PDF saved as: {output_file}")

def main():
    # Generate for Black Magic Ritual deck only
    deck_file = "Structure-Decks/black_magic_ritual_deck_cards.txt"
    
    if not os.path.exists(deck_file):
        print(f"Deck file not found: {deck_file}")
        return
    
    # Parse the deck
    cards = parse_deck_new_format(deck_file)
    print(f"Found {len(cards)} cards in deck")
    
    # Use Rush-Cards-Deviant-Art folder
    image_dir = "Rush-Cards-Deviant-Art"
    
    # Generate PDF
    output_file = "Structure-Decks/black_magic_ritual_deck_cards_hd.pdf"
    create_pdf_with_text_fallback(output_file, cards, image_dir)
    
    print(f"Generated PDF: {output_file}")

if __name__ == "__main__":
    main()