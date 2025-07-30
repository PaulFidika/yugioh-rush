#!/usr/bin/env python3
"""
Comprehensive Rush-HD Card Database Builder
Systematically processes all Rush-HD images to create complete EDOPro ID to card name mapping
"""
import os
import json
import csv
from pathlib import Path

def get_all_rush_hd_files():
    """Get sorted list of all PNG files in Rush-HD directory"""
    rush_hd_dir = Path("/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/Rush-HD")
    png_files = sorted(list(rush_hd_dir.glob("*.png")))
    return png_files

def load_existing_database():
    """Load existing comprehensive database"""
    db_file = "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/comprehensive_rush_database.json"
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "database_info": {
            "created": "2024-07-28",
            "description": "Comprehensive EDOPro ID to Card Name mapping for all Rush-HD images",
            "total_files": 0,
            "processed_cards": 0,
            "last_batch_processed": 0,
            "last_updated": "2024-07-28"
        },
        "cards": {}
    }

def save_database(database):
    """Save database in multiple formats"""
    # Save as JSON
    json_file = "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/comprehensive_rush_database.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    # Save as CSV for easy searching
    csv_file = "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/comprehensive_rush_database.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['EDOPro_ID', 'Card_Name', 'Type', 'Level', 'ATK', 'DEF', 'Attribute', 'Subtype'])
        
        for edopro_id, card_data in sorted(database["cards"].items()):
            if card_data.get('processed', False):
                writer.writerow([
                    edopro_id,
                    card_data.get('name', ''),
                    card_data.get('type', ''),
                    card_data.get('level', ''),
                    card_data.get('atk', ''),
                    card_data.get('def', ''),
                    card_data.get('attribute', ''),
                    card_data.get('subtype', '')
                ])
    
    # Create simple name lookup file
    lookup_file = "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/card_name_lookup.txt"
    with open(lookup_file, 'w', encoding='utf-8') as f:
        f.write("EDOPro ID to Card Name Quick Lookup\n")
        f.write("=" * 50 + "\n\n")
        for edopro_id, card_data in sorted(database["cards"].items()):
            if card_data.get('processed', False):
                name = card_data.get('name', 'UNKNOWN')
                f.write(f"{edopro_id}: {name}\n")

def create_batch_for_processing(all_files, batch_size=25, start_from=0):
    """Create a batch of files to process"""
    return all_files[start_from:start_from + batch_size]

def prepare_batch_list(files_batch):
    """Prepare a list of files for manual processing"""
    batch_file = "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/current_batch_to_process.txt"
    with open(batch_file, 'w', encoding='utf-8') as f:
        f.write("Current Batch for Manual Processing\n")
        f.write("=" * 40 + "\n\n")
        f.write("Instructions: Use Read tool on each file to extract card name\n\n")
        
        for i, file_path in enumerate(files_batch):
            edopro_id = file_path.stem
            f.write(f"{i+1}. {edopro_id} - {file_path.name}\n")
    
    return batch_file

def main():
    print("Comprehensive Rush-HD Database Builder")
    print("=" * 40)
    
    # Get all files
    all_files = get_all_rush_hd_files()
    print(f"Total PNG files found: {len(all_files)}")
    
    # Load existing database
    database = load_existing_database()
    processed_count = database["database_info"]["processed_cards"]
    last_batch = database["database_info"]["last_batch_processed"]
    
    print(f"Already processed: {processed_count} cards")
    print(f"Last batch processed: {last_batch}")
    
    # Update total files count
    database["database_info"]["total_files"] = len(all_files)
    
    # Create next batch for processing
    batch_size = 25
    start_from = last_batch * batch_size
    
    if start_from >= len(all_files):
        print("All files have been processed!")
        return
    
    files_batch = create_batch_for_processing(all_files, batch_size, start_from)
    
    print(f"\nPreparing batch {last_batch + 1}")
    print(f"Processing files {start_from + 1} to {start_from + len(files_batch)}")
    
    # Prepare batch list
    batch_file = prepare_batch_list(files_batch)
    print(f"Batch list created: {batch_file}")
    
    # Initialize placeholders for this batch
    for file_path in files_batch:
        edopro_id = file_path.stem
        if edopro_id not in database["cards"]:
            database["cards"][edopro_id] = {
                "name": "PENDING_PROCESSING",
                "type": "",
                "level": "",
                "atk": "",
                "def": "",
                "attribute": "",
                "subtype": "",
                "processed": False,
                "file_path": str(file_path)
            }
    
    # Save initial batch setup
    save_database(database)
    
    print(f"\nReady to process batch {last_batch + 1}")
    print("Use the Read tool on each file to extract card names, then update the database.")
    
    # Show first few files to process
    print("\nFirst 5 files in this batch:")
    for i, file_path in enumerate(files_batch[:5]):
        print(f"  {i+1}. {file_path.stem} - {file_path.name}")

if __name__ == "__main__":
    main()