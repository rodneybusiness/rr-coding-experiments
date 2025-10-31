# CogRepo Web UI Guide

Beautiful, modern web interface for uploading and processing AI conversations.

## ✨ Features

### Upload Interface
- 📤 **Drag-and-Drop Upload** - Simply drag files onto the upload zone
- 🎯 **Auto-Detection** - Automatically detects ChatGPT, Claude, or Gemini formats
- ⚡ **Real-Time Progress** - Live progress bars and statistics via WebSocket
- 💰 **Cost Estimation** - See estimated API costs before processing
- 📊 **Import History** - Track all your imports with timestamps and stats
- 🎨 **Beautiful UI** - Modern, responsive design with smooth animations

### Search Interface
- 🔍 **Fast Search** - Keyword search across all conversations
- 🏷️ **Filter by Source** - Filter by ChatGPT, Claude, or Gemini
- 📅 **Date Range** - Search within specific time periods
- 📋 **Export Results** - Export search results to JSON

## 🚀 Quick Start

### Starting the Server

```bash
# From the cogrepo directory
./start_web_ui.sh

# Or manually:
cd cogrepo-ui
python3 app.py
```

### Access the UI

Open your browser to:

- **Upload Interface:** http://localhost:5000/upload.html
- **Search Interface:** http://localhost:5000/index.html
- **API Status:** http://localhost:5000/api/status

## 📤 How to Upload & Process

### Step 1: Export Your Conversations

**ChatGPT:**
1. Go to https://chat.openai.com
2. Settings → Data controls → Export data
3. Download `conversations.json` from email

