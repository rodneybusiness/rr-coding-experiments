import csv
import re
from typing import Dict, List, Optional
from pathlib import Path
from .models import Show, Writer, Credit

# Mapping of abbreviated show names to full show names (Legacy support)
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

class DataManager:
    # Fallback database for known hits missing from the CSV
    FALLBACK_SHOWS = {
        "The Office": {"tier": 4.0, "creators": ["Greg Daniels", "Ricky Gervais", "Stephen Merchant"]},
        "Parks and Recreation": {"tier": 4.0, "creators": ["Greg Daniels", "Michael Schur"]},
        "Brooklyn Nine-Nine": {"tier": 3.5, "creators": ["Dan Goor", "Michael Schur"]},
        "The Simpsons": {"tier": 4.0, "creators": ["Matt Groening"]},
        "Family Guy": {"tier": 3.5, "creators": ["Seth MacFarlane"]},
        "American Dad!": {"tier": 3.0, "creators": ["Seth MacFarlane", "Mike Barker", "Matt Weitzman"]},
        "King of the Hill": {"tier": 3.5, "creators": ["Mike Judge", "Greg Daniels"]},
        "30 Rock": {"tier": 4.0, "creators": ["Tina Fey"]},
        "Community": {"tier": 3.5, "creators": ["Dan Harmon"]},
        "New Girl": {"tier": 3.0, "creators": ["Elizabeth Meriwether"]},
        "Modern Family": {"tier": 4.0, "creators": ["Christopher Lloyd", "Steven Levitan"]},
        "The Goldbergs": {"tier": 2.5, "creators": ["Adam F. Goldberg"]},
        "Fresh Off the Boat": {"tier": 2.5, "creators": ["Nahnatchka Khan"]},
        "Last Man Standing": {"tier": 2.0, "creators": ["Jack Burditt"]},
        "The Mindy Project": {"tier": 3.0, "creators": ["Mindy Kaling"]},
        "Futurama": {"tier": 3.5, "creators": ["Matt Groening"]},
        "Black-ish": {"tier": 3.0, "creators": ["Kenya Barris"]},
        "Happy Endings": {"tier": 3.0, "creators": ["David Caspe"]},
        "Scrubs": {"tier": 3.5, "creators": ["Bill Lawrence"]},
        "It's Always Sunny in Philadelphia": {"tier": 4.0, "creators": ["Rob McElhenney"]},
        "Curb Your Enthusiasm": {"tier": 4.0, "creators": ["Larry David"]},
        "Seinfeld": {"tier": 4.0, "creators": ["Larry David", "Jerry Seinfeld"]},
        "Friends": {"tier": 4.0, "creators": ["David Crane", "Marta Kauffman"]},
        "How I Met Your Mother": {"tier": 3.5, "creators": ["Carter Bays", "Craig Thomas"]},
        "The Big Bang Theory": {"tier": 3.5, "creators": ["Chuck Lorre", "Bill Prady"]},
        "Two and a Half Men": {"tier": 3.0, "creators": ["Chuck Lorre", "Lee Aronsohn"]},
        "Entourage": {"tier": 3.0, "creators": ["Doug Ellin"]},
        "Silicon Valley": {"tier": 4.0, "creators": ["Mike Judge", "John Altschuler", "Dave Krinsky"]},
        "Veep": {"tier": 4.0, "creators": ["Armando Iannucci"]},
        "Succession": {"tier": 4.0, "creators": ["Jesse Armstrong"]},
        "Key & Peele": {"tier": 4.0, "creators": ["Keegan-Michael Key", "Jordan Peele"]},
        "Crazy Ex-Girlfriend": {"tier": 3.5, "creators": ["Rachel Bloom", "Aline Brosh McKenna"]},
        "The Good Place": {"tier": 4.0, "creators": ["Michael Schur"]},
        "Broad City": {"tier": 3.5, "creators": ["Ilana Glazer", "Abbi Jacobson"]},
        "Nathan For You": {"tier": 3.5, "creators": ["Nathan Fielder"]},
        "Portlandia": {"tier": 3.5, "creators": ["Fred Armisen", "Carrie Brownstein"]},
        "Workaholics": {"tier": 3.0, "creators": ["Blake Anderson", "Adam DeVine", "Anders Holm", "Kyle Newacheck"]},
        "What We Do in the Shadows": {"tier": 4.0, "creators": ["Jemaine Clement"]},
    }

    def __init__(self, data_dir: str = "."):
        self.data_dir = Path(data_dir)
        self.shows: Dict[str, Show] = {}
        self.writers: List[Writer] = []

    def load_data(self, shows_file: str = 'michelin_enriched_updated.csv', writers_file: str = 'comedy_writers.csv'):
        """Load all data from CSVs."""
        self.load_shows(shows_file)
        self.load_writers(writers_file)
        
    def load_shows(self, filename: str):
        """Load shows from the Michelin enriched CSV."""
        path = self.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Shows file not found: {path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get('Show', '').strip()
                if not title:
                    continue
                    
                # Parse Tier
                tier_str = row.get('Tier', '0')
                tier = self._parse_tier(tier_str)
                
                # Parse Creators
                creators_str = row.get('Creators', '')
                if creators_str:
                    # Split by comma or semicolon
                    creators = [c.strip() for c in re.split(r'[;,]', creators_str)]
                else:
                    creators = []
                
                # Parse Metadata (if available from add_metadata.py)
                sub_genre = [s.strip() for s in row.get('Sub_Genre', '').split(',')] if row.get('Sub_Genre') else []
                tone_tags = [t.strip() for t in row.get('Tone_Tags', '').split(',')] if row.get('Tone_Tags') else []
                
                show = Show(
                    title=title,
                    tier=tier,
                    creators=creators,
                    sub_genre=sub_genre,
                    tone_tags=tone_tags
                )
                self.shows[title.lower()] = show
                
        # Inject Fallback Shows
        for title, data in self.FALLBACK_SHOWS.items():
            if title.lower() not in self.shows:
                self.shows[title.lower()] = Show(
                    title=title,
                    tier=data['tier'],
                    creators=data['creators'],
                    sub_genre=["Comedy"], # Default
                    tone_tags=["Classic", "Sitcom"] # Default
                )

    def load_writers(self, filename: str):
        """Load writers from the comedy writers CSV."""
        path = self.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Writers file not found: {path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('Writer Name', '').strip()
                if not name:
                    continue
                    
                writer = Writer(name=name)
                
                # Parse Credits
                credits_str = row.get('Per-Show Breakdown', '')
                writer.credits = self._parse_credits(credits_str)
                
                self.writers.append(writer)

    def _parse_tier(self, tier_string: str) -> float:
        """Count stars or parse number from tier string."""
        if not tier_string:
            return 0.0
        
        # Count stars
        star_count = tier_string.count('★')
        if star_count > 0:
            return float(star_count)
            
        # Try parsing number
        try:
            match = re.search(r'(\d+)[\s-]*[Ss]tar', tier_string)
            if match:
                return float(match.group(1))
            return float(tier_string.strip())
        except (ValueError, AttributeError):
            return 0.0

    def _parse_credits(self, credits_str: str) -> List[Credit]:
        """Parse the 'Show (Count)' format."""
        credits = []
        if not credits_str:
            return credits
            
        parts = credits_str.split(';')
        for part in parts:
            match = re.match(r'(.*?)\s*\((\d+)\)', part.strip())
            if match:
                show_abbr = match.group(1).strip()
                count = int(match.group(2))
                
                # Map abbreviation to full name
                full_title = SHOW_MAPPING.get(show_abbr, show_abbr)
                
                credits.append(Credit(
                    show_title=full_title,
                    episode_count=count
                ))
        return credits
