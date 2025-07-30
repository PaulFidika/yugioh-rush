#!/usr/bin/env python3
import os
import sys
from PIL import Image

def search_blue_eyes_ranges():
    """Search through specific ranges to find Blue-Eyes cards"""
    rush_hd_dir = "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/Rush-HD"
    
    # Known Blue-Eyes cards found so far
    known_blue_eyes = {
        "160001000.png": "Blue-Eyes White Dragon (LEGEND)",
        "160205001.png": "Blue-Eyes White Dragon"
    }
    
    print("Known Blue-Eyes cards:")
    for file_id, name in known_blue_eyes.items():
        print(f"  {file_id}: {name}")
    print()
    
    # Target ranges to search (focusing on ranges that might contain Structure Deck cards)
    search_ranges = [
        (160206, 160206 + 50),  # Around the second Blue-Eyes
        (160207, 160207 + 50),  # Next range
        (160208, 160208 + 50),  # Next range  
        (160209, 160209 + 50),  # Next range
        (160001, 160001 + 50),  # Around the first Blue-Eyes
        (160002, 160002 + 50),  # Next range from first
    ]
    
    blue_eyes_cards = []
    
    for start, end in search_ranges:
        print(f"Searching range {start}000-{end}999...")
        for i in range(start * 1000, end * 1000):
            filename = f"{i:09d}.png"
            filepath = os.path.join(rush_hd_dir, filename)
            
            if os.path.exists(filepath):
                # Sample every 5th file to be more efficient
                if i % 5 == 0:
                    try:
                        # Check if file can be opened (basic validation)
                        with Image.open(filepath) as img:
                            print(f"  Found: {filename}")
                            blue_eyes_cards.append(filename)
                    except Exception as e:
                        continue
    
    print(f"\nTotal files to manually check: {len(blue_eyes_cards)}")
    return blue_eyes_cards

if __name__ == "__main__":
    cards = search_blue_eyes_ranges()