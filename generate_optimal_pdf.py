#!/usr/bin/env python3
"""
Optimal PDF Generator using matplotlib for 2x2 card layout
No HTML intermediary - Direct PDF with maximum card size for printing
"""
import os
import re
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

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
            current_type = 'Monster'
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
        
        # Parse card lines
        match = re.match(r'^\d+\.\s*(.+?)\s*\(EDOPro:\s*([^)]+)\)', line)
        if match and current_type:
            card_name = match.group(1).strip()
            edopro_id = match.group(2).strip()
            
            if not edopro_id:
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

def create_matplotlib_pdf(deck_name, cards, card_database, images_dir, output_filename):
    """Create PDF using matplotlib with 2x2 layout for maximum card size"""
    
    # Remove duplicates
    unique_cards = []
    seen_cards = set()
    
    for card in cards:
        if card['name'] not in seen_cards:
            seen_cards.add(card['name'])
            unique_cards.append(card)
    
    print(f"Creating PDF with {len(unique_cards)} unique cards...")
    
    # Create PDF with A4 size and minimal margins
    with PdfPages(output_filename) as pdf:
        
        # Process cards in groups of 4 (2x2 per page)
        for page_start in range(0, len(unique_cards), 4):
            page_cards = unique_cards[page_start:page_start + 4]
            
            # Create figure with A4 proportions and minimal margins
            fig, axes = plt.subplots(2, 2, figsize=(8.27, 11.69))  # A4 size in inches
            fig.suptitle(f"{deck_name} - Page {page_start//4 + 1}", fontsize=14, fontweight='bold')
            
            # Remove spacing between subplots for maximum card size
            fig.subplots_adjust(left=0.02, right=0.98, top=0.94, bottom=0.02, wspace=0.02, hspace=0.02)
            
            # Fill each subplot with a card
            for i in range(4):
                row = i // 2
                col = i % 2
                ax = axes[row, col]
                
                if i < len(page_cards):
                    card = page_cards[i]
                    
                    # Try to load and display card image
                    image_path = os.path.join(images_dir, f"{card['edopro_id']}.png")
                    
                    if os.path.exists(image_path):
                        try:
                            # Load and display card image
                            img = plt.imread(image_path)
                            ax.imshow(img, aspect='auto')
                        except Exception as e:
                            print(f"  ⚠️  Could not load image {card['edopro_id']}: {e}")
                            # Create placeholder
                            ax.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor='lightgray', edgecolor='black'))
                            ax.text(0.5, 0.5, 'Image\nNot Available', ha='center', va='center', fontsize=12)
                            ax.set_xlim(0, 1)
                            ax.set_ylim(0, 1)
                    else:
                        # Create placeholder for missing image
                        ax.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor='lightgray', edgecolor='black'))
                        ax.text(0.5, 0.5, 'Image\nNot Available', ha='center', va='center', fontsize=12)
                        ax.set_xlim(0, 1)
                        ax.set_ylim(0, 1)
                    
                    # Add card information as title
                    card_info = get_card_info_from_database(card['edopro_id'], card_database)
                    
                    # Create title with card name and stats
                    title = card['name']
                    if len(title) > 25:
                        title = title[:22] + "..."
                    
                    subtitle = f"ID: {card['edopro_id']}"
                    if card_info and card_info.get('atk') and card_info.get('def'):
                        subtitle += f" | ATK: {card_info['atk']} DEF: {card_info['def']}"
                    if card_info and card_info.get('level'):
                        subtitle += f" | Lv: {card_info['level']}"
                    
                    ax.set_title(f"{title}\n{subtitle}", fontsize=8, pad=2)
                    
                else:
                    # Empty subplot for pages with less than 4 cards
                    ax.set_visible(False)
                
                # Remove axes for clean look
                ax.set_xticks([])
                ax.set_yticks([])
            
            # Save this page to PDF
            pdf.savefig(fig, bbox_inches='tight', pad_inches=0.1)
            plt.close(fig)
    
    print(f"✅ Generated optimized PDF: {output_filename}")
    return True

def main():
    print("Optimal PDF Generator - 2x2 Layout with matplotlib")
    print("=" * 60)
    
    # Check if matplotlib is available
    try:
        import matplotlib.pyplot as plt
        print("✅ matplotlib available")
    except ImportError:
        print("❌ matplotlib not available - cannot generate PDFs")
        return
    
    # Load card database
    print("Loading card database...")
    card_database = load_card_database()
    if not card_database:
        print("❌ Could not load card database!")
        return
    print(f"✅ Loaded database with {len(card_database.get('cards', {}))} cards")
    
    # Check images directory
    images_dir = "/home/fidika/yugioh-rush/Rush-HD-Pictures/pics"
    if not os.path.exists(images_dir):
        print(f"❌ Rush-HD-Pictures directory not found: {images_dir}")
        return
    
    image_count = len([f for f in os.listdir(images_dir) if f.endswith('.png')])
    print(f"✅ Found {image_count} HD card images")
    
    # List of decks to process
    decks_to_process = [
        ("chimeratech_cyber_deck_cards.txt", "Chimeratech Cyber Structure Deck"),
        ("harpie_lady_sisters_deck_cards.txt", "Harpie Lady Sisters Structure Deck"),
        ("yuga_deck_cards.txt", "Yuga's Sevens Road Starter Deck")
    ]
    
    for deck_file, deck_display_name in decks_to_process:
        print(f"\n" + "="*50)
        print(f"Processing {deck_display_name}")
        print("="*50)
        
        deck_path = f"/home/fidika/yugioh-rush/structure-decks-txt/{deck_file}"
        if not os.path.exists(deck_path):
            print(f"❌ Deck file not found: {deck_path}")
            continue
        
        cards = parse_deck_file(deck_path)
        print(f"Found {len(cards)} cards")
        
        # Check available images
        available_images = 0
        for card in cards:
            image_path = os.path.join(images_dir, f"{card['edopro_id']}.png")
            if os.path.exists(image_path):
                available_images += 1
        
        print(f"✅ {available_images}/{len(cards)} card images available")
        
        # Generate PDF
        base_name = deck_file.replace('_cards.txt', '').replace('_deck', '')
        pdf_output = f"/home/fidika/yugioh-rush/structure-decks-pdf/{base_name}_optimal.pdf"
        
        create_matplotlib_pdf(deck_display_name, cards, card_database, images_dir, pdf_output)
    
    print(f"\n🎉 Generated optimal PDFs with 2x2 layout and maximum card size!")
    print("Files ready for high-quality printing")

if __name__ == "__main__":
    main()