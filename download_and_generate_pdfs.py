#!/usr/bin/env python3
"""
Download Rush Duel card images and generate PDFs for Chimeratech Cyber and Harpie Lady Sisters Decks
Uses YGOProDeck API to download card images by EDOPro ID
"""
import os
import re
import json
import urllib.request
import urllib.error
from pathlib import Path

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
        content = f.read()
    
    # Split by double newlines to get card blocks
    sections = content.split('\n\n')
    
    for section in sections:
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        first_line = lines[0].strip()
        
        # Check for section headers
        if first_line == 'EXTRA DECK:':
            current_type = 'Monster'  # Treat Extra Deck monsters as monsters for PDF layout
            continue
        elif first_line == 'MONSTER CARDS:':
            current_type = 'Monster'
            continue
        elif first_line == 'SPELL CARDS:':
            current_type = 'Spell'
            continue
        elif first_line == 'TRAP CARDS:':
            current_type = 'Trap'
            continue
        
        # Parse card entries - look for lines starting with numbers
        for line in lines:
            line = line.strip()
            # Format: "1. Card Name (EDOPro: 160301001)"
            match = re.match(r'^\d+\.\s*(.+?)\s*\(EDOPro:\s*([^)]+)\)', line)
            if match and current_type:
                card_name = match.group(1).strip()
                edopro_id = match.group(2).strip()
                
                # Skip if no EDOPro ID found
                if not edopro_id:
                    continue
                
                cards.append({
                    'name': card_name,
                    'type': current_type,
                    'edopro_id': edopro_id
                })
    
    return cards

def download_card_image(edopro_id, output_dir):
    """Download card image by EDOPro ID from various sources"""
    if not edopro_id:
        return None
    
    # Create pics directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Define possible image URLs
    image_urls = [
        f"https://images.ygoprodeck.com/images/cards/{edopro_id}.jpg",
        f"https://storage.googleapis.com/ygoprodeck.com/pics/{edopro_id}.jpg",
        f"https://ms.yugipedia.com//thumb/{edopro_id}.png/300px-{edopro_id}.png"
    ]
    
    output_file = os.path.join(output_dir, f"{edopro_id}.jpg")
    
    # Skip if already downloaded
    if os.path.exists(output_file):
        print(f"  ✓ {edopro_id}.jpg (already exists)")
        return output_file
    
    for url in image_urls:
        try:
            print(f"  Downloading {edopro_id} from {url.split('/')[2]}...")
            urllib.request.urlretrieve(url, output_file)
            print(f"  ✓ Downloaded {edopro_id}.jpg")
            return output_file
        except urllib.error.URLError as e:
            print(f"  ✗ Failed to download from {url.split('/')[2]}: {e}")
            continue
        except Exception as e:
            print(f"  ✗ Error downloading {edopro_id}: {e}")
            continue
    
    print(f"  ⚠️  Could not download image for {edopro_id}")
    return None

