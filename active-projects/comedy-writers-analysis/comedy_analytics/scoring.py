from typing import List, Dict
from .models import Writer, Show

CREATOR_MULTIPLIER = 2.5

class Scorer:
    @staticmethod
    def calculate_scores(writers: List[Writer], shows: Dict[str, Show]):
        """
        Calculate scores for all writers based on their credits and the show database.
        Updates the Writer objects in-place.
        """
        for writer in writers:
            # Reset scores
            writer.writing_points = 0.0
            writer.creator_points = 0.0
            
            for credit in writer.credits:
                # Normalize title for matching
                normalized_credit_title = credit.show_title.lower().strip()
                
                # Find matching show
                matched_show = None
                
                # Direct lookup
                if normalized_credit_title in shows:
                    matched_show = shows[normalized_credit_title]
                else:
                    # Fuzzy/Substring matching (simple version)
                    for show_key, show in shows.items():
                        if (normalized_credit_title in show_key or 
                            show_key in normalized_credit_title):
                            matched_show = show
                            break
                
                if matched_show:
                    # Calculate points
                    points = matched_show.tier
                    
                    # Check if writer is also a creator (override role if needed)
                    is_creator = False
                    
                    # Check explicit role in credit
                    if credit.role == "Creator":
                        is_creator = True
                    
                    # Check against show's creator list
                    writer_name_lower = writer.name.lower()
                    for creator in matched_show.creators:
                        creator_lower = creator.lower()
                        if (creator_lower in writer_name_lower or 
                            writer_name_lower in creator_lower):
                            is_creator = True
                            break
                    
                    if is_creator:
                        writer.creator_points += points * CREATOR_MULTIPLIER
                        credit.role = "Creator" # Update role if inferred
                    else:
                        writer.writing_points += points
