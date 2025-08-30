#!/bin/bash

# Burnt Project File Renaming Script
# Using 8 Billion Genies Naming Convention
# Created: June 25, 2025

cd "/Users/newuser/Dropbox/***Documents/*** Current Film Projects/Burnt"

echo "🔥 Renaming Burnt files using 8BG naming convention..."
echo "================================================"

# Create log file
LOG_FILE="rename_log_$(date +%Y%m%d_%H%M%S).txt"
echo "Burnt Rename Log - $(date)" > "$LOG_FILE"
echo "================================" >> "$LOG_FILE"

renamed_count=0
skipped_count=0

# Function to rename files
rename_file() {
    old_name="$1"
    new_name="$2"
    
    if [ -f "$old_name" ]; then
        if [ ! -f "$new_name" ]; then
            mv -n "$old_name" "$new_name"
            echo "✓ $old_name → $new_name" | tee -a "$LOG_FILE"
            ((renamed_count++))
        else
            echo "⚠ Skipped (already exists): $new_name" | tee -a "$LOG_FILE"
            ((skipped_count++))
        fi
    else
        echo "✗ Not found: $old_name" | tee -a "$LOG_FILE"
    fi
}

echo -e "\n📁 STAGE 01 - NOTES (Development/Research/Personal)"
echo "=================================================="

# Early Development Notes (December 2024)
rename_file "Burnt -- Thoughts + Pitches on 12-17 doc -- RR.pages" \
    "01-NOTES-DEVELOPMENT_BURNT_InitialPitches_v01-RR_241217.pages"

rename_file "Burnt -- Thoughts + Pitches on 12-17 doc -- RR.pdf" \
    "01-NOTES-DEVELOPMENT_BURNT_InitialPitches_v01-RR_241217.pdf"

rename_file "Burnt -- Thoughts + Pitches on 12-17 doc -- RR-1.pages" \
    "01-NOTES-DEVELOPMENT_BURNT_InitialPitches_v02-RR_241217.pages"

rename_file "Burnt -- Thoughts + Pitches on 12-17 doc -- RR-1.pdf" \
    "01-NOTES-DEVELOPMENT_BURNT_InitialPitches_v02-RR_241217.pdf"

rename_file "Burnt -- Thoughts + Pitches on 12-18 doc -- RR.pdf" \
    "01-NOTES-DEVELOPMENT_BURNT_InitialPitches_v03-RR_241218.pdf"

rename_file "Burnt -- Thoughts + Pitches on 12-17 doc -- RR (not used I think?).pages" \
    "01-NOTES-DEVELOPMENT_BURNT_InitialPitches_v01-RR_241217-unused.pages"

# Personal Notes
rename_file "Burnt RR Notes.pdf" \
    "01-NOTES-PERSONAL_BURNT_EarlyThoughts_v01-RR_241217.pdf"

# Research Material
rename_file "midnight-run-1988-1.pdf" \
    "01-NOTES-RESEARCH_BURNT_MidnightRunScript_v01_1988.pdf"

echo -e "\n📁 STAGE 05 - DRAFTS (Working Scripts)"
echo "====================================="

# Original First Act (March 2025)
rename_file "Burnt -- First Act + 30 Pages - Original.fdx" \
    "05-DRAFT_BURNT_FirstAct30Pages_v01_250318.fdx"

rename_file "Burnt -- First Act + 30 Pages.fdx" \
    "05-DRAFT_BURNT_FirstAct30Pages_v02_250322.fdx"

rename_file "Burnt -- First Act + 30 Pages.pdf" \
    "05-DRAFT_BURNT_FirstAct30Pages_v02_250322.pdf"

# RR Revision (March 22)
rename_file "Burnt -- First Act + 30 Pages - RR 3-22-25.pdf" \
    "05-DRAFT_BURNT_FirstAct30Pages_v03-RR_250322.pdf"

# SK+RR Collaboration (June 2025)
rename_file "Burnt -- First Act + 30 Pages - SKRR.fdx" \
    "05-DRAFT_BURNT_FirstAct30Pages_v04-SK-RR_250624.fdx"

rename_file "Burnt -- First Act + 30 Pages - SKRR.pdf" \
    "05-DRAFT_BURNT_FirstAct30Pages_v04-SK-RR_250624.pdf"

rename_file "Burnt -- First Act + 30 Pages - SKRR--fd12.fdx" \
    "05-DRAFT_BURNT_FirstAct30Pages_v05-SK-RR_250624-FD12.fdx"

# Latest Extended Draft (June 24, 2025)
rename_file "Burnt -- First Act + 2A - RR-- 6-24-25.fdx" \
    "05-DRAFT_BURNT_FirstActPlus2A_v01-RR_250624.fdx"

echo -e "\n📊 Summary"
echo "=========="
echo "✓ Successfully renamed: $renamed_count files"
echo "⚠ Skipped (existing): $skipped_count files"
echo ""
echo "📋 Naming Convention Applied:"
echo "- Stage prefixes: 01-NOTES, 05-DRAFT"
echo "- Sub-categories: DEVELOPMENT, PERSONAL, RESEARCH"
echo "- Clear descriptors replacing vague titles"
echo "- Version tracking (v01, v02, etc.)"
echo "- Collaborator initials (RR, SK)"
echo "- Dates in YYMMDD format"
echo ""
echo "💡 Next Steps:"
echo "1. As project progresses, use these stages:"
echo "   - 02-BEATSHEET for story structure docs"
echo "   - 03-TREATMENT for official treatments"
echo "   - 04-VOMDRAFT for rough first drafts"
echo "   - 06-OFFICIAL for studio submissions"
echo "   - 07-FINAL for locked scripts"
echo ""
echo "2. Keep using descriptive names like:"
echo "   - FirstActPlus2A instead of just 'Draft'"
echo "   - InitialPitches instead of 'Thoughts'"
echo "   - EarlyThoughts instead of just 'Notes'"
echo ""
echo "Log saved to: $LOG_FILE"