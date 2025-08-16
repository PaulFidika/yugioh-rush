#!/usr/bin/env python3
"""
Direct PDF Generator for Rush Duel Structure Decks
Creates PDFs directly with 2x2 card layout for optimal printing
No HTML intermediary files - maximum card size
"""
import os
import re
import json
from pathlib import Path

# Try to import reportlab, fallback to basic PDF creation
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.lib.utils import ImageReader
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

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
            current_type = 'Extra Deck'
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

def check_image_exists(edopro_id, images_dir):
    """Check if card image exists in Rush-HD-Pictures"""
    image_path = os.path.join(images_dir, f"{edopro_id}.png")
    return os.path.exists(image_path)

def create_fallback_pdf(deck_name, cards, card_database, output_filename):
    """Create PDF without reportlab using basic text layout"""
    
    # Create a simple PostScript file and convert to PDF
    ps_content = f"""%!PS-Adobe-3.0
/Helvetica-Bold findfont 16 scalefont setfont
50 750 moveto
({deck_name}) show

/Helvetica findfont 12 scalefont setfont
"""
    
    y_pos = 720
    for i, card in enumerate(cards[:20]):  # Limit to 20 cards for simple layout
        if y_pos < 100:
            break
        ps_content += f"""
50 {y_pos} moveto
({card['name']} - ID: {card['edopro_id']}) show
"""
        y_pos -= 20
    
    ps_content += "\nshowpage\n"
    
    ps_file = output_filename.replace('.pdf', '.ps')
    with open(ps_file, 'w') as f:
        f.write(ps_content)
    
    # Try to convert PS to PDF
    result = os.system(f"ps2pdf {ps_file} {output_filename} 2>/dev/null")
    if result == 0:
        os.remove(ps_file)
        print(f"✅ Generated fallback PDF: {output_filename}")
        return True
    
    # If ps2pdf not available, just create a text file
    txt_file = output_filename.replace('.pdf', '_cards.txt')
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"{deck_name}\n{'='*50}\n\n")
        for card in cards:
            card_info = get_card_info_from_database(card['edopro_id'], card_database)
            f.write(f"{card['name']} (ID: {card['edopro_id']})\n")
            if card_info and card_info.get('atk') and card_info.get('def'):
                f.write(f"  ATK: {card_info['atk']} / DEF: {card_info['def']}\n")
            f.write(f"  Type: {card['type']}\n\n")
    
    print(f"⚠️  Created text file instead: {txt_file}")
    return False

