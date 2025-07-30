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
            current_type = 'Monster'  # Legacy support - treat as monsters
            continue
        elif line == 'SPELL CARDS:':
            current_type = 'Spell'
            continue
        elif line == 'TRAP CARDS:':
            current_type = 'Trap'
            continue
        
        # Parse card lines with EDOPro IDs
        # Format: "1. Card Name (EDOPro: 160301001) (3 copies)"
        match = re.match(r'^\d+\.\s*(.+?)(?:\s*\(EDOPro:\s*([^)]+)\))?\s*(?:\((\d+)\s*[Cc]opies?\))?$', line)
        if match and current_type:
            card_name = match.group(1).strip()
            edopro_id = match.group(2).strip() if match.group(2) else None
            count = int(match.group(3)) if match.group(3) else 1
            
            cards.append({
                'name': card_name,
                'type': current_type,
                'count': count,
                'edopro_id': edopro_id
            })
    
    return cards

def get_card_descriptions():
    """Get descriptions for missing cards"""
    return {
        'Blue-Eyes Ultimate Dragon': 'Fusion Material: "Blue-Eyes White Dragon" + "Blue-Eyes White Dragon" + "Blue-Eyes White Dragon"\n\nThis legendary dragon is a powerful engine of destruction. Virtually invincible, very few have faced this awesome creature and lived to tell the tale.',
        
        'Absolute Lord of D.': 'Level 4 DARK Spellcaster Effect Monster\nATK 1200 DEF 1100\n\n[REQUIREMENT] During the turn this card is Normal or Special Summoned.\n[EFFECT] Excavate the top 4 cards of your Deck and reveal them. You can choose up to 1 each of a Level 8 LIGHT Dragon monster and "The Ultimate Blue-Eyed Legend" among the excavated cards and add them to the hand, also, shuffle the remaining cards back into the Deck.',
        
        'Node of Legend': 'Level 4 EARTH Dragon Effect Monster\nATK 1300 DEF 0\n\n[REQUIREMENT] During the turn this card was Normal Summoned.\n[EFFECT] Send the top card of your Deck to the Graveyard. Then, you can add 1 "The Origin Stone of Legend" or "Sanctum of Legend" from your Graveyard to your hand.',
        
        'Soul Drake': 'Level 4 DARK Dragon Effect Monster\nATK 1100 DEF 600\n\n[REQUIREMENT] During your Main Phase that you Normal Summoned or Special Summoned this card, send 2 face-up Level 4 or lower Effect Monsters from your field to the Graveyard.\n[EFFECT] Special Summon 1 Level 8 LIGHT Attribute Dragon Type monster from your Graveyard face-up to your field. Your Level 7 or lower monsters cannot attack this turn.',
        
        'The Ultimate Blue-Eyed Legend': 'Normal Spell Card\n\n[EFFECT] Fusion Summon a Level 10 or higher Dragon monster by sending up to 3 Dragon monsters from your hand or field to the GY, also, during this turn, the monster Special Summoned by this effect cannot be destroyed by your opponent\'s effects.',
        
        'Phoenix Dragoon': 'Effect Monster (Rush Duel)\n\nEffect text unknown',
        
        'Light Effigy': 'Normal Monster (Rush Duel)\n\n"If you Tribute Summon a LIGHT Normal Monster, you can treat this 1 monster as 2 Tributes."\n\nNote: Effect appears to be the same in Rush Duel format.',
        
        'The Fire Dragon': 'Normal Monster (Rush Duel)\n\nUsed as Tribute material',
        
        'Sylphidra': 'Normal Monster (Rush Duel)\nATK 1500 DEF 0 (approximate)',
        
        'Defender of Dragon Sorcerers': 'Effect Monster (Rush Duel)\n\nEffect text unknown',
        
        'Sanctum of Legend': 'Field Spell Card\n\n[REQUIREMENT] None\n[EFFECT] While this card is face-up in a Field Zone, face-up Level 8 or higher Dragon monsters gain 500 ATK and face-up Dragon Legend monsters cannot be destroyed by effects.',
        
        'Dragon\'s Inferno': 'Normal Spell Card\n\n[REQUIREMENT] You have a face-up Dragon Type monster on your field.\n[EFFECT] Destroy 1 Spell/Trap Card on your opponent\'s field.',
        
        'Treasure of Eyes of Blue': 'Normal Trap Card\n\n[REQUIREMENT] When a monster you control is destroyed by your opponent\'s attack or your opponent\'s effect.\n[EFFECT] Choose 1 Level 8 or higher LIGHT Dragon monster in your GY and Special Summon it to your field face-up, then, if you control a face-up "Blue-Eyes White Dragon", you can choose 1 card your opponent controls and destroy it.',
        
        'Blue-Eyes Bright Dragon': 'Level 8 Dragon Effect Monster\n\nThis card\'s name becomes "Blue-Eyes White Dragon" while in the hand.\n[REQUIREMENT] Send the top card of your Deck to the Graveyard.\n[EFFECT] This turn, this card\'s name becomes "Blue-Eyes White Dragon" and it gains 500 ATK. Then, if you have a face-up Legend Normal Monster on your field, you can destroy 1 face-up Level 8 or lower monster on your opponent\'s field.',
        
        'Blue-Eyes Vision Dragon': 'Level 8 Dragon Effect Monster\n\n[REQUIREMENT] Send the top card of your Deck to the Graveyard.\n[EFFECT] This turn, this card\'s name becomes "Blue-Eyes White Dragon", and if you Fusion Summon "Blue-Eyes Ultimate Dragon", this face-up card can be treated as 2 materials.'
    }

