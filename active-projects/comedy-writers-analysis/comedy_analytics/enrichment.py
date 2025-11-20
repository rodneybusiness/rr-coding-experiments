from dataclasses import dataclass
from typing import Dict, List
import random

@dataclass
class ToneVector:
    darkness: float = 0.0  # 0 (Light/Sitcom) to 100 (Grim/Dark)
    pace: float = 0.0      # 0 (Slow/Languid) to 100 (Fast/Sorkin)
    satire: float = 0.0    # 0 (Sincere) to 100 (Cynical/Satirical)
    heart: float = 0.0     # 0 (Cold) to 100 (Warm/Ted Lasso)
    absurdity: float = 0.0 # 0 (Grounded) to 100 (Surreal/I Think You Should Leave)

    def to_dict(self):
        return {
            "Darkness": self.darkness,
            "Pace": self.pace,
            "Satire": self.satire,
            "Heart": self.heart,
            "Absurdity": self.absurdity
        }

from .llm_client import LLMClient

from .llm_client import LLMClient

class EnrichmentEngine:
    def __init__(self):
        self.client = LLMClient()

    def analyze_show(self, show) -> ToneVector:
        """
        Generates a ToneVector for a given Show object.
        Uses LLM if available, otherwise falls back to heuristic/mock.
        """
        # Construct a description from available metadata
        desc = f"Genre: {', '.join(show.sub_genre)}. Tags: {', '.join(show.tone_tags)}."
        
        # Call LLM (or mock)
        scores = self.client.analyze_show_tone(show.title, desc)
        
        vector = ToneVector()
        vector.darkness = float(scores.get("Darkness", 50))
        vector.pace = float(scores.get("Pace", 50))
        vector.satire = float(scores.get("Satire", 50))
        vector.heart = float(scores.get("Heart", 50))
        vector.absurdity = float(scores.get("Absurdity", 50))

        return vector

    def enrich_show_deep(self, show):
        """
        Populates deep enrichment fields for a Show.
        """
        data = self.client.analyze_show_deep(show.title)
        show.plot_summary = data.get("Plot", "")
        show.key_themes = data.get("Themes", [])
        show.cultural_impact_score = float(data.get("Impact", 0.0))

    def enrich_writer_deep(self, writer):
        """
        Populates deep enrichment fields for a Writer.
        """
        credits = [c.show_title for c in writer.credits]
        data = self.client.analyze_writer_deep(writer.name, credits)
        writer.background = data.get("Background", [])
        writer.awards = data.get("Awards", [])
        writer.key_strengths = data.get("Strengths", [])
        writer.bio_summary = data.get("Bio", "")

    def get_writer_tone(self, writer, shows_map) -> ToneVector:
        """
        Calculates the 'Average Tone' of a writer based on their credits.
        """
        total_vector = ToneVector()
        count = 0
        
        for credit in writer.credits:
            show_title = credit.show_title.lower().strip()
            # Find show
            show = None
            if show_title in shows_map:
                show = shows_map[show_title]
            else:
                # Fuzzy match
                for k, v in shows_map.items():
                    if show_title in k or k in show_title:
                        show = v
                        break
            
            if show:
                show_vec = self.analyze_show(show)
                total_vector.darkness += show_vec.darkness
                total_vector.pace += show_vec.pace
                total_vector.satire += show_vec.satire
                total_vector.heart += show_vec.heart
                total_vector.absurdity += show_vec.absurdity
                count += 1
                
        if count > 0:
            total_vector.darkness /= count
            total_vector.pace /= count
            total_vector.satire /= count
            total_vector.heart /= count
            total_vector.absurdity /= count
            
        return total_vector
