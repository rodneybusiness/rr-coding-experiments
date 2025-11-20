from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set

@dataclass
class Show:
    title: str
    tier: float = 0.0
    creators: List[str] = field(default_factory=list)
    primary_genre: str = ""
    sub_genre: List[str] = field(default_factory=list)
    format: str = ""
    tone_tags: List[str] = field(default_factory=list)
    
    # 10X Enrichment Fields
    plot_summary: str = ""
    key_themes: List[str] = field(default_factory=list)
    cultural_impact_score: float = 0.0 # 0-100
    
    @property
    def normalized_title(self) -> str:
        return self.title.lower().strip()

@dataclass
class Credit:
    show_title: str
    role: str = "Writer" # Writer, Creator, etc.
    episode_count: int = 0
    year: Optional[int] = None

@dataclass
class Writer:
    name: str
    imdb_id: Optional[str] = None
    credits: List[Credit] = field(default_factory=list)
    reps: Dict[str, str] = field(default_factory=dict) # Agency, Manager
    
    # Scoring attributes
    writing_points: float = 0.0
    creator_points: float = 0.0
    
    # 10X Enrichment Fields
    background: List[str] = field(default_factory=list) # e.g., "Stand-up", "Improv", "Playwright"
    awards: List[str] = field(default_factory=list)
    key_strengths: List[str] = field(default_factory=list) # e.g., "Dialogue", "Structure", "Character"
    bio_summary: str = ""
    
    @property
    def total_score(self) -> float:
        return self.writing_points + self.creator_points
        
    @property
    def shows_written(self) -> Set[str]:
        return {c.show_title for c in self.credits if c.role == "Writer"}
        
    @property
    def shows_created(self) -> Set[str]:
        return {c.show_title for c in self.credits if c.role == "Creator"}
