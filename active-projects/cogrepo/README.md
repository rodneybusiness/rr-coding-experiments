# CogRepo (Cognitive Repository)

**Turn LLM conversations into searchable knowledge**

Import, enrich, and search conversations from ChatGPT, Claude, and Gemini. Supports incremental updates - only processes new conversations.

## Features

- **Multi-platform**: ChatGPT, Claude, Gemini parsers with automatic format detection
- **Incremental sync**: Track archives and only process new conversations
- **AI enrichment**: Generate titles, summaries, tags, and quality scores via Claude API
- **Full-text search**: SQLite FTS5 with BM25 ranking
- **Modern web UI**: Search, filter, keyboard shortcuts (⌘K), offline support
- **101 tests passing**

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Set API key for enrichment (optional)
export ANTHROPIC_API_KEY="sk-..."

# Start web server
cd cogrepo-ui && python app.py
# Open http://localhost:5000
```

## Project Structure

```
cogrepo/
├── parsers/                    # Format parsers
│   ├── chatgpt_parser.py       # ChatGPT conversations.json
│   ├── claude_parser.py        # Claude JSON/JSONL
│   └── gemini_parser.py        # Gemini JSON/HTML
│
├── core/                       # Core infrastructure
│   ├── config.py               # Configuration management
│   ├── exceptions.py           # Custom exceptions
│   └── logging_config.py       # Structured logging
│
├── enrichment/                 # AI enrichment
│   └── enrichment_pipeline.py  # Title, summary, tags, scoring
│
├── archive_registry.py         # Track archive files & cursors
├── smart_parser.py             # Auto-detect format, incremental parsing
├── search_engine.py            # FTS5 search with filters
├── cogrepo_import.py           # Import conversations
├── cogrepo_manage.py           # CLI management tool
├── quick_sync.py               # Fast incremental sync
│
├── cogrepo-ui/                 # Web interface
│   ├── app.py                  # Flask API server
│   ├── index.html              # Modern search UI
│   ├── static/css/             # Design system
│   ├── static/js/              # Modular JS (api, ui, app)
│   └── sw.js                   # Service worker (offline)
│
├── tests/                      # Test suite (101 tests)
│   ├── test_parsers.py
│   ├── test_search_engine.py
│   ├── test_integration.py
│   └── test_config.py
│
└── data/                       # Output
    ├── enriched_repository.jsonl
    └── archives/               # Registry state
```

## Usage

### Import Conversations

```bash
# Import with enrichment
python cogrepo_import.py --source chatgpt --file conversations.json --enrich

# Import without enrichment (faster)
python cogrepo_import.py --source claude --file export.json

# Auto-detect format
python cogrepo_import.py --file any_export.json
```

### Incremental Sync

```bash
# Register archive for tracking
python cogrepo_manage.py register ~/Downloads/chatgpt_export.json chatgpt

# Sync only new conversations
python quick_sync.py

# Check what's pending
python cogrepo_manage.py status
```

### Search

```bash
# CLI search
python cogrepo_search.py "machine learning"

# Date range
python cogrepo_date_search.py --start 2024-01-01 --end 2024-06-30

# Web UI (recommended)
cd cogrepo-ui && python app.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/conversations` | GET | List all (limit, source filter) |
| `/api/conversation/<id>` | GET | Single conversation |
| `/api/search` | GET | Full-text search with filters |
| `/api/stats` | GET | Repository statistics |
| `/api/tags` | GET | Tag cloud data |
| `/api/export` | POST | Export selected conversations |

## Configuration

```yaml
# config/enrichment_config.yaml
enrichment:
  batch_size: 10
  model: claude-sonnet-4-20250514

search:
  use_fts5: true
  default_limit: 50
```

## Running Tests

```bash
pytest tests/ -v
# 101 tests, ~1.5s
```

## Keyboard Shortcuts (Web UI)

| Shortcut | Action |
|----------|--------|
| ⌘K | Focus search |
| ⌘S | Save search |
| ⌘E | Export results |
| J/K | Navigate results |
| ? | Show shortcuts |

## License

MIT
