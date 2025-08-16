#!/usr/bin/env python3
"""
Debug the card parsing to see what's going wrong
"""
import re

def debug_parse_deck_file(filename):
    """Debug version of parse deck file"""
    cards = []
    current_type = None
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"File content length: {len(content)}")
    print("First 500 characters:")
    print(repr(content[:500]))
    print("\n" + "="*50)
    
    # Split by double newlines to get card blocks
    sections = content.split('\n\n')
    print(f"Number of sections: {len(sections)}")
    
    for i, section in enumerate(sections):
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        first_line = lines[0].strip()
        print(f"\nSection {i}: First line: '{first_line}'")
        print(f"Lines in section: {len(lines)}")
        
        # Check for section headers
        if first_line == 'EXTRA DECK:':
            current_type = 'Monster'
            print(f"  -> Set type to Monster (Extra Deck)")
            continue
        elif first_line == 'MONSTER CARDS:':
            current_type = 'Monster'
            print(f"  -> Set type to Monster")
            continue
        elif first_line == 'SPELL CARDS:':
            current_type = 'Spell'
            print(f"  -> Set type to Spell")
            continue
        elif first_line == 'TRAP CARDS:':
            current_type = 'Trap'
            print(f"  -> Set type to Trap")
            continue
        
        # Parse card entries - look for lines starting with numbers
        for j, line in enumerate(lines):
            line = line.strip()
            print(f"    Line {j}: '{line}'")
            # Format: "1. Card Name (EDOPro: 160301001)"
            match = re.match(r'^\d+\.\s*(.+?)\s*\(EDOPro:\s*([^)]+)\)', line)
            if match:
                card_name = match.group(1).strip()
                edopro_id = match.group(2).strip() if match.group(2) else None
                print(f"      -> MATCH: name='{card_name}', id='{edopro_id}', type='{current_type}'")
                
                # Skip if no EDOPro ID found
                if not edopro_id:
                    print(f"      -> SKIPPED: No EDOPro ID")
                    continue
                
                if current_type:
                    cards.append({
                        'name': card_name,
                        'type': current_type,
                        'edopro_id': edopro_id
                    })
                    print(f"      -> ADDED CARD")
                else:
                    print(f"      -> SKIPPED: No current type set")
            else:
                print(f"      -> No match")
    
    return cards

# Test both files
print("DEBUGGING CHIMERATECH CYBER DECK")
print("="*50)
chimeratech_cards = debug_parse_deck_file("/home/fidika/yugioh-rush/structure-decks-txt/chimeratech_cyber_deck_cards.txt")
print(f"\nFinal result: {len(chimeratech_cards)} cards found")
for card in chimeratech_cards:
    print(f"  - {card['name']} ({card['edopro_id']}) [{card['type']}]")

print("\n\nDEBUGGING HARPIE LADY SISTERS DECK")
print("="*50)
harpie_cards = debug_parse_deck_file("/home/fidika/yugioh-rush/structure-decks-txt/harpie_lady_sisters_deck_cards.txt")
print(f"\nFinal result: {len(harpie_cards)} cards found")
for card in harpie_cards:
    print(f"  - {card['name']} ({card['edopro_id']}) [{card['type']}]")