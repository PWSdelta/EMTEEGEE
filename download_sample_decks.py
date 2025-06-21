#!/usr/bin/env python3
"""
Script to download sample MTGJson deck files for testing.
Downloads a few popular deck files from MTGJson's official repository.
"""

import requests
import json
from pathlib import Path

# Base URL for MTGJson deck files
MTGJSON_DECKS_BASE = "https://mtgjson.com/api/v5/decks"

# List of popular deck files to download (these are actual MTGJson deck file names)
SAMPLE_DECKS = [
    "AFR_CommanderDeck_DungeonoftheMadMage.json",
    "AFC_CommanderDeck_PlanarPortal.json", 
    "C21_CommanderDeck_QuantumQuandrix.json",
    "ZNR_CommanderDeck_SnakeRampageDeck.json",
    "CMR_CommanderDeck_EnhancedEvolution.json"
]

def download_deck_file(deck_name, output_dir):
    """Download a single deck file from MTGJson."""
    url = f"{MTGJSON_DECKS_BASE}/{deck_name}"
    output_path = output_dir / deck_name
    print(f"Downloading {deck_name}...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse and re-save to ensure proper formatting
        deck_data = response.json()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(deck_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully downloaded {deck_name}")
        return True
        
    except requests.RequestException as e:
        print(f"❌ Failed to download {deck_name}: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {deck_name}: {e}")
        return False


def main():
    """Download sample deck files and create a sample deck."""
    downloads_dir = Path("downloads/deck_files")
    downloads_dir.mkdir(parents=True, exist_ok=True)
    
    print("Downloading sample MTGJson deck files...")
    
    # Try to download real deck files
    for deck_name in SAMPLE_DECKS:
        download_deck_file(deck_name, downloads_dir)
    
    # Create a sample deck for testing
    sample_deck = {
        "data": {
            "SampleDeck": {
                "code": "SAMPLE",
                "name": "Sample Test Deck",
                "type": "commander", 
                "releaseDate": "2024-01-01",
                "mainBoard": [
                    {
                        "count": 1,
                        "name": "Lightning Bolt",
                        "uuid": "123e4567-e89b-12d3-a456-426614174000",
                        "finishes": ["nonfoil"],
                        "identifiers": {
                            "mtgjsonV4Id": "123e4567-e89b-12d3-a456-426614174000"
                        }
                    }
                ],
                "sideBoard": [],
                "commander": []
            }
        }
    }
    
    # Save sample deck
    sample_file = downloads_dir / "sample_deck.json"
    with open(sample_file, 'w') as f:
        json.dump(sample_deck, f, indent=2)
    
    print(f"Created sample deck file: {sample_file}")
    print("To get real MTGJson deck files:")
    print("1. Visit https://mtgjson.com/downloads/all-decks/")
    print("2. Download individual deck JSON files")
    print("3. Place them in downloads/deck_files/")

if __name__ == "__main__":
    main()