def create_direct_pdf_with_reportlab(deck_name, cards, card_database, images_dir, output_filename):
    """Create PDF directly with reportlab using 2x2 layout organized by card sections"""
    
    if not REPORTLAB_AVAILABLE:
        return create_fallback_pdf(deck_name, cards, card_database, output_filename)
    
    # Page setup - A4 size for better printing
    page_width, page_height = A4
    
    # Minimal margins for maximum card size
    margin = 0.15 * inch
    title_space = 0.5 * inch  # More space for section headers
    
    # Calculate card dimensions for 2x2 grid - maximize card size
    available_width = page_width - 2 * margin
    available_height = page_height - 2 * margin - title_space
    
    card_gap = 0.05 * inch  # Minimal gap between cards
    card_width = available_width / 2 - card_gap / 2
    card_height = available_height / 2 - card_gap / 2
    
    # Create PDF
    c = canvas.Canvas(output_filename, pagesize=A4)
    
    # Remove duplicates and group by type
    unique_cards = []
    seen_cards = set()
    
    for card in cards:
        if card['name'] not in seen_cards:
            seen_cards.add(card['name'])
            unique_cards.append(card)
    
    # Group cards by section
    sections = {
        'Extra Deck': [],
        'Monster': [],
        'Spell': [],
        'Trap': []
    }
    
    # Map card types to sections (using proper parsing types)
    for card in unique_cards:
        card_type = card['type']
        if card_type in sections:
            sections[card_type].append(card)
        else:
            # Fallback for any unexpected types
            sections['Monster'].append(card)
    
    # Section headers and order
    section_order = ['Extra Deck', 'Monster', 'Spell', 'Trap']
    section_names = {
        'Extra Deck': 'Extra Deck - Fusion/Ritual Monsters',
        'Monster': 'Monster Cards',
        'Spell': 'Spell Cards', 
        'Trap': 'Trap Cards'
    }
    
    first_section = True
    
    # Process each section separately
    for section_type in section_order:
        section_cards = sections[section_type]
        if not section_cards:
            continue
            
        # Start new page for each section (except first)
        if not first_section:
            c.showPage()
        first_section = False
        
        print(f"  📄 {section_names[section_type]}: {len(section_cards)} cards")
        
        # Process cards in groups of 4 (2x2 per page)
        for page_start in range(0, len(section_cards), 4):
            if page_start > 0:  # New page within section
                c.showPage()
                
            page_cards = section_cards[page_start:page_start + 4]
            
            # Add section header
            c.setFont("Helvetica-Bold", 16)
            header_y = page_height - margin/2 - 5
            c.drawString(margin, header_y, section_names[section_type])
            
            # Add deck name subtitle
            c.setFont("Helvetica", 12)
            subtitle_y = header_y - 20
            c.drawString(margin, subtitle_y, f"{deck_name} - Page {page_start//4 + 1}")
            
            # Draw cards in 2x2 grid
            for i, card in enumerate(page_cards):
                row = i // 2
                col = i % 2
                
                x = margin + col * (card_width + card_gap)
                y = page_height - margin - title_space - (row + 1) * (card_height + card_gap)
                
                # Draw card image - use full card space
                image_path = os.path.join(images_dir, f"{card['edopro_id']}.png")
                if os.path.exists(image_path):
                    try:
                        if PIL_AVAILABLE:
                            # Use PIL to get image dimensions for proper scaling
                            with Image.open(image_path) as img:
                                img_width, img_height = img.size
                                aspect_ratio = img_width / img_height
                                
                                # Scale to fit within card while maintaining aspect ratio
                                if aspect_ratio > (card_width / card_height):
                                    # Image is wider - fit to width
                                    draw_width = card_width
                                    draw_height = draw_width / aspect_ratio
                                else:
                                    # Image is taller - fit to height
                                    draw_height = card_height
                                    draw_width = draw_height * aspect_ratio
                                
                                # Center the image in the card space
                                image_x = x + (card_width - draw_width) / 2
                                image_y = y + (card_height - draw_height) / 2
                                
                                c.drawImage(image_path, image_x, image_y, draw_width, draw_height)
                        else:
                            # Fallback without PIL - use full card space
                            c.drawImage(image_path, x, y, card_width, card_height)
                    except Exception as e:
                        print(f"  ⚠️  Could not load image {card['edopro_id']}: {e}")
                        # Draw minimal placeholder
                        c.setFillColorRGB(0.95, 0.95, 0.95)
                        c.rect(x, y, card_width, card_height, fill=1)
                        c.setFillColorRGB(0.5, 0.5, 0.5)
                        c.setFont("Helvetica", 12)
                        c.drawCentredString(x + card_width/2, y + card_height/2, "Image Not Available")
                else:
                    # Draw minimal placeholder for missing image
                    c.setFillColorRGB(0.95, 0.95, 0.95)
                    c.rect(x, y, card_width, card_height, fill=1)
                    c.setFillColorRGB(0.5, 0.5, 0.5)
                    c.setFont("Helvetica", 12)
                    c.drawCentredString(x + card_width/2, y + card_height/2, "Image Not Available")
    
    c.save()
    print(f"✅ Generated sectioned PDF: {output_filename}")
    return True

def main():
    print("Direct PDF Generator - 2x2 Layout for Maximum Print Size")
    print("=" * 60)
    
    # Check dependencies
    if not REPORTLAB_AVAILABLE:
        print("⚠️  reportlab not available - using fallback method")
    if not PIL_AVAILABLE:
        print("⚠️  PIL not available - image scaling may be suboptimal")
    
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
        available_images = sum(1 for card in cards if check_image_exists(card['edopro_id'], images_dir))
        print(f"✅ {available_images}/{len(cards)} card images available")
        
        # Generate PDF
        base_name = deck_file.replace('_cards.txt', '').replace('_deck', '')
        pdf_output = f"/home/fidika/yugioh-rush/structure-decks-pdf/{base_name}_print_ready.pdf"
        
        create_direct_pdf_with_reportlab(deck_display_name, cards, card_database, images_dir, pdf_output)
    
    print(f"\n🎉 Generated print-ready PDFs with 2x2 layout!")
    print("Files optimized for maximum card size when printing")

if __name__ == "__main__":
    main()