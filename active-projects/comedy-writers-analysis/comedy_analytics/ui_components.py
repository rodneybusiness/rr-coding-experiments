import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* Main Background */
        .stApp {
            background-color: #0e1117;
        }
        
        /* Cards/Containers */
        .css-1r6slb0, .css-12w0qpk {
            background-color: #1f2937;
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #374151;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #f3f4f6 !important;
            font-family: 'Inter', sans-serif;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            color: #60a5fa;
        }
        
        /* Dataframe */
        .stDataFrame {
            border: 1px solid #374151;
            border-radius: 5px;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background-color: #111827;
        }
        
        /* Custom Card Class */
        .writer-card {
            background-color: #1f2937;
            padding: 1.5rem;
            border-radius: 0.5rem;
            border: 1px solid #374151;
            margin-bottom: 1rem;
        }
        .writer-name {
            font-size: 1.25rem;
            font-weight: bold;
            color: #f3f4f6;
            margin-bottom: 0.5rem;
        }
        .writer-stats {
            color: #9ca3af;
            font-size: 0.875rem;
        }
        .tag {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }
        .tag-blue { background-color: #1e40af; color: #dbeafe; }
        .tag-purple { background-color: #5b21b6; color: #f3e8ff; }
        .tag-green { background-color: #065f46; color: #d1fae5; }
        </style>
    """, unsafe_allow_html=True)

def writer_card(writer):
    shows_written = len(writer.shows_written)
    shows_created = len(writer.shows_created)
    
    tags_html = ""
    if shows_created > 0:
        tags_html += f'<span class="tag tag-purple">Creator ({shows_created})</span>'
    if shows_written > 0:
        tags_html += f'<span class="tag tag-blue">Writer ({shows_written})</span>'
        
    # Enriched Data Tags
    if writer.key_strengths:
        for strength in writer.key_strengths:
            tags_html += f'<span class="tag tag-green">💪 {strength}</span>'
            
    bio_html = ""
    if writer.bio_summary:
        bio_html = f'<div style="margin-top: 10px; font-style: italic; color: #d1d5db;">"{writer.bio_summary}"</div>'
        
    awards_html = ""
    if writer.awards:
        awards_str = ", ".join(writer.awards)
        awards_html = f'<div style="margin-top: 5px; color: #fbbf24; font-size: 0.8em;">🏆 {awards_str}</div>'

    st.markdown(f"""
<div class="writer-card">
    <div class="writer-name">{writer.name}</div>
    <div style="margin-bottom: 10px;">{tags_html}</div>
    {bio_html}
    {awards_html}
    <div class="writer-stats" style="margin-top: 10px;">
        Total Score: <span style="color: #60a5fa; font-weight: bold;">{writer.total_score:.1f}</span>
    </div>
</div>
    """, unsafe_allow_html=True)
