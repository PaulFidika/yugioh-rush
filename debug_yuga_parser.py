#!/usr/bin/env python3
"""
Debug Yuga deck parsing specifically
"""
import re

def debug_parse_yuga_deck():
    filename = "/home/fidika/yugioh-rush/structure-decks-txt/yuga_deck_cards.txt"
    cards = []
    current_type = None
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines: {len(lines)}")
    
    for i, line in enumerate(lines):
        line = line.strip()
        print(f"Line {i}: '{line}'")
        
        # Check for section headers
        if line == 'MONSTER CARDS:':
            current_type = 'Monster'
            print(f"  -> Set type to Monster")
            continue
        elif line == 'SPELL CARDS:':
            current_type = 'Spell'
            print(f"  -> Set type to Spell")
            continue
        elif line == 'TRAP CARDS:':
            current_type = 'Trap'
            print(f"  -> Set type to Trap")
            continue
        
        # Parse card lines
        match = re.match(r'^\d+\.\s*(.+?)\s*\(EDOPro:\s*([^)]+)\)', line)
        if match and current_type:
            card_name = match.group(1).strip()
            edopro_id = match.group(2).strip()
            print(f"  -> MATCH: name='{card_name}', id='{edopro_id}', type='{current_type}'")
            
            cards.append({
                'name': card_name,
                'type': current_type,
                'edopro_id': edopro_id
            })
        elif re.match(r'^\d+\.', line):
            print(f"  -> Partial match but no type: {line}")
    
    print(f"\nFinal result: {len(cards)} cards found")
    for card in cards:
        print(f"  - {card['name']} ({card['edopro_id']}) [{card['type']}]")
    
    return cards

# Test it
debug_parse_yuga_deck()