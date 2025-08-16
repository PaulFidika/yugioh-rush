#!/usr/bin/env python3
"""
Simple PDF Generator for Rush Duel Structure Decks
Creates PDFs with card information using basic text layout
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

def get_card_info_from_database(edopro_id, card_database):
    """Get card information from the database using EDOPro ID"""
    if not card_database or not edopro_id:
        return None
    
    cards_data = card_database.get("cards", {})
    return cards_data.get(str(edopro_id), None)

def create_simple_text_pdf(deck_name, cards, card_database, output_filename):
    """Create a simple text-based PDF using basic formatting"""
    
    # Create a simple text file first, then we can convert it
    text_filename = output_filename.replace('.pdf', '.txt')
    
    with open(text_filename, 'w', encoding='utf-8') as f:
        f.write(f"{deck_name}\n")
        f.write("=" * len(deck_name) + "\n\n")
        f.write("Complete Card List with English Translated Information\n")
        f.write("Source: EDOPro Rush Duel Database\n\n")
        
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
        
        # Write sections
        for section_name, card_list in [('MONSTER CARDS', monster_cards), ('SPELL CARDS', spell_cards), ('TRAP CARDS', trap_cards)]:
            if not card_list:
                continue
            
            f.write(f"\n{section_name} ({len(card_list)} cards)\n")
            f.write("-" * (len(section_name) + 20) + "\n\n")
            
            for i, card in enumerate(card_list, 1):
                card_info = get_card_info_from_database(card['edopro_id'], card_database)
                
                f.write(f"{i}. {card['name']}\n")
                f.write(f"   EDOPro ID: {card['edopro_id']}\n")
                
                if card_info:
                    if card_info.get('type') == 'Monster':
                        if card_info.get('atk') and card_info.get('def'):
                            f.write(f"   ATK: {card_info.get('atk')} / DEF: {card_info.get('def')}\n")
                        if card_info.get('level'):
                            f.write(f"   Level: {card_info.get('level')}\n")
                        if card_info.get('attribute'):
                            f.write(f"   Attribute: {card_info.get('attribute')}\n")
                        if card_info.get('race'):
                            f.write(f"   Type: {card_info.get('race')}\n")
                    
                    if card_info.get('description'):
                        desc = card_info.get('description')
                        # Wrap description at 80 characters
                        words = desc.split()
                        lines = []
                        current_line = "   "
                        
                        for word in words:
                            if len(current_line + word) > 77:
                                lines.append(current_line)
                                current_line = "   " + word
                            else:
                                current_line += (" " + word) if current_line != "   " else word
                        
                        if current_line.strip():
                            lines.append(current_line)
                        
                        f.write("   Effect:\n")
                        for desc_line in lines[:5]:  # Limit to 5 lines
                            f.write(f"{desc_line}\n")
                        
                        if len(lines) > 5:
                            f.write("   [Description truncated...]\n")
                
                f.write("\n")
        
        # Summary
        f.write(f"\nDECK SUMMARY\n")
        f.write("=" * 50 + "\n")
        f.write(f"Total Cards: {len(monster_cards + spell_cards + trap_cards)}\n")
        f.write(f"Monster Cards: {len(monster_cards)}\n")
        f.write(f"Spell Cards: {len(spell_cards)}\n")
        f.write(f"Trap Cards: {len(trap_cards)}\n")
        f.write(f"\nGenerated from Yu-Gi-Oh! Rush Duel Database\n")
    
    print(f"✅ Generated detailed card list: {text_filename}")
    
    # Try to create a simple PDF using available system tools
    try:
        pdf_cmd = f"enscript -p - {text_filename} | ps2pdf - {output_filename}"
        os.system(f"which enscript > /dev/null && which ps2pdf > /dev/null && {pdf_cmd}")
        if os.path.exists(output_filename):
            print(f"✅ Generated PDF: {output_filename}")
            return True
    except:
        pass
    
    # Alternative: try pandoc
    try:
        os.system(f"which pandoc > /dev/null && pandoc {text_filename} -o {output_filename}")
        if os.path.exists(output_filename):
            print(f"✅ Generated PDF with pandoc: {output_filename}")
            return True
    except:
        pass
    
    print(f"⚠️  Could not generate PDF, but text file created: {text_filename}")
    return False

def main():
    print("Simple PDF Generator for Rush Duel Structure Decks")
    print("=" * 60)
    
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
    
    chimeratech_output = "/home/fidika/yugioh-rush/structure-decks-pdf/chimeratech_cyber_deck_updated.pdf"
    create_simple_text_pdf("Yu-Gi-Oh! Rush Duel Structure Deck: Chimeratech Cyber", 
                          chimeratech_cards, card_database, chimeratech_output)
    
    # Process Harpie Lady Sisters deck
    print("\n" + "="*50)
    print("Processing Harpie Lady Sisters deck...")
    print("="*50)
    harpie_file = "/home/fidika/yugioh-rush/structure-decks-txt/harpie_lady_sisters_deck_cards.txt"
    harpie_cards = parse_deck_file(harpie_file)
    print(f"Found {len(harpie_cards)} cards in Harpie Lady Sisters deck")
    
    harpie_output = "/home/fidika/yugioh-rush/structure-decks-pdf/harpie_lady_sisters_deck_updated.pdf"
    create_simple_text_pdf("Yu-Gi-Oh! Rush Duel Structure Deck: Harpie Lady Sisters", 
                          harpie_cards, card_database, harpie_output)
    
    print(f"\n🎉 Successfully processed both structure decks!")
    print(f"Check the structure-decks-pdf/ directory for the generated files.")

if __name__ == "__main__":
    main()