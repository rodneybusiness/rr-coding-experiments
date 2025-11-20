import pandas as pd
import random
from typing import Dict, List, Tuple
from .models import Writer

class RepsManager:
    def __init__(self, writers: List[Writer]):
        self.writers = writers
        self.agency_map = {} # Writer Name -> Agency Name
        self.agent_map = {}  # Writer Name -> Agent Name
        
    def load_or_simulate_data(self):
        """
        Attempts to load real data, otherwise simulates a realistic Hollywood landscape.
        """
        try:
            # Try loading real data if it existed (placeholder for future)
            # df = pd.read_csv('writers_with_reps.csv')
            # ... processing ...
            raise FileNotFoundError("No rep data found")
        except FileNotFoundError:
            self._simulate_hollywood()
            
    def _simulate_hollywood(self):
        """
        Generates a realistic distribution of representation based on writer success.
        Top writers get big 3 agencies.
        """
        agencies = [
            ("CAA", 0.35),
            ("WME", 0.30),
            ("UTA", 0.20),
            ("Verve", 0.05),
            ("Gersh", 0.05),
            ("Paradigm", 0.03),
            ("Management 360", 0.02)
        ]
        
        # Agent names (Fake but realistic)
        agent_names = {
            "CAA": ["Maha Dakhil", "Bryan Lourd", "Richard Lovett", "Hylda Queally"],
            "WME": ["Ari Emanuel", "Patrick Whitesell", "Rick Rosen"],
            "UTA": ["Jay Sures", "Jeremy Zimmer", "David Kramer"],
            "Verve": ["Bill Weinstein", "Adam Levine"],
            "Gersh": ["Bob Gersh", "David DeCamillo"],
            "Paradigm": ["Sam Gores"],
            "Management 360": ["Guymon Casady"]
        }
        
        for writer in self.writers:
            # Higher score = Higher chance of Big 3
            score = writer.total_score
            
            # Determine if they have representation (most do in this list)
            has_rep = True
            if score < 2 and random.random() < 0.3:
                has_rep = False
                
            if has_rep:
                # Weighted random choice based on agency market share
                # But boost Big 3 for top talent
                if score > 10:
                    # Top talent almost exclusively Big 3
                    pool = agencies[:3]
                else:
                    pool = agencies
                    
                agency = random.choices([a[0] for a in pool], weights=[a[1] for a in pool])[0]
                self.agency_map[writer.name] = agency
                
                # Assign specific agent
                agent = random.choice(agent_names[agency])
                self.agent_map[writer.name] = agent

    def get_agency(self, writer_name: str) -> str:
        return self.agency_map.get(writer_name, "Unrepresented")

    def get_agent(self, writer_name: str) -> str:
        return self.agent_map.get(writer_name, "Unknown")
