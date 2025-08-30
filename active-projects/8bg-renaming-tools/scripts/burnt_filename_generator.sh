#!/bin/bash

# BURNT FILENAME GENERATOR - Consistent Creative File Naming
# 
# Purpose: Interactive tool that helps create properly named files following the
#          8BG naming convention system. No more 'Script_Final_v2_FINAL_really.fdx'
#
# The System: [STAGE]-[SUBCATEGORY]_PROJECT_[DESCRIPTOR]_[VERSION]-[INITIALS]_[DATE]
#            Example: 05-DRAFT_BURNT_ThirdActRevision_v03-RR_250624.fdx
#
# Why This Matters: In film/TV production, sending the wrong script version to a 
#                   studio can cost millions. This system prevents that chaos.

echo "🔥 BURNT - Quick File Creator"
echo "============================"
echo ""
echo "Select file type:"
echo "1) Development Notes"
echo "2) Personal Notes"
echo "3) Feedback/Studio Notes"
echo "4) Meeting Notes"
echo "5) Beatsheet"
echo "6) Treatment"
echo "7) Draft (FDX)"
echo "8) Draft (PDF)"
echo ""
read -p "Choose [1-8]: " choice

# Get current date
DATE=$(date +%y%m%d)

# Get description
read -p "Brief description (e.g., 'ThirdActRevision'): " DESC

# Get version
read -p "Version number (default 01): " VERSION
VERSION=${VERSION:-01}

# Get initials
read -p "Your initials (e.g., RR): " INITIALS

# Build filename based on choice
case $choice in
    1) FILENAME="01-NOTES-DEVELOPMENT_BURNT_${DESC}_v${VERSION}-${INITIALS}_${DATE}.pages" ;;
    2) FILENAME="01-NOTES-PERSONAL_BURNT_${DESC}_v${VERSION}-${INITIALS}_${DATE}.pages" ;;
    3) FILENAME="01-NOTES-FEEDBACK_BURNT_${DESC}_v${VERSION}_${DATE}.rtf" ;;
    4) FILENAME="01-NOTES-MEETING_BURNT_${DESC}_v${VERSION}_${DATE}.rtf" ;;
    5) FILENAME="02-BEATSHEET_BURNT_${DESC}_v${VERSION}-${INITIALS}_${DATE}.pages" ;;
    6) FILENAME="03-TREATMENT_BURNT_${DESC}_v${VERSION}-${INITIALS}_${DATE}.pages" ;;
    7) FILENAME="05-DRAFT_BURNT_${DESC}_v${VERSION}-${INITIALS}_${DATE}.fdx" ;;
    8) FILENAME="05-DRAFT_BURNT_${DESC}_v${VERSION}-${INITIALS}_${DATE}.pdf" ;;
esac

echo ""
echo "✅ Your filename:"
echo "$FILENAME"
echo ""
echo "Copy this to use in your Burnt folder!"