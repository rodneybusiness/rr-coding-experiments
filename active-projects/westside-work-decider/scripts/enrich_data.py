#!/usr/bin/env python3
"""
Enrich spots data with operating hours, WiFi quality, and noise levels.
"""

import json
from pathlib import Path

# Operating hours templates based on place type and OpenLate flag
HOURS_TEMPLATES = {
    "coffee_shop_standard": {
        1: {"open": "06:00", "close": "18:00"},
        2: {"open": "06:00", "close": "18:00"},
        3: {"open": "06:00", "close": "18:00"},
        4: {"open": "06:00", "close": "18:00"},
        5: {"open": "06:00", "close": "18:00"},
        6: {"open": "07:00", "close": "18:00"},
        7: {"open": "07:00", "close": "17:00"},
    },
    "coffee_shop_late": {
        1: {"open": "06:00", "close": "21:00"},
        2: {"open": "06:00", "close": "21:00"},
        3: {"open": "06:00", "close": "21:00"},
        4: {"open": "06:00", "close": "21:00"},
        5: {"open": "06:00", "close": "22:00"},
        6: {"open": "07:00", "close": "22:00"},
        7: {"open": "07:00", "close": "20:00"},
    },
    "hotel_lobby": {
        1: {"open": "06:00", "close": "23:00"},
        2: {"open": "06:00", "close": "23:00"},
        3: {"open": "06:00", "close": "23:00"},
        4: {"open": "06:00", "close": "23:00"},
        5: {"open": "06:00", "close": "24:00"},
        6: {"open": "06:00", "close": "24:00"},
        7: {"open": "07:00", "close": "23:00"},
    },
    "coworking": {
        1: {"open": "07:00", "close": "22:00"},
        2: {"open": "07:00", "close": "22:00"},
        3: {"open": "07:00", "close": "22:00"},
        4: {"open": "07:00", "close": "22:00"},
        5: {"open": "07:00", "close": "22:00"},
        6: {"open": "08:00", "close": "20:00"},
        7: {"open": "09:00", "close": "18:00"},
    },
    "library": {
        1: {"open": "10:00", "close": "20:00"},
        2: {"open": "10:00", "close": "20:00"},
        3: {"open": "10:00", "close": "20:00"},
        4: {"open": "10:00", "close": "20:00"},
        5: {"open": "10:00", "close": "18:00"},
        6: {"open": "10:00", "close": "17:00"},
        7: None,  # Closed Sundays
    },
    "cafe": {
        1: {"open": "08:00", "close": "21:00"},
        2: {"open": "08:00", "close": "21:00"},
        3: {"open": "08:00", "close": "21:00"},
        4: {"open": "08:00", "close": "21:00"},
        5: {"open": "08:00", "close": "22:00"},
        6: {"open": "08:00", "close": "22:00"},
        7: {"open": "09:00", "close": "20:00"},
    },
    "club": {
        1: {"open": "06:00", "close": "22:00"},
        2: {"open": "06:00", "close": "22:00"},
        3: {"open": "06:00", "close": "22:00"},
        4: {"open": "06:00", "close": "22:00"},
        5: {"open": "06:00", "close": "22:00"},
        6: {"open": "07:00", "close": "21:00"},
        7: {"open": "07:00", "close": "20:00"},
    },
}

# WiFi quality based on tier and place type
def get_wifi_quality(spot):
    tier = spot.get("Tier", "").lower()
    place_type = spot.get("PlaceType", "").lower()
    notes = spot.get("CriticalFieldNotes", "").lower()

    if "strong wifi" in notes or "excellent wifi" in notes:
        return "excellent"
    if "weak wifi" in notes or "poor wifi" in notes or "spotty" in notes:
        return "poor"

    if tier == "elite":
        return "excellent"
    if "cowork" in place_type or "library" in place_type:
        return "excellent"
    if tier == "solid":
        return "good"
    return "adequate"

# Noise level based on place type and notes
def get_noise_level(spot):
    notes = spot.get("CriticalFieldNotes", "").lower()
    place_type = spot.get("PlaceType", "").lower()
    attributes = spot.get("Attributes", "").lower()

    if "quiet" in notes or "silent" in notes or "library" in place_type:
        return "quiet"
    if "noisy" in notes or "loud" in notes or "buzzy" in notes:
        return "lively"
    if "🎯 deep focus" in attributes.lower() or "deep focus" in attributes:
        return "quiet"
    if "body doubling" in attributes:
        return "moderate"
    if "hotel" in place_type or "club" in place_type:
        return "moderate"
    return "moderate"

# Get operating hours template based on spot characteristics
def get_hours_template(spot):
    place_type = spot.get("PlaceType", "").lower()
    open_late = spot.get("OpenLate", False)

    if "hotel" in place_type:
        return HOURS_TEMPLATES["hotel_lobby"]
    if "club" in place_type:
        return HOURS_TEMPLATES["club"]
    if "cowork" in place_type:
        return HOURS_TEMPLATES["coworking"]
    if "library" in place_type:
        return HOURS_TEMPLATES["library"]
    if "cafe" in place_type or "restaurant" in place_type:
        return HOURS_TEMPLATES["cafe"]

    # Default to coffee shop
    if open_late:
        return HOURS_TEMPLATES["coffee_shop_late"]
    return HOURS_TEMPLATES["coffee_shop_standard"]

def enrich_spot(spot):
    """Add operating hours, WiFi quality, and noise level to a spot."""
    enriched = spot.copy()

    # Add operating hours
    hours_template = get_hours_template(spot)
    enriched["OperatingHours"] = {
        str(day): hours for day, hours in hours_template.items() if hours is not None
    }

    # Add WiFi quality
    enriched["WifiQuality"] = get_wifi_quality(spot)

    # Add noise level
    enriched["NoiseLevel"] = get_noise_level(spot)

    return enriched

def main():
    # Read original data
    data_path = Path(__file__).parent.parent / "data" / "westside_remote_work_master_verified.json"

    with open(data_path, "r") as f:
        spots = json.load(f)

    print(f"Loaded {len(spots)} spots")

    # Enrich each spot
    enriched_spots = [enrich_spot(spot) for spot in spots]

    # Write enriched data
    with open(data_path, "w") as f:
        json.dump(enriched_spots, f, indent=2)

    print(f"Enriched {len(enriched_spots)} spots with operating hours, WiFi quality, and noise level")

    # Print sample
    print("\nSample enriched spot:")
    print(json.dumps(enriched_spots[0], indent=2))

if __name__ == "__main__":
    main()
