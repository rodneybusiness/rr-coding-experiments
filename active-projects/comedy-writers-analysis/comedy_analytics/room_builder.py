from typing import List, Dict, Optional
from dataclasses import dataclass
import random
from .models import Writer, Show
from .enrichment import ToneVector, EnrichmentEngine

@dataclass
class RoomRequest:
    target_tone: ToneVector
    budget_tier: str = "Mid" # Low, Mid, High
    room_size: int = 8
    must_haves: List[str] = None # List of writer names

@dataclass
class RoomSlot:
    role: str
    writer: Optional[Writer] = None
    match_score: float = 0.0

class RoomBuilder:
    def __init__(self, writers: List[Writer], shows: Dict[str, Show]):
        self.writers = writers
        self.shows = shows
        self.analyzer = EnrichmentEngine()
        
        # Pre-calculate writer tones (in production this would be cached)
        self.writer_tones = {}
        for w in self.writers:
            self.writer_tones[w.name] = self.analyzer.get_writer_tone(w, self.shows)

    def build_room(self, request: RoomRequest) -> List[RoomSlot]:
        """
        Constructs a writers room based on the request with REALISTIC constraints.
        """
        room = []
        
        # 1. Define Budget Cap (Weekly/Episodic Estimate)
        budget_caps = {
            "Low": 60000,   # Indie/Basic Cable
            "Mid": 120000,  # Network/Premium Cable
            "High": 250000  # Streaming Blockbuster
        }
        total_budget = budget_caps.get(request.budget_tier, 100000)
        current_spend = 0
        
        # Define structure based on size
        structure = self._get_structure(request.room_size)
        
        # Pool of available writers (exclude already picked)
        available_writers = list(self.writers)
        
        for role in structure:
            best_candidate = None
            best_score = -1
            
            # Filter candidates by role suitability AND affordability
            candidates = self._filter_candidates_by_role(available_writers, role)
            
            # Shuffle to add variety
            random.shuffle(candidates)
            
            for candidate in candidates:
                # Estimate Quote (Salary)
                quote = self._estimate_quote(candidate, role)
                
                # Check Budget
                if current_spend + quote > total_budget:
                    continue
                
                # Calculate Fit
                w_tone = self.writer_tones.get(candidate.name)
                tone_score = self._calculate_tone_match(w_tone, request.target_tone)
                
                # Impact Score (Normalized)
                impact_score = min(candidate.total_score / 40.0, 1.0)
                
                # Composite score
                # For Showrunners, Impact matters more. For Staff Writers, Tone matters more.
                if role == "Showrunner":
                    total_score = (tone_score * 0.4) + (impact_score * 0.6)
                else:
                    total_score = (tone_score * 0.8) + (impact_score * 0.2)
                
                if total_score > best_score:
                    best_score = total_score
                    best_candidate = candidate
            
            if best_candidate:
                quote = self._estimate_quote(best_candidate, role)
                room.append(RoomSlot(role=role, writer=best_candidate, match_score=best_score))
                available_writers.remove(best_candidate)
                current_spend += quote
            else:
                # Failed to find affordable candidate
                room.append(RoomSlot(role=role, writer=None, match_score=0))
            
        return room

    def _estimate_quote(self, writer: Writer, role: str) -> int:
        """
        Estimates the weekly cost of a writer based on their score and role.
        """
        base_rates = {
            "Showrunner": 35000,
            "Co-EP": 20000,
            "Supervising Producer": 12000,
            "Producer": 9000,
            "Story Editor": 7000,
            "Staff Writer": 4500 # WGA Minimum-ish
        }
        
        base = base_rates.get(role, 5000)
        
        # Premium for high-scoring talent (The "Quote")
        premium = writer.total_score * 500
        
        return int(base + premium)

    def _filter_candidates_by_role(self, writers: List[Writer], role: str) -> List[Writer]:
        """
        Filters writers based on their likely seniority.
        Strict enforcement to ensure realistic rooms.
        """
        filtered = []
        for w in writers:
            score = w.total_score
            created_count = len(w.shows_created)
            
            if role == "Showrunner":
                # Must be a creator or very high level veteran
                if created_count > 0 or score > 25: filtered.append(w)
            elif role == "Co-EP":
                # Veteran but maybe not a creator yet, or a smaller creator
                if score > 15: filtered.append(w)
            elif role == "Supervising Producer":
                if 10 < score <= 20: filtered.append(w)
            elif role == "Producer":
                if 5 < score <= 15: filtered.append(w)
            elif role == "Story Editor":
                if 2 < score <= 8: filtered.append(w) # Mid-level
            elif role == "Staff Writer":
                # Must be junior. High scorers should NOT be staff writers.
                if score <= 5: filtered.append(w)
            
        # Fallback: If strict filtering fails, widen the net slightly
        if not filtered:
            if role == "Showrunner": return [w for w in writers if w.total_score > 15]
            if role == "Staff Writer": return [w for w in writers if w.total_score < 10]
            return writers 
        
        # Limit pool size for performance
        if len(filtered) > 100:
            return random.sample(filtered, 100)
        return filtered

    def _get_structure(self, size: int) -> List[str]:
        """Returns a list of roles for the room."""
        roles = ["Showrunner"]
        if size >= 2: roles.append("Co-EP")
        if size >= 3: roles.append("Co-EP")
        if size >= 4: roles.append("Supervising Producer")
        if size >= 5: roles.append("Producer")
        if size >= 6: roles.append("Story Editor")
        if size >= 7: roles.append("Staff Writer")
        if size >= 8: roles.append("Staff Writer")
        # Add more if needed
        while len(roles) < size:
            roles.append("Staff Writer")
        return roles

    def _calculate_tone_match(self, w_tone: ToneVector, t_tone: ToneVector) -> float:
        """
        Calculates similarity between two tone vectors (0 to 1).
        Using simple Euclidean distance inverted.
        """
        diff = 0
        diff += (w_tone.darkness - t_tone.darkness) ** 2
        diff += (w_tone.pace - t_tone.pace) ** 2
        diff += (w_tone.satire - t_tone.satire) ** 2
        diff += (w_tone.heart - t_tone.heart) ** 2
        diff += (w_tone.absurdity - t_tone.absurdity) ** 2
        
        distance = diff ** 0.5
        max_distance = (100**2 * 5) ** 0.5 # Max possible distance
        
        return 1.0 - (distance / max_distance)
