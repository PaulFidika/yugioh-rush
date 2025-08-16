#!/usr/bin/env python3
"""
Generate Updated PDFs for Chimeratech Cyber and Harpie Lady Sisters Decks
Uses the local card database and updated card lists to generate new PDFs
"""
import os
import re
import json
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def load_card_database():
    """Load the local Rush Duel card database"""
    db_file = "/home/fidika/yugioh-rush/rush_duel_complete_database.json"
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def parse_deck_file(filename):
    """Parse deck file using the new format with EDOPro IDs"""
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
        elif line == 'SPELL CARDS:':
            current_type = 'Spell'
            continue
        elif line == 'TRAP CARDS:':
            current_type = 'Trap'
            continue
        
        # Parse card lines with EDOPro IDs
        # Format: "1. Card Name (EDOPro: 160301001)"
        match = re.match(r'^\d+\.\s*(.+?)(?:\s*\(EDOPro:\s*([^)]+)\))?', line)
        if match and current_type:
            card_name = match.group(1).strip()
            edopro_id = match.group(2).strip() if match.group(2) else None
            
            # Skip lines that are just descriptions or notes
            if not card_name or card_name.startswith('Level') or card_name.startswith('Fusion') or card_name.startswith('Available'):
                continue
            
            cards.append({
                'name': card_name,
                'type': current_type,
                'edopro_id': edopro_id
            })
    
    return cards

def get_card_info_from_database(edopro_id, card_database):
    """Get card information from the database using EDOPro ID"""
    if not card_database or not edopro_id:
        return None
    
    cards_data = card_database.get("cards", {})
    return cards_data.get(str(edopro_id), None)

def create_card_description(card_name, card_info):
    """Create a text description for a card"""
    if not card_info:
        return f"{card_name}\n\nCard information not found in database."
    
    description = f"{card_name}\n\n"
    
    if card_info.get('type') == 'Monster':
        if card_info.get('atk') and card_info.get('def'):
            description += f"ATK: {card_info.get('atk')} DEF: {card_info.get('def')}\n"
        if card_info.get('level'):
            description += f"Level: {card_info.get('level')}\n"
        if card_info.get('attribute'):
            description += f"Attribute: {card_info.get('attribute')}\n"
    
    if card_info.get('description'):
        desc_text = card_info.get('description')[:200] + "..." if len(card_info.get('description', '')) > 200 else card_info.get('description')
        description += f"\n{desc_text}"
    
    return description

def create_pdf_page(c, card_items, page_width, page_height, card_width, card_height, margin, header_space):
    """Create a page with up to 4 card descriptions in a 2x2 grid"""
    gap = 0.2 * inch  # Gap between cards
    
    for i, item in enumerate(card_items):
        if i >= 4:
            break
        
        row = i // 2
        col = i % 2
        
        x = margin + col * (card_width + gap)
        y = page_height - margin - header_space - (row + 1) * card_height - row * gap
        
        # Draw border
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(2)
        c.rect(x, y, card_width, card_height)
        
        # Draw card name at top
        c.setFont("Helvetica-Bold", 12)
        text_y = y + card_height - 20
        
        # Wrap card name if too long
        card_name = item['name']
        name_lines = []
        if len(card_name) > 25:
            words = card_name.split()
            line = ""
            for word in words:
                if len(line + " " + word) <= 25:
                    line += (" " + word) if line else word
                else:
                    if line:
                        name_lines.append(line)
                    line = word
            if line:
                name_lines.append(line)
        else:
            name_lines = [card_name]
        
        for name_line in name_lines:
            c.drawString(x + 5, text_y, name_line)
            text_y -= 14
        
        # Draw description
        c.setFont("Helvetica", 8)
        text_y -= 10
        
        description = item.get('description', 'No description available')
        
        # Wrap description text
        desc_lines = []
        for paragraph in description.split('\n'):
            if not paragraph.strip():
                desc_lines.append("")
                continue
            
            words = paragraph.split()
            line = ""
            chars_per_line = int((card_width - 10) / 4.8)  # Approximate characters per line
            
            for word in words:
                if len(line + " " + word) <= chars_per_line:
                    line += (" " + word) if line else word
                else:
                    if line:
                        desc_lines.append(line)
                    line = word
            if line:
                desc_lines.append(line)
        
        for desc_line in desc_lines:
            if text_y < y + 10:  # Stop if we're near the bottom
                break
            c.drawString(x + 5, text_y, desc_line)
            text_y -= 10

