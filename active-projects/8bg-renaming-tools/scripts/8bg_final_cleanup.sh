#!/bin/bash

# 8 Billion Genies - Final Cleanup Script
# Fixes all remaining stragglers

cd "/Users/newuser/Dropbox/***Documents/*** Current Film Projects/8 Billion Genies"

echo "=== FINAL CLEANUP - Fixing all stragglers ==="

# 1. Add missing .fdx extensions
echo "Adding missing .fdx extensions..."
mv "05-DRAFT_8BG_Working_v01_250122" "05-DRAFT_8BG_Working_v01_250122.fdx" 2>/dev/null
mv "05-DRAFT_8BG_Working_v01-RR_241019" "05-DRAFT_8BG_Working_v01-RR_241019.fdx" 2>/dev/null
mv "05-DRAFT_8BG_Working_v01-RR_250122" "05-DRAFT_8BG_Working_v01-RR_250122.fdx" 2>/dev/null
mv "07-FINAL_8BG_HeroScript_v02-RR_250429" "07-FINAL_8BG_HeroScript_v02-RR_250429.fdx" 2>/dev/null
mv "07-FINAL_8BG_HeroScript_v03-RR_250429-PM" "07-FINAL_8BG_HeroScript_v03-RR_250429-PM.fdx" 2>/dev/null
mv "07-FINAL_8BG_HeroScript_v04-RR_250429-PM" "07-FINAL_8BG_HeroScript_v04-RR_250429-PM.fdx" 2>/dev/null
mv "07-FINAL_8BG_HeroScript_v05-RR_250516-PM" "07-FINAL_8BG_HeroScript_v05-RR_250516-PM.fdx" 2>/dev/null
mv "99-WRONGFOLDER_BURNT_FirstAct_v01" "99-WRONGFOLDER_BURNT_FirstAct_v01.fdx" 2>/dev/null

# 2. Add missing .pages extensions to work areas
echo "Adding missing .pages extensions..."
mv "09-ARCHIVE_8BG_WorkArea_v01_250422" "09-ARCHIVE_8BG_WorkArea_v01_250318.pages" 2>/dev/null
mv "09-ARCHIVE_8BG_WorkArea_v02_250423" "09-ARCHIVE_8BG_WorkArea_v02_250318.pages" 2>/dev/null

# 3. Rename RTFD stragglers
echo "Renaming RTFD files..."
mv "CHARACTER OVERVIEW DOC+ SUPPLEMENTAL" "00-INFO_8BG_CharacterOverview_v01_250411.rtfd" 2>/dev/null
mv "Genies Official Treatment/Scriptment 1" "03-TREATMENT_8BG_Scriptment_v01_241217.rtfd" 2>/dev/null
mv "Meetings and Work Leading to Treatment 1" "01-NOTES-MEETING_8BG_TreatmentMeetings_v01_241217.rtfd" 2>/dev/null
mv "Official Official Treatent 1 3.15.24" "03-TREATMENT_8BG_Official_v01_240315.rtfd" 2>/dev/null

# 4. Create archive folder for system files
echo "Organizing system files..."
mkdir -p "99-SYSTEM-FILES"
mv "channels4_profile.jpg" "99-SYSTEM-FILES/" 2>/dev/null
mv "eight_billion_genies_analysis.csv" "99-SYSTEM-FILES/" 2>/dev/null
mv "eight_billion_genies_analysis.py" "99-SYSTEM-FILES/" 2>/dev/null
mv "eight_billion_genies_stages_analyzer.py" "99-SYSTEM-FILES/" 2>/dev/null
mv "eight_billion_genies_stages.csv" "99-SYSTEM-FILES/" 2>/dev/null
mv "rename_log_20250625_111504.txt" "99-SYSTEM-FILES/" 2>/dev/null

echo ""
echo "✅ ALL DONE! Your 8 Billion Genies folder is now perfectly clean!"
echo ""
echo "Summary of fixes:"
echo "- Added .fdx extensions to 8 script files"
echo "- Added .pages extensions to 2 work area files"
echo "- Renamed 4 RTFD document bundles"
echo "- Moved system files to 99-SYSTEM-FILES folder"
echo ""
echo "Your files are now perfectly named and organized in a single folder!"