**Claude:**
1. Install [Claude Exporter](https://chromewebstore.google.com/detail/claude-exporter) extension
2. Export conversations as JSON

**Gemini:**
1. Install [Gemini Chat Exporter](https://chromewebstore.google.com/detail/gemini-chat-exporter) extension
2. Export conversations as JSON

### Step 2: Upload via Web UI

1. **Open Upload Page:** http://localhost:5000/upload.html

2. **Drag & Drop or Browse:**
   - Drag your export file onto the upload zone
   - Or click to browse and select file

3. **Configure Options:**
   - **Source:** Auto-detect or manually select platform
   - **AI Enrichment:** Toggle on/off
     - ON: Generates titles, summaries, tags, scores (~$0.025/conversation)
     - OFF: Just imports raw data (free, faster)

4. **Start Import:**
   - Click "Start Import"
   - Watch real-time progress
   - See live statistics

5. **Done!**
   - Import completes automatically
   - Conversations are now searchable
   - View in search interface

### Step 3: Search Your Conversations

1. **Open Search Page:** http://localhost:5000/index.html

2. **Search:**
   - Enter keywords
   - Filter by source
   - Set date range
   - Export results

## 📊 Real-Time Progress Features

During import, you'll see:

- **Progress Bar** - Visual progress (0-100%)
- **Status Updates** - Current processing step
- **Live Statistics:**
  - Total conversations found
  - New conversations (not yet processed)
  - Processed count
  - Failed count
- **Cost Estimation** - API cost estimates (if enriching)
- **Time Remaining** - Estimated completion time

## 🎨 UI Screenshots (Conceptual)

### Upload Page
```
┌─────────────────────────────────────────┐
│  🧠 CogRepo                             │
│  Import & Process Your AI Conversations │
├─────────────────────────────────────────┤
│  📤 Import  |  🔍 Search                │
├─────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  📁 Drag & Drop Your Export File   │ │
│  │     or click to browse             │ │
│  │                                     │ │
│  │  Supports ChatGPT, Claude, Gemini  │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Source: [Auto-detect ▼]                │
│  ☑ Enable AI enrichment                 │
│                                          │
│  [Start Import]                         │
└─────────────────────────────────────────┘
```

### Progress View
```
┌─────────────────────────────────────────┐
│  Processing Import        [Completed]   │
├─────────────────────────────────────────┤
│  ████████████████████ 100%             │
│  Processing conversation 100/100       │
├─────────────────────────────────────────┤
│  Total: 100  New: 50  Processed: 50    │
│  Failed: 0   Cost: $1.25               │
└─────────────────────────────────────────┘
```

## 🔧 API Endpoints

### GET `/api/status`
Server status and statistics
```json
{
  "status": "online",
  "data_exists": true,
  "total_conversations": 2150,
  "api_key_configured": true
}
```

### POST `/api/upload`
Upload and process export file
```
Form data:
- file: Export file (.json, .jsonl)
- source: "auto" | "chatgpt" | "claude" | "gemini"
- enrich: "true" | "false"
```

### GET `/api/imports`
List all imports (history)
```json
{
  "imports": [
    {
      "id": "uuid",
      "filename": "conversations.json",
      "source": "chatgpt",
      "status": "completed",
      "created_time": "2025-10-31T..."
    }
  ]
}
```

### GET `/api/conversations`
Search conversations
```
Query params:
- q: Search query
- source: Filter by source
- limit: Max results (default: 100)
```

## 🌐 WebSocket Events

The UI uses WebSocket for real-time updates:

### Server → Client Events

- `connected` - Connection established
- `import_progress` - Progress updates during processing
- `import_status` - Status changes
- `import_complete` - Import finished successfully
- `import_error` - Import failed

### Client → Server Events

- `subscribe_import` - Subscribe to specific import updates

## 🛠️ Troubleshooting

### Server Won't Start

**Check dependencies:**
```bash
pip install flask flask-socketio flask-cors werkzeug
```

**Check API key:**
```bash
cat .env
# Should show: ANTHROPIC_API_KEY=sk-ant-...
```

### Upload Fails

**File too large:**
- Max size: 500MB
- Split large exports if needed

**Invalid format:**
- Ensure file is .json or .jsonl
- Check file isn't corrupted

**API key error:**
- Disable enrichment (uncheck box)
- Or set ANTHROPIC_API_KEY in .env

### No Progress Updates

**Refresh page:**
- Reload to reconnect WebSocket

**Check browser console:**
- F12 → Console tab
- Look for connection errors

### Port Already in Use

**Change port in app.py:**
```python
socketio.run(app, host='0.0.0.0', port=5001)  # Change port
```

## 💡 Tips & Best Practices

### First Import
1. Start with small file to test (~10 conversations)
2. Try without enrichment first (faster, free)
3. Then enable enrichment for full import

### Incremental Updates
1. Export fresh conversations weekly/monthly
2. Upload via web UI
3. System automatically skips duplicates
4. Only new conversations are processed

### Cost Optimization
- **Without enrichment:** Free, fast (~seconds for 1000 conversations)
- **With enrichment:** ~$0.025 per conversation
  - 50 conversations: ~$1.25
  - 100 conversations: ~$2.50
  - Use for important conversations only

### Performance
- **Upload:** Instant (just file upload)
- **Processing:** ~2 minutes per 50 conversations (with enrichment)
- **Search:** Instant once indexed

## 🎯 Workflow Example

**Weekly update routine:**

1. Monday morning: Export from ChatGPT, Claude, Gemini
2. Open http://localhost:5000/upload.html
3. Drag & drop ChatGPT export
4. Enable enrichment, start import
5. While processing: Repeat for Claude and Gemini
6. 10 minutes later: All conversations searchable!

## 🔒 Security Notes

- Web server runs locally (localhost only)
- No data sent to external servers (except Anthropic API for enrichment)
- API key stored in .env file (not in git)
- Uploaded files deleted after processing

## 📖 Additional Resources

- **IMPORT_GUIDE.md** - Detailed import instructions
- **INCREMENTAL_PROCESSING_PLAN.md** - Technical architecture
- **README.md** - Project overview

---

**Enjoy your beautiful, modern CogRepo web interface!** 🎉