def generate_deck_pdf(deck_name, cards, card_database, output_filename):
    """Generate a PDF for a deck using card information from database"""
    # Page setup - maximize card size for 2x2 grid
    page_width, page_height = letter
    margin = 0.4 * inch  # Margin around the page
    header_space = 0.6 * inch  # Space for header
    gap = 0.2 * inch  # Gap between cards
    
    # Calculate maximum card size for 2x2 grid to fill the page
    available_width = page_width - 2 * margin - gap
    available_height = page_height - 2 * margin - header_space - gap
    
    card_width = available_width / 2
    card_height = available_height / 2
    
    # Create PDF
    c = canvas.Canvas(output_filename, pagesize=letter)
    
    # Group cards by type and remove duplicates
    monster_cards = []
    spell_cards = []
    trap_cards = []
    seen_cards = set()
    
    for card in cards:
        # Only add each unique card once
        if card['name'] not in seen_cards:
            card_info = get_card_info_from_database(card['edopro_id'], card_database)
            card_item = {
                'name': card['name'],
                'description': create_card_description(card['name'], card_info),
                'edopro_id': card['edopro_id']
            }
            
            seen_cards.add(card['name'])
            
            if card['type'] == 'Monster':
                monster_cards.append(card_item)
            elif card['type'] == 'Spell':
                spell_cards.append(card_item)
            elif card['type'] == 'Trap':
                trap_cards.append(card_item)
    
    # Create pages for each card type
    first_page = True
    
    for card_type, card_list in [('Monster', monster_cards), ('Spell', spell_cards), ('Trap', trap_cards)]:
        if not card_list:
            continue
            
        # Process cards in groups of 4 (2x2 grid)
        for i in range(0, len(card_list), 4):
            page_cards = card_list[i:i+4]
            
            # Start new page if not first page
            if not first_page:
                c.showPage()
            
            # Add header for each page
            c.setFont("Helvetica-Bold", 20)
            c.drawString(margin, page_height - margin/2, f"{deck_name} - {card_type} Cards")
            c.setFont("Helvetica", 10)
            c.drawString(margin, page_height - margin/2 - 20, f"Page {i//4 + 1} - Cards {i+1}-{min(i+4, len(card_list))}")
            
            # Create the page
            create_pdf_page(c, page_cards, page_width, page_height, 
                          card_width, card_height, margin, header_space)
            
            first_page = False
    
    c.save()
    print(f"✅ Generated {output_filename}")

def main():
    print("Generating Updated PDFs for Chimeratech Cyber and Harpie Lady Sisters Decks")
    print("=" * 80)
    
    # Load card database
    print("Loading card database...")
    card_database = load_card_database()
    if not card_database:
        print("❌ Could not load card database!")
        return
    print(f"✅ Loaded database with {len(card_database.get('cards', {}))} cards")
    
    # Process Chimeratech Cyber deck
    print("\nProcessing Chimeratech Cyber deck...")
    chimeratech_file = "/home/fidika/yugioh-rush/structure-decks-txt/chimeratech_cyber_deck_cards.txt"
    chimeratech_cards = parse_deck_file(chimeratech_file)
    print(f"Found {len(chimeratech_cards)} cards in Chimeratech Cyber deck")
    
    chimeratech_output = "/home/fidika/yugioh-rush/structure-decks-pdf/chimeratech_cyber_deck_updated.pdf"
    generate_deck_pdf("Chimeratech Cyber Deck", chimeratech_cards, card_database, chimeratech_output)
    
    # Process Harpie Lady Sisters deck
    print("\nProcessing Harpie Lady Sisters deck...")
    harpie_file = "/home/fidika/yugioh-rush/structure-decks-txt/harpie_lady_sisters_deck_cards.txt"
    harpie_cards = parse_deck_file(harpie_file)
    print(f"Found {len(harpie_cards)} cards in Harpie Lady Sisters deck")
    
    harpie_output = "/home/fidika/yugioh-rush/structure-decks-pdf/harpie_lady_sisters_deck_updated.pdf"
    generate_deck_pdf("Harpie Lady Sisters Deck", harpie_cards, card_database, harpie_output)
    
    print(f"\n🎉 Successfully generated updated PDFs!")
    print(f"Generated files:")
    print(f"- {chimeratech_output}")
    print(f"- {harpie_output}")

if __name__ == "__main__":
    main()