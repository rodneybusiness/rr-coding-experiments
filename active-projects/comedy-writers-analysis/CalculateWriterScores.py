import csv
import os
import re

# Constants
CREATOR_MULTIPLIER = 2.5

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
    "Killing It": "Killing It",
    "Avenue 5": "Avenue 5",
    "Jury Duty": "Jury Duty",
    "Wrecked": "Wrecked",
    "Sunnyside": "Sunnyside"
}

def extract_shows_from_credits(per_show_breakdown):
    """Extract show names from a writer's per-show breakdown."""
    shows = []
    if not per_show_breakdown:
        return shows
        
    parts = per_show_breakdown.split(';')
    for part in parts:
        # Extract show name and episode count
        match = re.match(r'(.*?)\s*\(\d+\)', part.strip())
        if match:
            show_name = match.group(1).strip()
            shows.append(show_name)
    return shows

def count_stars(tier_string):
    """Count the number of stars in a tier string."""
    if not tier_string or not isinstance(tier_string, str):
        return 0
    # Count actual star characters
    star_count = tier_string.count('★')
    if star_count > 0:
        return star_count
    # If no star characters, try to extract a number
    try:
        # Look for patterns like "5-Star" or just "5"
        match = re.search(r'(\d+)[\s-]*[Ss]tar', tier_string)
        if match:
            return int(match.group(1))
        # Try to interpret the string as a number
        return int(tier_string.strip())
    except (ValueError, AttributeError):
        # If all else fails, return 0
        return 0

def main():
    michelin_file = 'michelin_enriched_updated.csv'
    writers_file = 'comedy_writers.csv'
    
    if not os.path.exists(michelin_file):
        print(f"Error: {michelin_file} not found")
        return
        
    if not os.path.exists(writers_file):
        print(f"Error: {writers_file} not found")
        return
    
    try:
        # Load show data from CSV
        print(f"Loading show data from {michelin_file}...")
        show_data = {}
        
        with open(michelin_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Check if required columns exist
            first_row = next(reader, None)
            if not first_row:
                print("Error: CSV file is empty")
                return
                
            if 'Show' not in first_row or 'Tier' not in first_row or 'Creators' not in first_row:
                print(f"Error: Missing required columns in CSV file")
                print(f"Available columns: {', '.join(first_row.keys())}")
                return
                
            # Reset file position
            file.seek(0)
            next(reader)  # Skip header
            
            for row in reader:
                show_name = row['Show']
                # Handle the tier - count stars or convert from numeric value
                tier = count_stars(row['Tier'])
                
                # Process creators
                creators = []
                if row['Creators']:
                    creators = row['Creators'].split(', ')
                
                show_data[show_name.lower()] = {
                    'tier': tier,
                    'creators': [c.lower() for c in creators]
                }
        
        # Initialize writer scores
        writer_scores = {}
        
        # Process writers file
        print(f"Processing writers from {writers_file}...")
        try:
            with open(writers_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    writer_name = row['Writer Name']
                    writer_lower = writer_name.lower()
                    
                    if writer_lower not in writer_scores:
                        writer_scores[writer_lower] = {
                            'name': writer_name,
                            'writing_points': 0,
                            'creator_points': 0,
                            'shows_written': [],
                            'shows_created': []
                        }
                    
                    # Process shows they wrote for
                    shows = extract_shows_from_credits(row['Per-Show Breakdown'])
                    
                    # Check each show against the michelin list
                    for show_abbr in shows:
                        # Try to map the abbreviated name to full name
                        show_full = SHOW_MAPPING.get(show_abbr, show_abbr)
                        
                        # Check if this show is in our michelin data
                        match_found = False
                        for michelin_show, data in show_data.items():
                            # Try different matching strategies
                            if (show_full.lower() == michelin_show or 
                                show_full.lower() in michelin_show or 
                                michelin_show in show_full.lower()):
                                
                                match_found = True
                                # Add writing points
                                tier = data['tier']
                                writer_scores[writer_lower]['writing_points'] += tier
                                if michelin_show not in writer_scores[writer_lower]['shows_written']:
                                    writer_scores[writer_lower]['shows_written'].append(michelin_show)
                                
                                # Check if they're also a creator
                                creator_match = False
                                for creator in data['creators']:
                                    if (creator in writer_lower or 
                                        writer_lower in creator or 
                                        writer_name in creator or 
                                        creator in writer_name):
                                        creator_match = True
                                        break
                                
                                if creator_match:
                                    creator_points = tier * CREATOR_MULTIPLIER
                                    writer_scores[writer_lower]['creator_points'] += creator_points
                                    if michelin_show not in writer_scores[writer_lower]['shows_created']:
                                        writer_scores[writer_lower]['shows_created'].append(michelin_show)
                        
                        if not match_found:
                            # For debugging - shows which shows weren't found
                            pass
        
        except Exception as e:
            print(f"Error processing writers file: {e}")
            return
        
        # Calculate total scores and format results
        results = []
        for writer_id, data in writer_scores.items():
            if data['writing_points'] > 0 or data['creator_points'] > 0:
                total_score = data['writing_points'] + data['creator_points']
                results.append({
                    'Writer': data['name'],
                    'Total Score': total_score,
                    'Writing Points': data['writing_points'],
                    'Creator Points': data['creator_points'],
                    'Shows Written': ', '.join(sorted(set(data['shows_written']))),
                    'Shows Created': ', '.join(sorted(set(data['shows_created'])))
                })
        
        # Sort by total score (descending)
        results = sorted(results, key=lambda x: x['Total Score'], reverse=True)
        
        # Save results to CSV
        output_file = 'writer_scores.csv'
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Writer', 'Total Score', 'Writing Points', 'Creator Points', 'Shows Written', 'Shows Created']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\nScoring complete. Top 10 writers:")
        for i, result in enumerate(results[:10], 1):
            print(f"{i}. {result['Writer']}: {result['Total Score']} points")
            print(f"   Writing: {result['Writing Points']} | Creator: {result['Creator Points']}")
            print(f"   Shows Written: {result['Shows Written']}")
            if result['Shows Created']:
                print(f"   Shows Created: {result['Shows Created']}")
            print("")
        
        print(f"\nFull results saved to {output_file}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()