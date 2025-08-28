# RR Coding Experiments - Setup Guide

This guide helps you set up the RR Coding Experiments projects for optimal use with terminal, GitHub, and Claude Code.

## ✅ Current Status

All Python scripts now support:
- ✅ **Portable paths** - Work from any directory
- ✅ **GitHub-ready** - Each project can be its own repository  
- ✅ **Environment variables** - Flexible data file locations
- ✅ **Auto-detection** - Scripts find data files automatically
- ✅ **Clean .gitignore** - Large data files excluded but preserved locally

## 🚀 Quick Start

### Option 1: Use as Monorepo
```bash
cd "RR Coding Experiments"
git init
git add .
git commit -m "Initial commit of RR Coding Experiments"
```

### Option 2: Individual Project Repos
```bash
cd family-travel-analysis
git init
git add .
git commit -m "Initial commit: Family Travel Analysis"

cd ../cogrepo  
git init
git add .
git commit -m "Initial commit: CogRepo"

# Repeat for other projects...
```

## 🔧 Environment Setup (Recommended)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# RR Coding Experiments
export COGREPO_PATH="/path/to/your/cogrepo/data/enriched_repository.jsonl"
```

Then run: `source ~/.zshrc`

## 📁 Project Structure

Each project is self-contained:

```
family-travel-analysis/
├── README.md
├── requirements.txt
├── scripts/
│   └── travel_search.py    # Consolidated search tool
└── data/                   # Local data files

cogrepo/
├── README.md  
├── requirements.txt
├── cogrepo_search.py       # Search conversations
├── cogrepo_date_search.py  # Date-based search
└── COGREPO_FINAL_20250816/ # Data files (gitignored)

8bg-renaming-tools/
├── README.md
├── requirements.txt
└── scripts/                # File renaming utilities

zombie-quest/
├── README.md
├── requirements.txt
└── zombie_quest.py         # Game implementation

shared-utils/
├── README.md
├── requirements.txt  
└── cogrepo_utils.py        # Common functions
```

## 🏃‍♂️ Running Scripts

All scripts work from any directory:

```bash
# From project root
python family-travel-analysis/scripts/travel_search.py --help
python cogrepo/cogrepo_search.py "family travel"

# From project directories
cd family-travel-analysis/scripts
python travel_search.py --query "disney" --analyze

cd ../../cogrepo
python cogrepo_search.py "creative projects"
```

## 🧪 Testing Your Setup

Run the path checker to verify everything works:

```bash
./fix_python_paths.sh
```

This will:
- ✅ Check for any remaining hardcoded paths
- ✅ Test script imports and functionality
- ✅ Show current path resolution results
- ✅ Provide setup recommendations

## 🔍 Data File Locations

Scripts automatically search for data files in this order:

1. **Environment variable**: `$COGREPO_PATH`
2. **Relative paths**: `../cogrepo/COGREPO_FINAL_20250816/enriched_repository.jsonl`
3. **Project paths**: `cogrepo/COGREPO_FINAL_20250816/enriched_repository.jsonl`
4. **Fallback paths**: Original desktop locations

## 🤖 Claude Code Integration

Each project includes:
- **requirements.txt** - Dependencies (mostly standard library)
- **README.md** - Project documentation  
- **Portable scripts** - Work from any directory
- **Shared utilities** - Reusable functions in `shared-utils/`

## 🔧 Troubleshooting

### "File not found" errors:
1. Check data file locations with `./fix_python_paths.sh`
2. Set `COGREPO_PATH` environment variable
3. Ensure data files are in expected locations

### Import errors:
1. Run `python -c "import sys; print(sys.path)"` to check Python path
2. Add shared-utils to path: `export PYTHONPATH="$PYTHONPATH:./shared-utils"`
3. Use relative imports in scripts

### Git sync issues:
1. Large data files are gitignored but preserved locally
2. Copy data files manually to new clones
3. Use `COGREPO_PATH` to point to data location

## 📋 Next Steps

1. **Set environment variable** for your data location
2. **Test scripts** with `./fix_python_paths.sh`
3. **Create Git repositories** for projects you want to sync
4. **Add collaborators** to individual project repos as needed

---

*Setup optimized for terminal, GitHub, and Claude Code compatibility* 🎉