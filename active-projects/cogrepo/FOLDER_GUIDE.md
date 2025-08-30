# CogRepo Folder Organization Guide

## ✅ Clear Structure (After Cleanup)

```
cogrepo/
├── 📋 README.md                 # Main project documentation
├── 📋 FOLDER_GUIDE.md          # This guide
├── 📋 requirements.txt         # Python dependencies
│
├── 🔍 cogrepo_search.py        # PRIMARY: Search conversations by keywords
├── 📅 cogrepo_date_search.py   # PRIMARY: Search by date ranges  
│
├── 🌐 cogrepo-ui/              # Web Interface (Complete & Functional)
│   ├── index.html              # Modern web UI for browsing conversations
│   ├── server.py               # Backend API server
│   ├── package.json            # Node.js config for Claude Code
│   └── README.md               # Web UI documentation
│
└── 📊 data/                    # Processed Conversation Data
    ├── enriched_repository.jsonl      # MAIN DATABASE (165MB, 3,748 conversations)
    ├── focus_list.jsonl               # High-priority items (89MB)
    ├── strategic_projects.json        # Key insights (5KB)
    ├── repository.index               # Search embeddings (45MB)
    ├── repository.index.meta.json     # Index metadata
    ├── standardized_conversations.parquet  # Analysis format (80MB)
    └── README.md                      # Data files documentation
```

## 🎯 What Each Component Does

### **Command Line Tools** (Use These First!)
- **`cogrepo_search.py`** - Find conversations about any topic
- **`cogrepo_date_search.py`** - Find conversations from specific time periods

### **Web Interface** (For Visual Exploration)  
- **`cogrepo-ui/`** - Beautiful web interface with real-time search
- Start with: `cd cogrepo-ui && python server.py`

### **Data Files** (Your Processed Conversations)
- **`data/enriched_repository.jsonl`** - Your main conversation database
- **`data/focus_list.jsonl`** - Pre-filtered high-priority conversations
- **`data/strategic_projects.json`** - AI-generated strategic insights

## 🚀 How to Use Each Component

### **1. Quick Search from Terminal**
```bash
# Search for any topic
python cogrepo_search.py "animation projects"
python cogrepo_search.py "family travel"

# Search by date
python cogrepo_date_search.py --start 2024-01-01 --end 2024-06-30
```

### **2. Visual Exploration (Recommended)**
```bash  
cd cogrepo-ui
python server.py

# Open http://localhost:8000 in browser
# Use the elegant web interface for browsing
```

### **3. Direct Data Access**
```bash
# View strategic insights  
cat data/strategic_projects.json

# Search raw data
grep -i "modern magic" data/enriched_repository.jsonl

# Count conversations by year
grep -o '"timestamp":"[0-9]*' data/enriched_repository.jsonl | cut -d'"' -f4 | cut -c1-4 | sort | uniq -c
```

## 🧹 What Was Removed/Cleaned Up

### ❌ **Removed:**
- **`cogrepo-github/`** - Was an empty template folder causing confusion
- **Duplicate file references** - All paths now point to `data/` folder

### ✅ **Renamed for Clarity:**
- **`COGREPO_FINAL_20250816/`** → **`data/`** (much clearer purpose)

### ✅ **Improved:**
- **All scripts** now auto-detect the `data/` folder location
- **Documentation** clearly explains what each file does
- **Path resolution** works from any directory (terminal, GitHub, Claude Code)

## 🎯 For GitHub & Claude Code

### **GitHub Ready:**
- Each script works as standalone tool
- `data/` folder is gitignored (large files) but preserved locally
- Requirements.txt for easy setup
- Clear documentation for collaborators

### **Claude Code Ready:**
- Scripts work from any directory
- Environment variable support: `export COGREPO_PATH="/path/to/data/enriched_repository.jsonl"`
- Shared utilities in `../shared-utils/cogrepo_utils.py`
- Web UI has package.json for Node.js integration

## 🤔 Which Tool Should I Use?

| Goal | Use This | Why |
|------|----------|-----|
| Quick keyword search | `cogrepo_search.py "topic"` | Fastest, command line |
| Browse conversations visually | `cogrepo-ui/` | Modern interface, real-time search |
| Find conversations by date | `cogrepo_date_search.py` | Optimized for time-based queries |
| View strategic insights | `cat data/strategic_projects.json` | Direct file access |
| Data analysis/programming | `data/enriched_repository.jsonl` | Raw data for custom analysis |

## ✨ Pro Tips

1. **Start with web UI** - Most user-friendly way to explore
2. **Set environment variable** - `export COGREPO_PATH="/full/path/to/data/enriched_repository.jsonl"`  
3. **Use command line for automation** - Scripts are perfect for integrating into workflows
4. **Check strategic_projects.json first** - AI-generated insights save time

---
*Organized for maximum clarity and usability across terminal, GitHub, and Claude Code* 🎉