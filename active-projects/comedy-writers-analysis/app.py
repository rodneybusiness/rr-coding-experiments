import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from comedy_analytics.data_manager import DataManager
from comedy_analytics.scoring import Scorer
from comedy_analytics.ui_components import apply_custom_css, writer_card

st.set_page_config(page_title="Comedy Writer Intelligence", layout="wide", page_icon="🎭")
apply_custom_css()

@st.cache_data
def load_data():
    dm = DataManager()
    dm.load_data()
    Scorer.calculate_scores(dm.writers, dm.shows)
    return dm.writers, dm.shows

def build_network_graph(writers, min_score):
    G = nx.Graph()
    top_writers = [w for w in writers if w.total_score >= min_score]
    
    for w in top_writers:
        G.add_node(w.name, score=w.total_score)
        
    for i in range(len(top_writers)):
        for j in range(i + 1, len(top_writers)):
            w1 = top_writers[i]
            w2 = top_writers[j]
            shared_shows = w1.shows_written.intersection(w2.shows_written)
            if shared_shows:
                G.add_edge(w1.name, w2.name, weight=len(shared_shows), shows=list(shared_shows))
    return G

def plot_network(G):
    if G.number_of_nodes() == 0:
        return None
        
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        score = G.nodes[node]['score']
        node_text.append(f"{node}<br>Score: {score:.1f}")
        node_color.append(score)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            showscale=True,
            colorscale='Viridis',
            reversescale=True,
            color=node_color,
            size=20,
            colorbar=dict(
                thickness=15,
                title='Total Score',
                xanchor='left'
            ),
            line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title=dict(text='Writer Network Connections', font=dict(size=16)),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
    return fig

