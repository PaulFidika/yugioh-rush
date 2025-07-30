#!/usr/bin/env python3
"""
Targeted search for Blue-Eyes cards in Rush-HD folder
"""
import os
import json

def get_known_blue_eyes_ranges():
    """Define strategic ranges to search based on what we know"""
    return [
        # Range around first Blue-Eyes White Dragon
        (160001000, 160001050),
        # Range around second Blue-Eyes White Dragon  
        (160205000, 160205070),
        # Range around fusion dragons
        (160206000, 160206050),
        # Structure Deck ranges
        (160207000, 160207070),
        (160208000, 160208070),
        (160209000, 160209070),
        (160210000, 160210070),
        (160211000, 160211070),
        # Higher ranges that might contain newer cards
        (160450000, 160456000),
    ]

def save_candidates_for_manual_review(candidates):
    """Save list of candidate files for manual review"""
    with open('/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/blue_eyes_candidates.txt', 'w') as f:
        f.write("Blue-Eyes Card Candidates for Manual Review\n")
        f.write("=" * 50 + "\n\n")
        for candidate in candidates:
            f.write(f"{candidate}\n")
    print(f"Saved {len(candidates)} candidates for manual review")

def main():
    rush_hd_dir = "/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/Rush-HD"
    candidates = []
    
    print("Searching for Blue-Eyes card candidates...")
    
    for start, end in get_known_blue_eyes_ranges():
        print(f"Checking range {start}-{end}...")
        
        for i in range(start, end + 1):
            filename = f"{i:09d}.png"
            filepath = os.path.join(rush_hd_dir, filename)
            
            if os.path.exists(filepath):
                candidates.append(filename)
    
    print(f"Found {len(candidates)} files to check manually")
    save_candidates_for_manual_review(candidates)
    
    # Print first 10 for immediate manual checking
    print("\nFirst 10 candidates for immediate checking:")
    for candidate in candidates[:10]:
        print(f"  {candidate}")

if __name__ == "__main__":
    main()