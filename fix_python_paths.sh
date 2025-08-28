#!/bin/bash

# Fix Python Paths - Updated for consolidated RR Coding Experiments
# This script ensures all Python scripts can work from any directory and with GitHub repos

echo "🔧 RR Coding Experiments - Python Path Checker"
echo "=" * 50

# Function to check if paths are already fixed
check_hardcoded_paths() {
    echo "🔍 Checking for remaining hardcoded paths..."
    
    hardcoded_count=$(grep -r "\/Users\/newuser" . --include="*.py" | wc -l)
    
    if [ "$hardcoded_count" -gt 0 ]; then
        echo "⚠️  Found $hardcoded_count hardcoded paths:"
        grep -r "\/Users\/newuser" . --include="*.py"
        return 1
    else
        echo "✅ No hardcoded user paths found"
        return 0
    fi
}

# Function to test script imports
test_script_functionality() {
    echo ""
    echo "🧪 Testing Python script functionality..."
    
    # Test shared utilities
    if [ -f "shared-utils/cogrepo_utils.py" ]; then
        echo "Testing shared utilities..."
        python3 -c "
import sys
sys.path.append('shared-utils')
try:
    from cogrepo_utils import get_default_repo_path, format_conversation_date
    print('✅ Shared utilities import successfully')
    print(f'   Default repo path: {get_default_repo_path()}')
except Exception as e:
    print(f'❌ Shared utilities error: {e}')
"
    fi
    
    # Test family travel analysis
    if [ -f "family-travel-analysis/scripts/travel_search.py" ]; then
        echo "Testing family travel analysis..."
        cd family-travel-analysis/scripts
        python3 -c "
try:
    from travel_search import get_default_repo_path
    print('✅ Travel search imports successfully')
    print(f'   Repo path: {get_default_repo_path()}')
except Exception as e:
    print(f'❌ Travel search error: {e}')
"
        cd ../..
    fi
    
    # Test cogrepo scripts
    if [ -f "cogrepo/cogrepo_search.py" ]; then
        echo "Testing cogrepo scripts..."
        cd cogrepo
        python3 -c "
try:
    from cogrepo_search import get_repo_path
    print('✅ CogRepo search imports successfully')
    print(f'   Repo path: {get_repo_path()}')
except Exception as e:
    print(f'❌ CogRepo search error: {e}')
"
        cd ..
    fi
}

# Function to show environment setup instructions
show_setup_instructions() {
    echo ""
    echo "📋 Setup Instructions for Optimal Usage:"
    echo "=" * 50
    echo ""
    echo "1. 🌍 Environment Variable (Optional but Recommended):"
    echo "   export COGREPO_PATH=\"/path/to/your/enriched_repository.jsonl\""
    echo "   Add this to your ~/.zshrc or ~/.bashrc for permanent setup"
    echo ""
    echo "2. 🗂️  Directory Structure for GitHub:"
    echo "   Each project can be its own Git repository:"
    echo "   - family-travel-analysis/"
    echo "   - cogrepo/"
    echo "   - 8bg-renaming-tools/"
    echo "   - zombie-quest/"
    echo "   - anime-directors-analysis/"
    echo ""
    echo "3. 🚀 Running Scripts:"
    echo "   From any project directory:"
    echo "   cd family-travel-analysis/scripts && python travel_search.py"
    echo "   cd cogrepo && python cogrepo_search.py \"your query\""
    echo ""
    echo "4. 🔧 Claude Code Integration:"
    echo "   Each project has requirements.txt for easy setup"
    echo "   Scripts auto-detect data file locations"
    echo "   Shared utilities in shared-utils/ for common functions"
}

# Main execution
cd "/Users/newuser/Desktop/RR Coding Experiments"

echo "Current directory: $(pwd)"
echo ""

# Check for hardcoded paths
check_hardcoded_paths

# Test functionality
test_script_functionality

# Show setup instructions
show_setup_instructions

echo ""
echo "🎉 Path optimization complete!"
echo ""
echo "💡 Pro tip: Set COGREPO_PATH environment variable for best experience"
echo "   export COGREPO_PATH=\"$(pwd)/cogrepo/data/enriched_repository.jsonl\""