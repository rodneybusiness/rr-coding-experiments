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
├── IMPORT_GUIDE.md             # 📖 Complete import/update guide
├── INCREMENTAL_PROCESSING_PLAN.md  # 🏗️ Technical architecture
├── requirements.txt             # Python dependencies
│
├── cogrepo_import.py           # 📥 Main import tool
├── cogrepo_update.py           # ♻️  Incremental update command
├── cogrepo_search.py           # 🔍 Keyword search tool
├── cogrepo_date_search.py      # 📅 Date-based search
├── index_builder.py            # 🔨 Build search indexes
│
├── models.py                   # 📊 Data models
├── state_manager.py            # 💾 Processing state tracking
│
├── parsers/                    # 🔧 Format parsers
│   ├── chatgpt_parser.py       # ChatGPT conversations.json
│   ├── claude_parser.py        # Claude JSON/JSONL
│   └── gemini_parser.py        # Gemini JSON/HTML
│
├── enrichment/                 # 🤖 AI enrichment pipeline
│   └── enrichment_pipeline.py  # Title, summary, tags, scoring
│
├── config/                     # ⚙️ Configuration
│   └── enrichment_config.yaml  # Enrichment settings
│
├── cogrepo-ui/                 # 🌐 Web interface
│   ├── index.html              # Web UI for browsing conversations
│   └── server.py               # Backend API server
│
└── data/                       # 📊 Processed conversation data
    ├── enriched_repository.jsonl    # Main database (all conversations)
    ├── focus_list.jsonl            # High-priority items
    ├── repository.index.meta.json  # Search index metadata
    ├── processing_state.json       # Import state tracking
    └── strategic_projects.json     # Key insights & opportunities
```

## 🚀 Quick Start Guide

### 1. **Import Your Conversations**
```bash
# Install dependencies
pip install -r requirements.txt

# Set your Anthropic API key (for AI enrichment)
export ANTHROPIC_API_KEY="your-key-here"

# Import ChatGPT conversations
python cogrepo_import.py --source chatgpt --file conversations.json --enrich

# Update with new conversations later
python cogrepo_update.py --source chatgpt --file new_export.json

# Build search indexes
python index_builder.py --rebuild
```

**📖 See [IMPORT_GUIDE.md](IMPORT_GUIDE.md) for detailed instructions on exporting from ChatGPT, Claude, and Gemini**

### 2. **Search Your Conversations (Command Line)**
```bash
# Search for topics
python cogrepo_search.py "family travel"
python cogrepo_search.py "creative projects"

# Search by date range
python cogrepo_date_search.py --start 2024-01-01 --end 2024-06-30
```

### 3. **Browse with Web Interface**
```bash
# Start the web UI
cd cogrepo-ui
python server.py

# Open browser to http://localhost:8000
# Use the web interface for visual exploration
```

### 4. **Analyze Data Files**
```bash
# View high-priority items
head data/focus_list.jsonl

# Check strategic insights
cat data/strategic_projects.json

# View processing statistics
python index_builder.py --stats
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
