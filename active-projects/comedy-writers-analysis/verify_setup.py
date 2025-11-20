from comedy_analytics.data_manager import DataManager
from comedy_analytics.scoring import Scorer
import networkx as nx

def verify():
    print("Verifying Comedy Writer Intelligence Platform Setup...")
    
    # 1. Test Data Loading
    try:
        dm = DataManager()
        dm.load_data()
        print(f"✅ Data Loaded: {len(dm.writers)} writers, {len(dm.shows)} shows.")
    except Exception as e:
        print(f"❌ Data Loading Failed: {e}")
        return

    # 2. Test Scoring
    try:
        Scorer.calculate_scores(dm.writers, dm.shows)
        top_writer = max(dm.writers, key=lambda w: w.total_score)
        top_creator = max(dm.writers, key=lambda w: w.creator_points)
        
        print(f"✅ Scoring Calculated.")
        print(f"   Top Overall: {top_writer.name} ({top_writer.total_score} pts)")
        print(f"   Top Creator: {top_creator.name} ({top_creator.creator_points} pts)")
    except Exception as e:
        print(f"❌ Scoring Failed: {e}")
        return

    # 3. Test Network Graph Logic
    try:
        G = nx.Graph()
        # Filter for top writers to simulate app logic
        top_writers = [w for w in dm.writers if w.total_score >= 20]
        
        for w in top_writers:
            G.add_node(w.name)
            
        for i in range(len(top_writers)):
            for j in range(i + 1, len(top_writers)):
                w1 = top_writers[i]
                w2 = top_writers[j]
                shared_shows = w1.shows_written.intersection(w2.shows_written)
                if shared_shows:
                    G.add_edge(w1.name, w2.name)
        
        print(f"✅ Network Graph Logic: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges (min score 20).")
    except Exception as e:
        print(f"❌ Network Graph Logic Failed: {e}")
        return

    print("\n🎉 Verification Complete! The system is ready.")
    print("Run 'streamlit run app.py' to launch the dashboard.")

if __name__ == "__main__":
    verify()
