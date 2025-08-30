import csv
import re
import os

# Mapping of abbreviated show names to full show names
SHOW_MAPPING = {
    "B99": "Brooklyn Nine-Nine",
    "HIMYM": "How I Met Your Mother",
    "P&R": "Parks and Recreation",
    "KOTH": "King of the Hill",
    "TGP": "The Good Place",
    "Office": "The Office",
    "NHIE": "Never Have I Ever",
    "Last Man": "Last Man on Earth",
    "Simpsons": "The Simpsons",
    "Curb": "Curb Your Enthusiasm",
    "Veep": "Veep",
    "Family Guy": "Family Guy",
    "Silicon V.": "Silicon Valley",
    "Community": "Community",
    "Modern Family": "Modern Family",
    "Bless Harts": "Bless the Harts",
    "Futurama": "Futurama",
    "Arrested Dev.": "Arrested Development",
    "Eastbound": "Eastbound & Down",
    "Fresh Off Boat": "Fresh Off the Boat",
    "Bob's Burgers": "Bob's Burgers",
    "League": "The League",
    "Broad City": "Broad City",
    "Mindy Proj.": "The Mindy Project",
    "Kimmy Schmidt": "Unbreakable Kimmy Schmidt",
    "Bear": "The Bear",
    "Master of N.": "Master of None",
    "What We Do Shadows": "What We Do in the Shadows",
    "Ted Lasso": "Ted Lasso",
    "Rick & Morty": "Rick and Morty",
    "Workaholics": "Workaholics",
    "Goldbergs": "The Goldbergs",
    "Raymond": "Everybody Loves Raymond",
    "South Park": "South Park",
    "New Girl": "New Girl",
    "Da Ali G Show": "Da Ali G Show",
    "American Dad": "American Dad!",
    "Key & Peele": "Key & Peele",
    "Hacks": "Hacks",
    "Portlandia": "Portlandia",
    "30 Rock": "30 Rock",
    "Inside Amy Schumer": "Inside Amy Schumer",
    "Black-ish": "Black-ish",
    "Life in Pieces": "Life in Pieces",
    "Girls": "Girls",
    "Single Parents": "Single Parents",
    "Superstore": "Superstore",
    "Crazy Ex-GF": "Crazy Ex-Girlfriend",
    "Dead to Me": "Dead to Me",
    "Last OG": "The Last O.G.",
    "Central Park": "Central Park",
    "Insecure": "Insecure",
    "Neighborhood": "The Neighborhood",
    "Mike & Molly": "Mike & Molly",
    "PEN15": "PEN15",
    "Tacoma FD": "Tacoma FD",
    "F Is for Family": "F Is for Family",
    "iZombie": "iZombie",
    "Big Mouth": "Big Mouth",
    "Wilfred": "Wilfred",
    "Fuller House": "Fuller House",
    "Kroll Show": "Kroll Show",
    "Lodge 49": "Lodge 49",
    "Mozart Jungle": "Mozart in the Jungle",
    "Saved Bell": "Saved by the Bell (2020)",
    "Space Force": "Space Force",
    "Miracle Workers": "Miracle Workers",
    "The Other Two": "The Other Two",
    "Search Party": "Search Party",
    "Playing House": "Playing House",
    "Raising Hope": "Raising Hope",
    "Carmichael Show": "The Carmichael Show",
    "Grinder": "The Grinder",
    "Muppets": "The Muppets (2015)",
    "Childrens Hospital": "Childrens Hospital",
    "Russian Doll": "Russian Doll",
    "Loot": "Loot",
    "Maron": "Maron",
    "Great News": "Great News",
    "Champions": "Champions",
    "Nathan For You": "Nathan for You",
    "Thick of It": "The Thick of It",
    "Corner Gas": "Corner Gas",
    "Wet Hot Am. Summer": "Wet Hot American Summer",
    "Dickinson": "Dickinson",
    "Bupkis": "Bupkis",
    "American Auto": "American Auto",
    "Drunk History": "Drunk History",
    "People of Earth": "People of Earth",
    "Little America": "Little America",
    "A.P. Bio": "A.P. Bio",
    "Upload": "Upload",
    "Rutherford Falls": "Rutherford Falls",
    "Red Oaks": "Red Oaks",
    "Sex Lives College Girls": "The Sex Lives of College Girls",
    "Angie Tribeca": "Angie Tribeca",
    "Upshaws": "The Upshaws",
    "Awkward.": "Awkward.",
}

def extract_shows_from_credits(per_show_breakdown):
    """Extract show names from a writer's per-show breakdown."""
    shows = []
    parts = per_show_breakdown.split(';')
    for part in parts:
        # Extract show name and episode count
        match = re.match(r'(.*?)\s*\(\d+\)', part.strip())
        if match:
            show_name = match.group(1).strip()
            shows.append(show_name)
    return shows

def main():
    # Check if files exist
    if not os.path.exists('comedy_writers.csv'):
        print("Error: comedy_writers.csv not found")
        return
    
    # Use the correct filename
    michelin_file = 'michelin_enriched_full - FINAL.csv'
    if not os.path.exists(michelin_file):
        print(f"Error: {michelin_file} not found")
        return
    
    # Read the michelin CSV
    michelin_shows = {}
    with open(michelin_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            show_name = row['Show']
            writers = row['Writers'] if row['Writers'] else ""
            michelin_shows[show_name] = {
                'writers': writers,
                'row': row
            }
    
    # Read the comedy writers CSV
    comedy_writers = []
    with open('comedy_writers.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            comedy_writers.append({
                'name': row['Writer Name'],
                'shows': extract_shows_from_credits(row['Per-Show Breakdown'])
            })
    
    # Track new writers added
    new_writers_added = 0
    shows_updated = set()
    
    # Update michelin shows with additional writers
    for writer in comedy_writers:
        writer_name = writer['name']
        
        for abbr_show in writer['shows']:
            # Try to match the show to a full show name
            full_show_name = SHOW_MAPPING.get(abbr_show, abbr_show)
            
            # Check if this show is in the michelin list
            for michelin_show_name, michelin_data in michelin_shows.items():
                # Check if show names match (case insensitive)
                if full_show_name.lower() == michelin_show_name.lower():
                    # Check if writer is already in the list
                    current_writers = michelin_data['writers'].split(', ') if michelin_data['writers'] else []
                    
                    # Check if writer is already listed (including partial name matches)
                    already_listed = False
                    for current_writer in current_writers:
                        if writer_name in current_writer or current_writer in writer_name:
                            already_listed = True
                            break
                    
                    # Add writer if not already listed
                    if not already_listed and writer_name:
                        if michelin_data['writers']:
                            michelin_data['writers'] += f", {writer_name}"
                        else:
                            michelin_data['writers'] = writer_name
                        
                        michelin_data['row']['Writers'] = michelin_data['writers']
                        new_writers_added += 1
                        shows_updated.add(michelin_show_name)
    
    # Write updated michelin CSV
    output_file = 'michelin_enriched_updated.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        fieldnames = list(next(iter(michelin_shows.values()))['row'].keys())
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        
        for show_data in michelin_shows.values():
            writer.writerow(show_data['row'])
    
    print(f"Update complete. Added {new_writers_added} new writers across {len(shows_updated)} shows.")
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()