def find_image_file(card_name, image_dir, edopro_id=None):
    """Find the image file for a card"""
    
    # First, try EDOPro ID if provided (for Rush-HD folder)
    if edopro_id:
        # Check if we're using the Rush-HD folder
        if "Rush-HD" in image_dir:
            # Try with the EDOPro ID format (e.g., "160301001.png")
            edopro_filename = f"{edopro_id}.png"
            edopro_filepath = os.path.join(image_dir, edopro_filename)
            if os.path.exists(edopro_filepath):
                return edopro_filepath
    
    # Fallback to semantic name matching for Rush-Cards-Deviant-Art folder
    cleaned_name = clean_card_name(card_name)
    
    # Try exact match first
    filename = f"{cleaned_name}.jpg"
    filepath = os.path.join(image_dir, filename)
    if os.path.exists(filepath):
        return filepath
    
    # Try with 's' at the end (plurals)
    filename = f"{cleaned_name}s.jpg"
    filepath = os.path.join(image_dir, filename)
    if os.path.exists(filepath):
        return filepath
    
    # Try alt-art versions
    filename = f"{cleaned_name}-alt-art.jpg"
    filepath = os.path.join(image_dir, filename)
    if os.path.exists(filepath):
        return filepath
    
    # Manual mappings for special cases - ONLY map to correct/similar cards
    special_mappings = {
        'Windcaster-Torna': 'Windcaster-Torna.jpg',
        'Answerer-the-Demonic-Swordsman': 'Answerer-the-Demonic-Sword.jpg',
        'Twin-Edge-Dragon': 'Double-Twin-Dragon.jpg',
        # Blue-Eyes cards - map to actual Blue-Eyes images only
        'Blue-Eyes-White-Dragon': 'Blue-Eyes-White-Dragon.jpg',
        # Note: Blue-Eyes Bright Dragon and Blue-Eyes Vision Dragon are NOT mapped
        # They should appear as text descriptions with their unique effects
        # Other mappings
        'Dragorite': 'Dragolite.jpg', 
        'Dragons-Priestess': 'Dragon-s-Priestess.jpg',
        'Fire-Dragons-Heatflash': 'Fire-Dragon-s-Heatflash.jpg',
        'Wind-Spirit-s-Blessing': 'Mystical-Elf.jpg',
        # Note: Blue-Eyes Ultimate Dragon is NOT mapped - it doesn't exist in Rush Cards
    }
    
    if cleaned_name in special_mappings:
        filepath = os.path.join(image_dir, special_mappings[cleaned_name])
        if os.path.exists(filepath):
            return filepath
    
    return None

def create_pdf_page(c, card_items, page_width, page_height, card_width, card_height, margin, header_space):
    """Create a page with up to 4 card images/descriptions in a 2x2 grid"""
    gap = 0.2 * inch  # Gap between cards
    
    for i, item in enumerate(card_items):
        if i >= 4:
            break
        
        row = i // 2
        col = i % 2
        
        x = margin + col * (card_width + gap)
        y = page_height - margin - header_space - (row + 1) * card_height - row * gap
        
        if isinstance(item, dict):
            # Item is a card with name and possibly description
            card_name = item['name']
            img_path = item.get('image_path')
            description = item.get('description')
            
            if img_path and os.path.exists(img_path):
                # Draw the image
                c.drawImage(img_path, x, y, width=card_width, height=card_height, preserveAspectRatio=True)
            elif description:
                # Draw text description for missing card
                # Draw border
                c.setStrokeColorRGB(0, 0, 0)
                c.setLineWidth(2)
                c.rect(x, y, card_width, card_height)
                
                # Draw card name at top
                c.setFont("Helvetica-Bold", 14)
                text_y = y + card_height - 20
                # Wrap card name if too long
                name_lines = []
                if len(card_name) > 20:
                    words = card_name.split()
                    line = ""
                    for word in words:
                        if len(line + " " + word) <= 20:
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
                    text_y -= 16
                
                # Draw description
                c.setFont("Helvetica", 8)
                text_y -= 10
                
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
        else:
            # Legacy: item is just an image path
            if item and os.path.exists(item):
                c.drawImage(item, x, y, width=card_width, height=card_height, preserveAspectRatio=True)