def main():
    st.title("🎭 Comedy Writer Intelligence")
    
    try:
        writers, shows = load_data()
    except FileNotFoundError as e:
        st.error(f"Data files not found: {e}")
        return

    # Initialize enrichment engine early (used in sidebar)
    from comedy_analytics.enrichment import EnrichmentEngine
    enrichment_engine = EnrichmentEngine()

    # --- Sidebar ---
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # LLM Status
        from comedy_analytics.llm_client import LLMClient
        llm_client = LLMClient()
        if llm_client.openai_client or llm_client.anthropic_client:
            st.success("🟢 LLM Connected (AI Powered)")
        else:
            st.warning("🟡 LLM Disconnected (Using Heuristics)")
            
        st.info("🌍 Database: Global & Modern (Expanded)")
        
        if st.button("🔄 Reload Data"):
            st.cache_data.clear()
            st.rerun()
            
        st.divider()
        
        if st.button("✨ Enrich Top 50 (AI)"):
            with st.spinner("Enriching Top 50 Writers... this may take a moment"):
                # Get top 50
                top_50 = sorted(writers, key=lambda x: x.total_score, reverse=True)[:50]
                progress_bar = st.progress(0)
                for idx, w in enumerate(top_50):
                    enrichment_engine.enrich_writer_deep(w)
                    progress_bar.progress((idx + 1) / 50)
                st.success("Enrichment Complete!")
                st.rerun()
        
        st.divider() # Keep the divider from original code
        st.header("Filters") # Re-add the Filters header
        min_score = st.slider("Minimum Score", 0, 100, 10)
        st.divider()
        st.info(f"Loaded {len(writers)} writers and {len(shows)} shows.")

    # --- Tabs ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Leaderboard", "🕸️ Network Graph", "🏗️ Room Builder (Alpha)", "🕴️ The Power Brokers", "📊 Statistics"])

    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Top Talent")
            
            # Pagination / Limit
            limit = st.slider("Show Top N Writers", 10, 100, 50)

            top_writers = sorted([w for w in writers if w.total_score >= min_score], 
                               key=lambda x: x.total_score, reverse=True)
            
            if not top_writers:
                st.warning("No writers found matching criteria.")
            
            for i, writer in enumerate(top_writers[:limit]):
                writer_card(writer)
                
                # Enrichment Button
                col_e1, col_e2 = st.columns([1, 4])
                with col_e1:
                    if not writer.bio_summary: # Only show if not enriched
                        if st.button(f"✨ Enrich", key=f"enrich_{i}"):
                            with st.spinner(f"Analyzing {writer.name}..."):
                                enrichment_engine.enrich_writer_deep(writer)
                                st.rerun()
                
        with col2:
            st.subheader("Quick View")
            # Simplified dataframe for quick scanning
            data = [{
                "Name": w.name, 
                "Score": w.total_score,
                "Creator Pts": w.creator_points
            } for w in top_writers]
            st.dataframe(pd.DataFrame(data), hide_index=True, use_container_width=True)

    with tab2:
        st.subheader("Comedy Cliques")
        graph_min_score = st.slider("Minimum Score for Graph", 0, 100, 20, key="graph_slider")
        
        with st.spinner("Building Network Graph..."):
            G = build_network_graph(writers, graph_min_score)
            fig = plot_network(G)
            
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"Showing connections between {G.number_of_nodes()} writers.")
            else:
                st.warning("No connections found at this threshold.")

    with tab3:
        st.subheader("🏗️ The Showrunner's Engine")
        st.markdown("Define your show's creative DNA and let the engine build your perfect room.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Creative Mandate")
            target_darkness = st.slider("Darkness (Light vs Grim)", 0, 100, 30)
            target_pace = st.slider("Pace (Slow vs Sorkin)", 0, 100, 50)
            target_satire = st.slider("Satire (Sincere vs Cynical)", 0, 100, 30)
            target_heart = st.slider("Heart (Cold vs Warm)", 0, 100, 50)
            target_absurdity = st.slider("Absurdity (Grounded vs Surreal)", 0, 100, 20)
            
        with col2:
            st.markdown("#### Logistics")
            room_size = st.number_input("Room Size", min_value=3, max_value=15, value=8)
            budget_tier = st.select_slider("Budget Tier", options=["Low", "Mid", "High"], value="Mid")
            
        if st.button("🚀 Build My Room", type="primary"):
            from comedy_analytics.enrichment import ToneVector
            from comedy_analytics.room_builder import RoomBuilder, RoomRequest
            
            target_tone = ToneVector(
                darkness=target_darkness,
                pace=target_pace,
                satire=target_satire,
                heart=target_heart,
                absurdity=target_absurdity
            )
            
            request = RoomRequest(target_tone=target_tone, room_size=room_size, budget_tier=budget_tier)
            builder = RoomBuilder(writers, shows)
            
            with st.spinner("Analyzing 1000+ writers... Calculating tone vectors... Optimizing chemistry..."):
                room = builder.build_room(request)
                
            st.success("✅ Room Assembled!")
            
            for slot in room:
                if slot.writer:
                    st.markdown(f"""
                    <div style="background-color: #1f2937; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 5px solid #60a5fa;">
                        <div style="font-weight: bold; color: #9ca3af; font-size: 0.8em;">{slot.role.upper()}</div>
                        <div style="font-size: 1.2em; color: white;">{slot.writer.name}</div>
                        <div style="font-size: 0.9em; color: #6b7280;">Match Score: {slot.match_score*100:.0f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                     st.warning(f"Could not fill role: {slot.role}")

    with tab4:
        st.subheader("🕴️ The Power Brokers")
        st.markdown("Visualize the hidden hierarchy. Who really controls the talent?")
        
        from comedy_analytics.reps_manager import RepsManager
        reps_manager = RepsManager(writers)
        reps_manager.load_or_simulate_data()
        
        # Build Agency Graph
        G_agency = nx.Graph()
        
        # Filter for top talent to keep graph readable
        pb_min_score = st.slider("Minimum Writer Score", 0, 50, 15, key="pb_slider")
        top_talent = [w for w in writers if w.total_score >= pb_min_score]
        
        for w in top_talent:
            agency = reps_manager.get_agency(w.name)
            if agency != "Unrepresented":
                # Add Agency Node (Hub)
                G_agency.add_node(agency, type="agency", score=50) # Big size
                # Add Writer Node
                G_agency.add_node(w.name, type="writer", score=w.total_score)
                # Add Edge
                G_agency.add_edge(agency, w.name)
        
        # Plotting Logic (Custom for this graph)
        if G_agency.number_of_nodes() > 0:
            pos = nx.spring_layout(G_agency, k=0.3, iterations=50)
            
            edge_x = []
            edge_y = []
            for edge in G_agency.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#444'),
                hoverinfo='none',
                mode='lines')

            node_x = []
            node_y = []
            node_text = []
            node_color = []
            node_size = []
            
            for node in G_agency.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                node_type = G_agency.nodes[node]['type']
                if node_type == "agency":
                    node_size.append(40)
                    node_color.append(100) # Brightest
                    node_text.append(f"🏢 {node}")
                else:
                    score = G_agency.nodes[node]['score']
                    node_size.append(10 + score) # Size by score
                    node_color.append(score)
                    node_text.append(f"👤 {node}")

            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                textposition="top center",
                hoverinfo='text',
                text=node_text,
                marker=dict(
                    showscale=True,
                    colorscale='Plasma',
                    color=node_color,
                    size=node_size,
                    line_width=2))
                    
            fig_agency = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title=dict(text='The Agency Ecosystem', font=dict(size=16)),
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20,l=5,r=5,t=40),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )
            st.plotly_chart(fig_agency, use_container_width=True)
        else:
            st.warning("No data to visualize.")

    with tab5:
        st.subheader("Platform Stats")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Writers", len(writers))
        col2.metric("Total Shows", len(shows))
        if writers:
            top_score = max(w.total_score for w in writers)
            col3.metric("Highest Score", f"{top_score:.1f}")

if __name__ == "__main__":
    main()
