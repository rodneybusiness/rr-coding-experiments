# CogRepo Import & Update Guide

Complete guide for importing and updating conversations from ChatGPT, Claude, and Gemini.

---

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Anthropic API key (required for AI enrichment)
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 2. Export Conversations (see detailed instructions below)

- **ChatGPT:** Settings → Data controls → Export data
- **Claude:** Use browser DevTools or Claude Exporter extension
- **Gemini:** Use Gemini Chat Exporter extension

### 3. Import Conversations

```bash
# First-time import with AI enrichment
python cogrepo_import.py --source chatgpt --file conversations.json --enrich

# Incremental update (only new conversations)
python cogrepo_update.py --source chatgpt --file new_export.json
```

### 4. Update Search Indexes

```bash
python index_builder.py --rebuild
```

### 5. Search!

```bash
# Search from command line
python cogrepo_search.py "your search query"

# Or start web UI
cd cogrepo-ui
python server.py
# Open http://localhost:8000
```

---

## Exporting Conversations

### ChatGPT (OpenAI)

**Method:** Official OpenAI export

**Steps:**
1. Go to ChatGPT: https://chat.openai.com
2. Click your profile icon → **Settings**
3. Go to **Data controls** → **Export data**
4. Click **Export** button
5. Wait for email (can take minutes to hours)
6. Download ZIP file from email link
7. Extract `conversations.json`

**Export Format:**
- File: `conversations.json`
- Format: JSON with tree-based mapping structure
- Includes: Full conversation history, timestamps, branching conversations

**Notes:**
- Export includes ALL conversations ever created
- File can be large (100+ MB for thousands of conversations)
- Safe to run multiple times (deduplication handles it)

---

### Claude (Anthropic)

**Method:** Browser DevTools or Extension

#### Option A: Browser DevTools (Free, Manual)

**Steps:**
1. Open Claude chat: https://claude.ai
2. Open Developer Tools (F12 or Right-click → Inspect)
3. Go to **Network** tab
4. In the filter box, type: `chat_`
5. Open any conversation
6. Find the network request with your conversation
7. Right-click → **Copy** → **Copy response**
8. Paste into a `.json` file

**For Multiple Conversations:**
- Repeat for each conversation you want
- OR use a script to fetch all via API (advanced)

#### Option B: Claude Exporter Extension (Easier)

