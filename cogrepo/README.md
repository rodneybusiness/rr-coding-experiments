# CogRepo (Cognitive Repository)
**Transform Your LLM Conversations Into Searchable Knowledge**

## What This Is
A comprehensive system for capturing, processing, indexing, and searching through thousands of AI/LLM conversations. CogRepo turns ephemeral chat history into a permanent, searchable knowledge base that can be analyzed for insights, patterns, and strategic opportunities.

## The Problem It Solves
- LLM conversations contain valuable insights but disappear into history
- No way to search across months/years of AI interactions
- Can't identify patterns in your thinking or recurring topics
- Difficult to extract actionable insights from conversation history
- No way to build on previous AI-assisted work systematically

## 📁 Project Structure

```
cogrepo/
├── README.md                    # This documentation
├── requirements.txt             # Python dependencies
├── cogrepo_search.py           # 🔍 Main search tool
├── cogrepo_date_search.py      # 📅 Date-based search
├── cogrepo-ui/                 # 🌐 Web interface
│   ├── index.html              # Web UI for browsing conversations
│   ├── server.py               # Backend API server
│   └── package.json            # Node.js config for Claude Code
└── data/                       # 📊 Processed conversation data
    ├── enriched_repository.jsonl    # Main database (all conversations)
    ├── focus_list.jsonl            # High-priority items (89MB)
    ├── strategic_projects.json     # Key insights & opportunities
    ├── repository.index            # Search embeddings
    └── standardized_conversations.parquet  # Analysis-ready format
```

## 🚀 Quick Start Guide

### 1. **Search Your Conversations (Command Line)**
```bash
# Search for topics
python cogrepo_search.py "family travel"
python cogrepo_search.py "creative projects"

# Search by date range
python cogrepo_date_search.py --start 2024-01-01 --end 2024-06-30
```

### 2. **Browse with Web Interface**
```bash
# Start the web UI
cd cogrepo-ui
python server.py

# Open browser to http://localhost:8000
# Use the web interface for visual exploration
```

### 3. **Analyze Data Files**
```bash
# View high-priority items
head data/focus_list.jsonl

# Check strategic insights
cat data/strategic_projects.json

# Search raw data
grep -i "animation" data/enriched_repository.jsonl
```

## How It Works
1. Export your LLM conversations (Claude, ChatGPT, etc.)
2. Process through the enrichment pipeline
3. Search and analyze using Python scripts or web UI
4. Extract insights, patterns, and actionable intelligence

## Real-World Impact
- **Rediscover forgotten insights** from months-old conversations
- **Track evolution of ideas** across multiple sessions
- **Identify patterns** in your questions and interests
- **Build on previous work** instead of starting fresh
- **Create a personal knowledge graph** from AI interactions

## Technical Stack
- Python for processing and analysis
- JSONL for flexible data storage
- Parquet for high-performance queries
- Web-based UI for accessibility
- Semantic search capabilities

## Why This Matters
Your conversations with AI contain years of refined thinking, problem-solving, and creative exploration. CogRepo transforms this hidden goldmine into an accessible, searchable asset that grows more valuable over time.

---
*Built for anyone who believes their AI conversations are too valuable to forget*
