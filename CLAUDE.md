# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Yu-Gi-Oh! Rush Duel card database and PDF generation toolkit. The project focuses on:
- Parsing official Rush Duel card databases (SQLite format from BabelCDB)
- Creating comprehensive card mappings between EDOPro IDs and card names
- Generating structure deck PDFs with card images and descriptions
- Building searchable databases for Rush Duel cards

## Key Scripts and Their Purpose

### Database Scripts
- `parse_rush_database.py` - Downloads and parses the official Rush Duel database from BabelCDB (cards-rush.cdb)
- `build_comprehensive_database.py` - Processes Rush-HD card images systematically to create EDOPro ID mappings
- `build_rush_hd_database.py` - Builds database from Rush-HD PNG files (batch processing)

### PDF Generation Scripts
- `generate_deck_pdfs.py` - Main PDF generator for structure decks with 2x2 card layout
- `generate_single_deck.py` - Single deck PDF generation utility

### Search/Analysis Scripts
- `search_blue_eyes.py` - Blue-Eyes card search functionality
- `search_blue_eyes_cards.py` - Extended Blue-Eyes card analysis

## File Structure and Data Flow

### Input Data Sources
- **External**: BabelCDB SQLite database (`cards-rush.cdb`) from GitHub
- **Local Images**: 
  - `/Rush-HD/` directory (PNG files named by EDOPro ID)
  - `/Rush-Cards-Deviant-Art/` directory (JPG files with semantic names)
- **Structure Deck Lists**: `/structure-decks-txt/` (text files with card lists)

### Generated Outputs
- **Databases**: JSON and CSV formats for card lookups
- **PDFs**: `/structure-decks-pdf/` (generated deck visualizations)
- **Analysis**: `rush_duel_analysis.txt` (comprehensive status report)

## Card Data Architecture

The system uses a dual-path approach for card identification:
1. **EDOPro ID mapping** - Direct numeric IDs (e.g., `160301001.png`)
2. **Semantic name mapping** - Cleaned card names (e.g., `Blue-Eyes-White-Dragon.jpg`)

### Card Database Schema
```json
{
  "database_info": {
    "source": "BabelCDB cards-rush.cdb",
    "total_cards": 2500+,
    "description": "Complete EDOPro ID to Rush Duel card name mapping"
  },
  "cards": {
    "160001000": {
      "name": "Blue-Eyes White Dragon (Rush)",
      "type": "Monster",
      "atk": "3000",
      "def": "2500",
      "level": "8",
      "attribute": "LIGHT",
      "race": "Dragon"
    }
  }
}
```

## Development Workflow

### Running Scripts
All scripts are standalone Python 3 executables:
```bash
python3 parse_rush_database.py        # Download and parse official database
python3 generate_deck_pdfs.py         # Generate all structure deck PDFs
python3 build_comprehensive_database.py  # Process Rush-HD images in batches
```

### Dependencies
- **Core**: `sqlite3`, `json`, `csv`, `urllib.request`, `pathlib`
- **PDF Generation**: `reportlab` (PDFgen, units)
- **Image Processing**: `PIL` (Pillow)

### Path Configuration
Scripts expect Windows paths with WSL access patterns:
- Base path: `/mnt/c/Users/User/OneDrive/Shinobi/Yugioh/`
- Adjust paths in scripts for different environments

## Key Design Patterns

### Batch Processing
Large datasets (2500+ cards) are processed in configurable batches (typically 25-50 items) to maintain memory efficiency and allow progress tracking.

### Fallback Image Resolution
PDF generation uses a priority system:
1. EDOPro ID lookup in Rush-HD folder
2. Semantic name matching in Rush-Cards folder  
3. Text description fallback for missing cards

### Error Handling
Scripts include comprehensive error handling for:
- Missing image files (fallback to text descriptions)
- Network issues (database downloads)
- File path mismatches between systems

## Structure Deck Processing

The system handles structure deck cards with special processing:
- Parses card lists with format: `1. Card Name (EDOPro: ID) (3 copies)`
- Groups cards by type (Monster/Spell/Trap) for PDF layout
- Handles missing cards with predefined descriptions
- Generates 2x2 grid layouts maximizing card visibility

## Important Notes

- EDOPro IDs are the primary key for card identification
- Rush Duel format is distinct from traditional Yu-Gi-Oh! TCG
- Missing card images are replaced with formatted text descriptions
- All card names and descriptions support Unicode/UTF-8 encoding
- Database files are saved in both JSON (complete) and CSV (searchable) formats