**Steps:**
1. Install [Claude Exporter](https://chromewebstore.google.com/detail/claude-exporter) from Chrome Web Store
2. Open any Claude conversation
3. Click the extension icon
4. Choose **Export as JSON**
5. Save file

**Export Format:**
- File: `claude_export.json` or `.jsonl`
- Format: Linear message array (simpler than ChatGPT)
- Includes: Messages, timestamps, conversation metadata

**Notes:**
- No official bulk export from Anthropic yet
- Extension method is easiest for multiple conversations
- Can also export single conversations as JSON

---

### Gemini (Google)

**Method:** Chrome Extension

#### Recommended: Gemini Chat Exporter Extension

**Steps:**
1. Install [Gemini Chat Exporter](https://chromewebstore.google.com/detail/gemini-chat-exporter) from Chrome Web Store
2. Open Gemini: https://gemini.google.com
3. Open a conversation
4. Click extension icon
5. Choose **Export as JSON**
6. Repeat for all conversations you want

**Alternative:** Export to Google Docs, then convert

**Steps:**
1. In any Gemini conversation, click **Share & export**
2. Click **Export to Docs**
3. Open the Google Doc
4. File → Download → Web Page (.html)
5. CogRepo can parse HTML exports

**Export Format:**
- File: `gemini_export.json` or `.html`
- Format: Variable (depends on export method)
- Includes: Messages, timestamps (may be limited metadata)

**Notes:**
- No official bulk export yet
- Extension is most reliable method
- HTML exports work but lose some metadata

---

## Using the Import Tools

### First-Time Import

Import all conversations from a platform for the first time:

```bash
# ChatGPT with AI enrichment
python cogrepo_import.py \
  --source chatgpt \
  --file ~/Downloads/conversations.json \
  --enrich

# Claude without enrichment (faster, free)
python cogrepo_import.py \
  --source claude \
  --file ~/Downloads/claude_export.json

# Gemini with auto-detection
python cogrepo_import.py \
  --file ~/Downloads/gemini.json \
  --enrich
```

**Flags:**
- `--source`: Platform (chatgpt, claude, gemini, auto)
- `--file`: Path to export file
- `--enrich`: Enable AI enrichment (requires API key)
- `--dry-run`: Preview without saving

### Incremental Updates

Update with new conversations only:

```bash
# ChatGPT incremental update
python cogrepo_update.py \
  --source chatgpt \
  --file ~/Downloads/new_conversations.json

# Preview what would be updated
python cogrepo_update.py \
  --source claude \
  --file ~/Downloads/claude_new.json \
  --dry-run

# Skip enrichment for speed
python cogrepo_update.py \
  --source gemini \
  --file gemini.json \
  --no-enrich
```

**How It Works:**
1. Loads existing processing state
2. Compares conversation IDs
3. Only processes NEW conversations
4. Updates indexes automatically
5. Safe to run repeatedly

**Example Output:**
```
📊 Current Repository Status:
  Total conversations: 3,748
    OpenAI: 2,100
    Anthropic: 1,500
    Google: 148

📥 Parsing chatgpt export file...
✓ Found 2,150 conversations

🔍 Checking for duplicates...
✓ New conversations: 50
  Already processed: 2,100

🤖 Enriching conversations with AI metadata...
Enriching: 100%|████████████| 50/50 [02:15<00:00]

✓ IMPORT COMPLETE
  Total found: 2,150
  New: 50
  Duplicates: 2,100
  Successfully processed: 50

✓ Repository updated successfully!
  Total conversations now: 3,798 (+50)
```

---

## AI Enrichment

### What Gets Enriched

When you use `--enrich`, each conversation gets:

1. **Generated Title** - Meaningful 5-8 word title
2. **Abstractive Summary** - AI-written summary (250-300 chars)
3. **Extractive Summary** - Key sentences extracted
4. **Primary Domain** - Category (Business, Tech, Creative, etc.)
5. **Tags** - 3-10 relevant keywords
6. **Key Topics** - 3-5 main topics discussed
7. **Brilliance Score** - Quality rating (1-10)
8. **Key Insights** - Important takeaways
9. **Status** - Completed, Ongoing, Reference, etc.
10. **Future Potential** - Value and next steps

### Cost Estimation

Approximate costs per conversation:
- ~5,000 input tokens + ~650 output tokens
- **~$0.025 per conversation** with Claude Sonnet
- Can be reduced 5x by using Haiku for simple tasks

**Examples:**
- 50 conversations: ~$1.25
- 100 conversations: ~$2.50
- 1,000 conversations: ~$25.00

**Tips to Reduce Costs:**
1. Set `use_haiku_for_simple_tasks: true` in config (default)
2. Use `--no-enrich` for drafts, only enrich final imports
3. Process in batches (state is saved, can resume)
4. Increase `min_conversation_length_chars` to skip short convos

### Performance

- **With enrichment:** ~2 minutes per 50 conversations
- **Without enrichment:** ~5 seconds per 1,000 conversations
- **Rate limit:** 50 requests/minute (configurable)

---

## Configuration

Edit `config/enrichment_config.yaml` to customize:

```yaml
# Use cheaper model for simple tasks
api:
  use_haiku_for_simple_tasks: true

# Batch size and rate limiting
processing:
  batch_size: 50
  rate_limit_rpm: 50

# What to enrich
enrichment:
  generate_titles: true
  generate_summaries: true
  extract_tags: true
  calculate_scores: true

# Focus list threshold
output:
  focus_list_min_score: 7
```

---

## Updating Search Indexes

After importing, rebuild indexes for search:

```bash
# Rebuild all indexes
python index_builder.py --rebuild

# Show statistics
python index_builder.py --stats

# Adjust focus list threshold (default: 7)
python index_builder.py --rebuild --min-score 8
```

**What Gets Updated:**
- `repository.index.meta.json` - Conversation IDs and titles
- `focus_list.jsonl` - High-priority conversations (score ≥ 7)

---

## Troubleshooting

### "ANTHROPIC_API_KEY not set"

```bash
# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Or skip enrichment
python cogrepo_import.py --file export.json  # (no --enrich)
```

### "File not found"

Check file path:
```bash
ls -lh ~/Downloads/conversations.json
python cogrepo_import.py --file ~/Downloads/conversations.json --source chatgpt
```

### "Could not detect format"

Specify source explicitly:
```bash
python cogrepo_import.py --source chatgpt --file export.json
```

### Rate Limit Errors

Reduce batch size in `config/enrichment_config.yaml`:
```yaml
processing:
  batch_size: 25  # Lower from 50
  rate_limit_rpm: 30  # Lower from 50
```

### Import Interrupted

Safe to re-run! State is saved every 5 batches:
```bash
# Just run again - will skip already processed
python cogrepo_update.py --source chatgpt --file export.json
```

### Duplicate Conversations

The system automatically deduplicates based on:
1. External conversation ID
2. Content hash (catches same conversation from different exports)

No action needed - safe to import same file multiple times.

---

## Best Practices

### Regular Updates

Schedule weekly/monthly updates:

```bash
#!/bin/bash
# update_cogrepo.sh

# Export conversations (manual step)
# Then run:

python cogrepo_update.py --source chatgpt --file ~/Downloads/chatgpt_latest.json
python cogrepo_update.py --source claude --file ~/Downloads/claude_latest.json
python cogrepo_update.py --source gemini --file ~/Downloads/gemini_latest.json

python index_builder.py --rebuild

echo "✓ CogRepo updated!"
```

### Backup Before Large Imports

```bash
# Backup data directory
cp -r data data_backup_$(date +%Y%m%d)

# Then import
python cogrepo_import.py --source chatgpt --file huge_export.json --enrich
```

### Test with Dry Run First

```bash
# Preview what would be imported
python cogrepo_update.py --source chatgpt --file export.json --dry-run

# If looks good, run for real
python cogrepo_update.py --source chatgpt --file export.json
```

### Incremental Enrichment

Already imported without enrichment? Re-enrich:

```bash
# This will detect and skip already-enriched conversations
python cogrepo_update.py --source chatgpt --file export.json
```

---

## Advanced Usage

### Custom Configuration

Create custom config file:

```bash
cp config/enrichment_config.yaml config/my_config.yaml
# Edit my_config.yaml
python cogrepo_import.py --config config/my_config.yaml --file export.json
```

### Batch Processing

Process in smaller batches:

```bash
# Split large export into smaller files, then:
python cogrepo_import.py --source chatgpt --file batch1.json --enrich
python cogrepo_import.py --source chatgpt --file batch2.json --enrich
# ... state is preserved, no duplicates
```

### Manual Retry of Failed Conversations

Check failed conversations:

```bash
# View processing state
cat data/processing_state.json | jq '.failed_conversations'
```

Edit export file to include only failed conversations, then re-import.

---

## Workflow Summary

**First Time Setup:**
1. Export from ChatGPT, Claude, Gemini
2. `pip install -r requirements.txt`
3. `export ANTHROPIC_API_KEY="..."`
4. `python cogrepo_import.py --source chatgpt --file export.json --enrich`
5. `python index_builder.py --rebuild`
6. Start using search tools

**Regular Updates:**
1. Export new conversations
2. `python cogrepo_update.py --source chatgpt --file new_export.json`
3. `python index_builder.py --rebuild`
4. Done!

---

## Getting Help

**Check stats:**
```bash
python index_builder.py --stats
cat data/processing_state.json | jq '.processing_stats'
```

**Verbose output:**
```bash
python cogrepo_import.py --file export.json --source chatgpt --enrich 2>&1 | tee import.log
```

**Common issues:** See Troubleshooting section above

---

*For technical architecture details, see `INCREMENTAL_PROCESSING_PLAN.md`*
