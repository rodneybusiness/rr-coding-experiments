# Shared Utilities

Common functions and utilities used across multiple RR Coding Experiments projects.

## Modules

### `cogrepo_utils.py`
Utilities for working with CogRepo conversation data:

- `load_conversations(repo_path)` - Load conversations from JSONL file
- `search_conversations(conversations, search_terms, custom_query)` - Search conversation content
- `format_conversation_date(timestamp_str)` - Format timestamps for display
- `sort_conversations_by_date(conversations, reverse)` - Sort by timestamp
- `save_conversations_json(conversations, output_path)` - Save to JSON
- `print_conversation_summary(convo, index)` - Print formatted conversation summary

## Usage

Add the shared-utils directory to your Python path or copy the utilities you need:

```python
import sys
sys.path.append('../shared-utils')
from cogrepo_utils import load_conversations, search_conversations

# Load and search conversations
conversations = load_conversations('/path/to/enriched_repository.jsonl')
results = search_conversations(conversations, search_terms=['family travel'])
```

## Integration

These utilities are designed to be used by:
- family-travel-analysis scripts
- cogrepo search tools  
- anime-directors-analysis tools
- Any other project working with conversation data

This reduces code duplication and provides consistent functionality across projects.