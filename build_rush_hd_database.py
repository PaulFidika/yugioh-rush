#!/usr/bin/env python3
"""
Rush-HD Card Database Builder
Systematically processes Rush-HD images to create a comprehensive 
mapping between EDOPro IDs and card names.
"""
import os
import json
import csv
from pathlib import Path
import time

def get_rush_hd_files():
    """Get all PNG files from Rush-HD directory"""
    rush_hd_dir = Path("/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/Rush-HD")
    png_files = list(rush_hd_dir.glob("*.png"))
    png_files.sort()  # Sort by filename
    print(f"Found {len(png_files)} PNG files in Rush-HD directory")
    return png_files

def load_existing_database():
    """Load existing database if it exists"""
    db_file = "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/rush_hd_card_database.json"
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_database(database):
    """Save database to JSON file"""
    db_file = "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/rush_hd_card_database.json"
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    # Also save as CSV for easy searching
    csv_file = "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/rush_hd_card_database.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['EDOPro_ID', 'Card_Name', 'Card_Type', 'Level', 'ATK', 'DEF', 'Attribute', 'Race'])
        
        for edopro_id, card_data in sorted(database.items()):
            writer.writerow([
                edopro_id,
                card_data.get('name', ''),
                card_data.get('type', ''),
                card_data.get('level', ''),
                card_data.get('atk', ''),
                card_data.get('def', ''),
                card_data.get('attribute', ''),
                card_data.get('race', '')
            ])

def process_batch(files_batch, database, start_idx):
    """Process a batch of files and update database"""
    print(f"\n=== Processing batch starting at index {start_idx} ===")
    
    for i, file_path in enumerate(files_batch):
        edopro_id = file_path.stem  # Filename without extension
        
        # Skip if already processed
        if edopro_id in database:
            print(f"Skipping {edopro_id} (already processed)")
            continue
        
        print(f"Processing {edopro_id} ({start_idx + i + 1}/{start_idx + len(files_batch)})")
        
        # Create entry with placeholder data
        # In actual implementation, we would use image analysis here
        database[edopro_id] = {
            'name': 'PENDING_MANUAL_REVIEW',
            'type': 'UNKNOWN',
            'level': '',
            'atk': '',
            'def': '',
            'attribute': '',
            'race': '',
            'processed': False,
            'file_path': str(file_path)
        }
    
    return database

def main():
    print("Rush-HD Card Database Builder")
    print("=" * 40)
    
    # Load existing database
    database = load_existing_database()
    print(f"Loaded existing database with {len(database)} entries")
    
    # Get all Rush-HD files
    all_files = get_rush_hd_files()
    
    # Process in batches to make it manageable
    batch_size = 50  # Process 50 cards at a time
    
    for i in range(0, len(all_files), batch_size):
        batch = all_files[i:i+batch_size]
        database = process_batch(batch, database, i)
        
        # Save progress after each batch
        save_database(database)
        print(f"Saved progress. Database now has {len(database)} entries.")
        
        # For now, just process first batch to demonstrate
        if i == 0:
            print("\nFirst batch processed. Ready for manual card name extraction.")
            break
    
    print(f"\nDatabase building complete. Total entries: {len(database)}")
    print("Files created:")
    print("- rush_hd_card_database.json (full database)")
    print("- rush_hd_card_database.csv (searchable CSV)")

if __name__ == "__main__":
    main()