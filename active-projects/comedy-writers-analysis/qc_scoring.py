from comedy_analytics.data_manager import DataManager
from comedy_analytics.scoring import Scorer
from collections import Counter

def qc_scoring():
    print("🔍 Starting Deep QC of Scoring Logic...")
    
    dm = DataManager()
    dm.load_data()
    Scorer.calculate_scores(dm.writers, dm.shows)
    
    print(f"Loaded {len(dm.writers)} writers and {len(dm.shows)} shows.")
    
    # 1. Check for Unmatched Shows
    print("\n--- Unmatched Show Credits (Top 20) ---")
    unmatched_shows = []
    total_credits = 0
    matched_credits = 0
    
    for writer in dm.writers:
        for credit in writer.credits:
            total_credits += 1
            # Re-simulate matching logic to check
            normalized_credit = credit.show_title.lower().strip()
            matched = False
            if normalized_credit in dm.shows:
                matched = True
            else:
                for show_key in dm.shows:
                    if normalized_credit in show_key or show_key in normalized_credit:
                        matched = True
                        break
            
            if not matched:
                unmatched_shows.append(credit.show_title)
            else:
                matched_credits += 1
                
    print(f"Match Rate: {matched_credits}/{total_credits} ({matched_credits/total_credits*100:.1f}%)")
    
    common_unmatched = Counter(unmatched_shows).most_common(20)
    for show, count in common_unmatched:
        print(f"   MISSING: '{show}' ({count} occurrences)")
        
    # 2. Check for Potential Missed Creators
    print("\n--- Potential Missed Creators ---")
    # Writers with "Created by" in their credit role but 0 creator points
    missed_creators = []
    for writer in dm.writers:
        has_creator_credit = any("creat" in c.role.lower() for c in writer.credits)
        if has_creator_credit and writer.creator_points == 0:
            missed_creators.append(writer.name)
            
    if missed_creators:
        print(f"Found {len(missed_creators)} writers with 'Creator' role but 0 creator points:")
        for name in missed_creators[:10]:
            print(f"   - {name}")
    else:
        print("✅ No obvious missed creators based on role text.")

    # 3. Zero Score Audit
    zero_score_writers = [w for w in dm.writers if w.total_score == 0]
    print(f"\n--- Zero Score Audit ---")
    print(f"Writers with 0 points: {len(zero_score_writers)} ({len(zero_score_writers)/len(dm.writers)*100:.1f}%)")
    if len(zero_score_writers) > 0:
        print("Sample of zero-score writers and their credits:")
        for w in zero_score_writers[:5]:
            credits = [c.show_title for c in w.credits]
            print(f"   {w.name}: {credits}")

if __name__ == "__main__":
    qc_scoring()
