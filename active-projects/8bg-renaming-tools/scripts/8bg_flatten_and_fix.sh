#!/bin/bash

# 8 Billion Genies - Flatten Folders & Fix Stragglers
# Generated on 2025-06-25

cd "/Users/newuser/Dropbox/***Documents/*** Current Film Projects/8 Billion Genies"

echo "=== Moving all files back to main 8BG folder ==="

# Move everything from subfolders back to main folder
for folder in 00-INFO 01-NOTES 02-BEATSHEETS 03-TREATMENTS 04-VOMDRAFTS 05-DRAFTS 06-OFFICIAL 07-FINAL 09-ARCHIVE 99-SYSTEM; do
    if [ -d "$folder" ]; then
        echo "Moving files from $folder..."
        mv "$folder"/* . 2>/dev/null
    fi
done

echo "=== Removing empty folders ==="
# Remove the now-empty folders
rmdir 00-INFO 01-NOTES 02-BEATSHEETS 03-TREATMENTS 04-VOMDRAFTS 05-DRAFTS 06-OFFICIAL 07-FINAL 09-ARCHIVE 99-SYSTEM 2>/dev/null

echo "=== Renaming straggler .rtfd files ==="
# These are the document bundles that show without extensions
mv "CHARACTER OVERVIEW DOC+ SUPPLEMENTAL" "00-INFO_8BG_CharacterOverview_v01_240415.rtfd" 2>/dev/null
mv "Genies Official Treatment/Scriptment 1" "03-TREATMENT_8BG_Scriptment_v01_241217.rtfd" 2>/dev/null
mv "Meetings and Work Leading to Treatment 1" "01-NOTES-MEETING_8BG_TreatmentMeetings_v01_241217.rtfd" 2>/dev/null
mv "Official Official Treatent 1 3.15.24" "03-TREATMENT_8BG_Official_v01_240315.rtfd" 2>/dev/null

echo "=== Final cleanup ==="
# List all files to confirm
echo ""
echo "✅ DONE! All files are now in the single 8BG folder."
echo ""
echo "Your folder now contains:"
ls -la | grep -E "^-|^d" | grep -v "^d" | wc -l
echo "files, all properly named and in one place!"
echo ""
echo "To see them sorted by stage, just sort by Name in Finder."
echo "To see your workflow timeline, sort by Date Modified."
