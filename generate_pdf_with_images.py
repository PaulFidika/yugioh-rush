#!/usr/bin/env python3
"""
Professional PDF Generator for Rush Duel Structure Decks
Creates PDFs with actual card images from Rush-HD-Pictures
"""
import os
import re
import json
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
        
        # Parse card lines
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

def get_card_info_from_database(edopro_id, card_database):
    """Get card information from the database using EDOPro ID"""
    if not card_database or not edopro_id:
        return None
    
    cards_data = card_database.get("cards", {})
    return cards_data.get(str(edopro_id), None)

def check_image_exists(edopro_id, images_dir):
    """Check if card image exists in Rush-HD-Pictures"""
    image_path = os.path.join(images_dir, f"{edopro_id}.png")
    return os.path.exists(image_path)

def create_html_with_images(deck_name, cards, card_database, images_dir, output_filename):
    """Create HTML file with card images that can be converted to PDF"""
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{deck_name}</title>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 0.5in;
        }}
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: white;
        }}
        .deck-header {{
            text-align: center;
            margin-bottom: 30px;
            page-break-after: avoid;
        }}
        .deck-title {{
            font-size: 24px;
            font-weight: bold;
            color: #1a472a;
            margin-bottom: 10px;
        }}
        .deck-subtitle {{
            font-size: 14px;
            color: #666;
        }}
        .card-section {{
            margin-bottom: 40px;
            page-break-inside: avoid;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: bold;
            color: #1a472a;
            border-bottom: 2px solid #1a472a;
            padding-bottom: 5px;
            margin-bottom: 20px;
        }}
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }}
        .card {{
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 8px;
            text-align: center;
            background: #f9f9f9;
            height: 280px;
            display: flex;
            flex-direction: column;
        }}
        .card-image {{
            width: 100%;
            height: 180px;
            object-fit: contain;
            border-radius: 4px;
            background: white;
            margin-bottom: 8px;
        }}
        .card-placeholder {{
            width: 100%;
            height: 180px;
            background: linear-gradient(135deg, #e0e0e0, #f5f5f5);
            border: 2px dashed #ccc;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #888;
            font-size: 11px;
            text-align: center;
            margin-bottom: 8px;
        }}
        .card-name {{
            font-weight: bold;
            font-size: 11px;
            color: #333;
            margin-bottom: 4px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .card-info {{
            font-size: 9px;
            color: #666;
            line-height: 1.2;
        }}
        .stats {{
            font-weight: bold;
            color: #1a472a;
        }}
        @media print {{
            .card-section {{
                page-break-inside: avoid;
            }}
            .cards-grid {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="deck-header">
        <div class="deck-title">{deck_name}</div>
        <div class="deck-subtitle">Complete Structure Deck with English Translated Cards</div>
    </div>
"""
    
    # Group cards by type
    monster_cards = []
    spell_cards = []
    trap_cards = []
    seen_cards = set()
    
    for card in cards:
        # Only add each unique card once
        if card['name'] not in seen_cards:
            seen_cards.add(card['name'])
            
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
        <div class="section-title">{section_name} ({len(card_list)} cards)</div>
        <div class="cards-grid">
"""
        
        for card in card_list:
            card_info = get_card_info_from_database(card['edopro_id'], card_database)
            image_exists = check_image_exists(card['edopro_id'], images_dir)
            
            # Create card HTML
            if image_exists:
                # Use absolute path for better PDF conversion compatibility
                image_path = f"/home/fidika/yugioh-rush/Rush-HD-Pictures/pics/{card['edopro_id']}.png"
                image_html = f'<img src="file://{image_path}" alt="{card["name"]}" class="card-image">'
            else:
                image_html = f'<div class="card-placeholder">Image<br>Not Available<br>{card["edopro_id"]}</div>'
            
            # Card stats
            stats_html = ""
            if card_info and card_info.get('type') == 'Monster':
                if card_info.get('atk') and card_info.get('def'):
                    stats_html = f'<div class="stats">ATK: {card_info.get("atk")} / DEF: {card_info.get("def")}</div>'
                if card_info.get('level'):
                    stats_html += f'<div>Level: {card_info.get("level")}</div>'
            
            html_content += f"""
            <div class="card">
                {image_html}
                <div class="card-name">{card['name']}</div>
                <div class="card-info">
                    ID: {card['edopro_id']}<br>
                    {stats_html}
                </div>
            </div>
"""
        
        html_content += """
        </div>
    </div>
"""
    
    # Summary
    total_cards = len(monster_cards + spell_cards + trap_cards)
    html_content += f"""
    <div style="margin-top: 40px; text-align: center; font-size: 12px; color: #666;">
        <strong>Deck Summary:</strong> {total_cards} Total Cards | 
        {len(monster_cards)} Monsters | {len(spell_cards)} Spells | {len(trap_cards)} Traps<br>
        Generated from Yu-Gi-Oh! Rush Duel EDOPro Database with HD Card Images
    </div>
</body>
</html>
"""
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Generated HTML: {output_filename}")
    return True

def html_to_pdf(html_file, pdf_file):
    """Convert HTML to PDF using available system tools"""
    
    # Try wkhtmltopdf first (best quality)
    if os.system("which wkhtmltopdf > /dev/null 2>&1") == 0:
        cmd = f'wkhtmltopdf --page-size A4 --margin-top 0.5in --margin-bottom 0.5in --margin-left 0.5in --margin-right 0.5in --enable-local-file-access "{html_file}" "{pdf_file}"'
        result = os.system(cmd)
        if result == 0:
            print(f"✅ Generated PDF with wkhtmltopdf: {pdf_file}")
            return True
    
    # Try chromium/chrome headless
    for browser in ['chromium-browser', 'google-chrome', 'chromium']:
        if os.system(f"which {browser} > /dev/null 2>&1") == 0:
            cmd = f'{browser} --headless --disable-gpu --print-to-pdf="{pdf_file}" --virtual-time-budget=5000 --no-pdf-header-footer "file://{os.path.abspath(html_file)}"'
            result = os.system(cmd)
            if result == 0:
                print(f"✅ Generated PDF with {browser}: {pdf_file}")
                return True
            break
    
    # Try pandoc
    if os.system("which pandoc > /dev/null 2>&1") == 0:
        cmd = f'pandoc "{html_file}" -o "{pdf_file}" --pdf-engine=wkhtmltopdf'
        result = os.system(cmd)
        if result == 0:
            print(f"✅ Generated PDF with pandoc: {pdf_file}")
            return True
    
    print(f"⚠️  Could not convert to PDF. HTML file available: {html_file}")
    return False

def main():
    print("Professional PDF Generator for Rush Duel Structure Decks")
    print("=" * 60)
    
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
    print(f"✅ Found {image_count} HD card images in Rush-HD-Pictures")
    
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
        print(f"Found {len(cards)} cards in {deck_display_name}")
        
        # Check how many images we have
        available_images = 0
        for card in cards:
            if check_image_exists(card['edopro_id'], images_dir):
                available_images += 1
        
        print(f"✅ {available_images}/{len(cards)} card images available")
        
        # Generate HTML
        base_name = deck_file.replace('_cards.txt', '').replace('_deck', '')
        html_output = f"/home/fidika/yugioh-rush/structure-decks-pdf/{base_name}_updated.html"
        pdf_output = f"/home/fidika/yugioh-rush/structure-decks-pdf/{base_name}_updated.pdf"
        
        success = create_html_with_images(deck_display_name, cards, card_database, images_dir, html_output)
        
        if success:
            # Convert to PDF
            html_to_pdf(html_output, pdf_output)
    
    print(f"\n🎉 Successfully processed all structure decks!")
    print("Generated files are in the structure-decks-pdf/ directory")

if __name__ == "__main__":
    main()