def generate_deck_pdf(deck_name, cards, image_dir, output_filename):
    """Generate a PDF for a deck"""
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
    
    # Get card descriptions for missing cards
    card_descriptions = get_card_descriptions()
    
    # Group cards by type (no duplicates by card name OR image file)
    monster_cards = []
    spell_cards = []
    trap_cards = []
    seen_cards = set()
    seen_images = set()
    missing_cards = []
    
    for card in cards:
        # Only add each unique card once
        if card['name'] not in seen_cards:
            img_path = find_image_file(card['name'], image_dir, card.get('edopro_id'))
            card_item = {
                'name': card['name'],
                'image_path': img_path,
                'description': card_descriptions.get(card['name'])
            }
            
            if img_path:
                # Also check if we've already used this image file
                if img_path not in seen_images:
                    seen_cards.add(card['name'])
                    seen_images.add(img_path)
                    if card['type'] == 'Monster':
                        monster_cards.append(card_item)
                    elif card['type'] == 'Spell':
                        spell_cards.append(card_item)
                    elif card['type'] == 'Trap':
                        trap_cards.append(card_item)
                else:
                    print(f"⚠️  Skipping duplicate image: {card['name']} maps to already used {os.path.basename(img_path)}")
            elif card_item['description']:
                # Card is missing but we have a description
                seen_cards.add(card['name'])
                if card['type'] == 'Monster':
                    monster_cards.append(card_item)
                elif card['type'] == 'Spell':
                    spell_cards.append(card_item)
                elif card['type'] == 'Trap':
                    trap_cards.append(card_item)
            else:
                missing_cards.append(card['name'])
    
    # Report missing cards
    if missing_cards:
        print(f"⚠️  Could not find images for the following cards in {deck_name}:")
        for card in missing_cards:
            print(f"   - {card}")
    
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
            c.setFont("Helvetica-Bold", 24)
            c.drawString(margin, page_height - margin/2, f"{deck_name} - {card_type} Cards")
            c.setFont("Helvetica", 12)
            
            # Create the page
            create_pdf_page(c, page_cards, page_width, page_height, 
                          card_width, card_height, margin, header_space)
            
            first_page = False
    
    c.save()
    print(f"✅ Generated {output_filename}")

def main():
    rush_cards_dir = "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/Rush-Cards-Deviant-Art"
    rush_hd_dir = "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/Rush-HD"
    
    # Process Birth of Hero deck with Rush-HD images
    print("Processing Birth of Hero deck with Rush-HD images...")
    birth_of_hero_cards = parse_deck_new_format("/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/Structure-Decks/birth_of_hero_deck_cards.txt")
    generate_deck_pdf("Birth of Hero Deck", birth_of_hero_cards, rush_hd_dir, "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/Structure-Decks/birth_of_hero_deck_cards_hd.pdf")
    
    # Process Black Magic Ritual deck with Rush-HD images
    print("Processing Black Magic Ritual deck with Rush-HD images...")
    black_magic_cards = parse_deck_new_format("/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/Structure-Decks/black_magic_ritual_deck_cards.txt")
    generate_deck_pdf("Black Magic Ritual Deck", black_magic_cards, rush_hd_dir, "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/Structure-Decks/black_magic_ritual_deck_cards_hd.pdf")
    
    # Process Chimeratech Cyber deck with Rush-HD images
    print("Processing Chimeratech Cyber deck with Rush-HD images...")
    chimeratech_cards = parse_deck_new_format("/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/Structure-Decks/chimeratech_cyber_deck_cards.txt")
    generate_deck_pdf("Chimeratech Cyber Deck", chimeratech_cards, rush_hd_dir, "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/Structure-Decks/chimeratech_cyber_deck_cards_hd.pdf")
    
    # Process Harpie Lady Sisters deck with Rush-HD images
    print("Processing Harpie Lady Sisters deck with Rush-HD images...")
    harpie_cards = parse_deck_new_format("/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/Structure-Decks/harpie_lady_sisters_deck_cards.txt")
    generate_deck_pdf("Harpie Lady Sisters Deck", harpie_cards, rush_hd_dir, "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/Structure-Decks/harpie_lady_sisters_deck_cards_hd.pdf")
    
    print("\n🎉 All 7 HD PDFs generated successfully!")

if __name__ == "__main__":
    main()