def create_simple_html_deck(deck_name, cards, card_database, images_dir, output_filename):
    """Create a simple HTML file showing the deck cards"""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{deck_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .deck-header {{ text-align: center; margin-bottom: 30px; }}
        .card-section {{ margin-bottom: 40px; }}
        .card-section h2 {{ color: #333; border-bottom: 2px solid #333; padding-bottom: 5px; }}
        .cards-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }}
        .card {{ border: 1px solid #ccc; padding: 10px; text-align: center; }}
        .card img {{ max-width: 100%; height: auto; }}
        .card-name {{ font-weight: bold; margin-top: 10px; }}
        .card-info {{ font-size: 12px; color: #666; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="deck-header">
        <h1>{deck_name}</h1>
        <p>Complete card list with images from EDOPro database</p>
    </div>
"""
    
    # Group cards by type
    monster_cards = []
    spell_cards = []
    trap_cards = []
    
    for card in cards:
        if card['type'] == 'Monster':
            monster_cards.append(card)
        elif card['type'] == 'Spell':
            spell_cards.append(card)
        elif card['type'] == 'Trap':
            trap_cards.append(card)
    
    # Add sections for each card type
    for section_name, card_list in [('Monster Cards', monster_cards), ('Spell Cards', spell_cards), ('Trap Cards', trap_cards)]:
        if not card_list:
            continue
        
        html_content += f"""
    <div class="card-section">
        <h2>{section_name} ({len(card_list)} cards)</h2>
        <div class="cards-grid">
"""
        
        seen_cards = set()
        for card in card_list:
            if card['name'] in seen_cards:
                continue
            seen_cards.add(card['name'])
            
            image_file = os.path.join(images_dir, f"{card['edopro_id']}.jpg")
            card_info = card_database.get("cards", {}).get(str(card['edopro_id']), {}) if card_database else {}
            
            # Create card HTML
            image_src = f"pics/{card['edopro_id']}.jpg" if os.path.exists(image_file) else ""
            
            html_content += f"""
            <div class="card">
                {"<img src='" + image_src + "' alt='" + card['name'] + "'>" if image_src else "<div style='height: 200px; background: #f0f0f0; display: flex; align-items: center; justify-content: center;'>No Image</div>"}
                <div class="card-name">{card['name']}</div>
                <div class="card-info">EDOPro ID: {card['edopro_id']}</div>
                {"<div class='card-info'>ATK: " + str(card_info.get('atk', '')) + " DEF: " + str(card_info.get('def', '')) + "</div>" if card_info.get('atk') and card_info.get('def') else ""}
            </div>
"""
        
        html_content += """
        </div>
    </div>
"""
    
    html_content += """
</body>
</html>
"""
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Generated {output_filename}")

def main():
    print("Downloading Rush Duel card images and generating deck displays")
    print("=" * 70)
    
    # Create images directory
    images_dir = "/home/fidika/yugioh-rush/pics"
    os.makedirs(images_dir, exist_ok=True)
    
    # Load card database
    print("Loading card database...")
    card_database = load_card_database()
    if not card_database:
        print("❌ Could not load card database!")
        return
    print(f"✅ Loaded database with {len(card_database.get('cards', {}))} cards")
    
    # Process Chimeratech Cyber deck
    print("\n" + "="*50)
    print("Processing Chimeratech Cyber deck...")
    print("="*50)
    chimeratech_file = "/home/fidika/yugioh-rush/structure-decks-txt/chimeratech_cyber_deck_cards.txt"
    chimeratech_cards = parse_deck_file(chimeratech_file)
    print(f"Found {len(chimeratech_cards)} cards in Chimeratech Cyber deck")
    
    # Download images for Chimeratech cards
    print("Downloading card images...")
    seen_ids = set()
    for card in chimeratech_cards:
        if card['edopro_id'] and card['edopro_id'] not in seen_ids:
            download_card_image(card['edopro_id'], images_dir)
            seen_ids.add(card['edopro_id'])
    
    # Generate HTML deck display
    chimeratech_output = "/home/fidika/yugioh-rush/chimeratech_cyber_deck.html"
    create_simple_html_deck("Chimeratech Cyber Deck", chimeratech_cards, card_database, images_dir, chimeratech_output)
    
    # Process Harpie Lady Sisters deck
    print("\n" + "="*50)
    print("Processing Harpie Lady Sisters deck...")
    print("="*50)
    harpie_file = "/home/fidika/yugioh-rush/structure-decks-txt/harpie_lady_sisters_deck_cards.txt"
    harpie_cards = parse_deck_file(harpie_file)
    print(f"Found {len(harpie_cards)} cards in Harpie Lady Sisters deck")
    
    # Download images for Harpie cards
    print("Downloading card images...")
    seen_ids = set()
    for card in harpie_cards:
        if card['edopro_id'] and card['edopro_id'] not in seen_ids:
            download_card_image(card['edopro_id'], images_dir)
            seen_ids.add(card['edopro_id'])
    
    # Generate HTML deck display
    harpie_output = "/home/fidika/yugioh-rush/harpie_lady_sisters_deck.html"
    create_simple_html_deck("Harpie Lady Sisters Deck", harpie_cards, card_database, images_dir, harpie_output)
    
    print(f"\n🎉 Successfully generated deck displays!")
    print(f"Generated files:")
    print(f"- {chimeratech_output}")
    print(f"- {harpie_output}")
    print(f"- Downloaded images in: {images_dir}")
    print(f"\nOpen the HTML files in a web browser to view the complete decks with images!")

if __name__ == "__main__":
    main()