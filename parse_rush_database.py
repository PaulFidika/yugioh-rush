#!/usr/bin/env python3
"""
Parse Rush Duel Database from BabelCDB
Downloads and extracts card names from the official Rush Duel database
"""
import sqlite3
import json
import csv
import urllib.request
import os
from pathlib import Path

def download_rush_database():
    """Download the Rush Duel database from BabelCDB"""
    url = "https://raw.githubusercontent.com/ProjectIgnis/BabelCDB/master/cards-rush.cdb"
    local_file = "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/cards-rush.cdb"
    
    print("Downloading Rush Duel database from BabelCDB...")
    try:
        urllib.request.urlretrieve(url, local_file)
        print(f"Downloaded database to: {local_file}")
        return local_file
    except Exception as e:
        print(f"Error downloading database: {e}")
        return None

def parse_database(db_file):
    """Parse the SQLite database and extract card information"""
    if not os.path.exists(db_file):
        print(f"Database file not found: {db_file}")
        return None
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables found: {[table[0] for table in tables]}")
        
        # Get texts table structure
        cursor.execute("PRAGMA table_info(texts);")
        texts_columns = cursor.fetchall()
        print(f"Texts table columns: {[col[1] for col in texts_columns]}")
        
        # Get datas table structure  
        cursor.execute("PRAGMA table_info(datas);")
        datas_columns = cursor.fetchall()
        print(f"Datas table columns: {[col[1] for col in datas_columns]}")
        
        # Extract all card data
        query = """
        SELECT 
            t.id,
            t.name,
            t.desc,
            d.type,
            d.atk,
            d.def,
            d.level,
            d.race,
            d.attribute
        FROM texts t
        LEFT JOIN datas d ON t.id = d.id
        ORDER BY t.id
        """
        
        cursor.execute(query)
        cards = cursor.fetchall()
        
        print(f"Found {len(cards)} cards in database")
        
        conn.close()
        return cards
        
    except Exception as e:
        print(f"Error parsing database: {e}")
        return None

def save_card_database(cards):
    """Save extracted card data to various formats"""
    if not cards:
        print("No card data to save")
        return
    
    # Create comprehensive database structure
    database = {
        "database_info": {
            "source": "BabelCDB cards-rush.cdb",
            "extracted": "2024-07-28",
            "total_cards": len(cards),
            "description": "Complete EDOPro ID to Rush Duel card name mapping"
        },
        "cards": {}
    }
    
    # Process each card
    for card in cards:
        edopro_id, name, desc, card_type, atk, def_val, level, race, attribute = card
        
        # Convert type from integer to readable format (simplified)
        type_map = {
            1: "Monster",
            2: "Spell", 
            4: "Trap"
        }
        
        card_type_readable = "Unknown"
        if card_type:
            if card_type & 1:
                card_type_readable = "Monster"
            elif card_type & 2:
                card_type_readable = "Spell"
            elif card_type & 4:
                card_type_readable = "Trap"
        
        database["cards"][str(edopro_id)] = {
            "name": name or "Unknown",
            "description": desc or "",
            "type": card_type_readable,
            "atk": atk if atk is not None else "",
            "def": def_val if def_val is not None else "",
            "level": level if level is not None else "",
            "race": race if race is not None else "",
            "attribute": attribute if attribute is not None else ""
        }
    
    # Save as JSON
    json_file = "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/rush_duel_complete_database.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    print(f"Saved JSON database: {json_file}")
    
    # Save as CSV for easy searching
    csv_file = "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/rush_duel_complete_database.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['EDOPro_ID', 'Card_Name', 'Type', 'ATK', 'DEF', 'Level', 'Race', 'Attribute', 'Description'])
        
        for edopro_id, card_data in sorted(database["cards"].items(), key=lambda x: int(x[0])):
            writer.writerow([
                edopro_id,
                card_data['name'],
                card_data['type'],
                card_data['atk'],
                card_data['def'],
                card_data['level'],
                card_data['race'],
                card_data['attribute'],
                card_data['description'][:100] + "..." if len(card_data['description']) > 100 else card_data['description']
            ])
    print(f"Saved CSV database: {csv_file}")
    
    # Create simple lookup file
    lookup_file = "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/rush_duel_id_to_name.txt"
    with open(lookup_file, 'w', encoding='utf-8') as f:
        f.write("Rush Duel EDOPro ID to Card Name Lookup\n")
        f.write("=" * 50 + "\n\n")
        for edopro_id, card_data in sorted(database["cards"].items(), key=lambda x: int(x[0])):
            f.write(f"{edopro_id}: {card_data['name']}\n")
    print(f"Saved lookup file: {lookup_file}")

def main():
    print("Rush Duel Database Parser")
    print("=" * 30)
    
    # Download database
    db_file = download_rush_database()
    if not db_file:
        return
    
    # Parse database
    cards = parse_database(db_file)
    if not cards:
        return
    
    # Save extracted data
    save_card_database(cards)
    
    print("\nDatabase parsing complete!")
    print("Generated files:")
    print("- rush_duel_complete_database.json (full database)")
    print("- rush_duel_complete_database.csv (searchable CSV)")
    print("- rush_duel_id_to_name.txt (simple lookup)")

if __name__ == "__main__":
    main()