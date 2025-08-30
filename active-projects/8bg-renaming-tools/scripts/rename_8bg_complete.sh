#!/bin/bash

# 8 Billion Genies Complete File Renaming Script
# Generated on 2025-06-25
# This script renames all files in the 8 Billion Genies folder to the new naming convention

# Set the working directory
cd "/Users/newuser/Dropbox/***Documents/*** Current Film Projects/8 Billion Genies"

# Create a log file
LOG_FILE="rename_log_$(date +%Y%m%d_%H%M%S).txt"
echo "8 Billion Genies File Renaming Log" > "$LOG_FILE"
echo "Started at: $(date)" >> "$LOG_FILE"
echo "=================================" >> "$LOG_FILE"

# Function to safely rename files
safe_rename() {
    if [ -f "$1" ]; then
        if [ ! -f "$2" ]; then
            mv -n "$1" "$2" && echo "✓ Renamed: $1 -> $2" | tee -a "$LOG_FILE"
        else
            echo "✗ Skipped (target exists): $2" | tee -a "$LOG_FILE"
        fi
    else
        echo "✗ Not found: $1" | tee -a "$LOG_FILE"
    fi
}

echo "Starting batch rename..."

# NOTES - FEEDBACK
safe_rename "Point Grey Notes on Treatment 1.rtf" "01-NOTES-FEEDBACK_8BG_PointGreyNotes_v01_240315.rtf"

# NOTES - PERSONAL
safe_rename "Genies treatment notes-RR.pages" "01-NOTES-PERSONAL_8BG_TreatmentNotes_v01-RR_240315.pages"
safe_rename "THE DIAMOND AGE_4.19.24 RR Notes.pages" "01-NOTES-PERSONAL_8BG_DiamondAge_v01-RR_240419.pages"
safe_rename "Notes as I plan new beats for finale.rtf" "01-NOTES-PERSONAL_8BG_FinaleBeatsPlanning_v01_241015.rtf"
safe_rename "*** Important Rewrite.rtf" "01-NOTES-PERSONAL_8BG_ImportantRewrite_v01_250429.rtf"

# NOTES - MEETING
safe_rename "Meetings and Work Leading to Treatment 1.rtfd" "01-NOTES-MEETING_8BG_TreatmentMeetings_v01_240315.rtfd"
safe_rename "Meetings to Rebreak Story after Vomit Draft.rtf" "01-NOTES-MEETING_8BG_StoryRebreak_v01_241020.rtf"
safe_rename "Work Meetings and PRocess Fall 2024.rtf" "01-NOTES-MEETING_8BG_WorkMeetingsFall2024_v01_241001.rtf"

# BEATSHEETS
safe_rename "GENIES fast beats 100224-RR.pdf" "02-BEATSHEET_8BG_FastBeats_v01-RR_241002.pdf"
safe_rename "Outline -- Genie Fast Beats 10-1-24.rtf" "02-BEATSHEET_8BG_FastBeatsOutline_v01_241001.rtf"
safe_rename "Act 2b + 3 Rough Ouline + Plan.pages" "02-BEATSHEET_8BG_Act2B-3Outline_v01_240406.pages"
safe_rename "Act 2b + 3 Rough Ouline + Plan.pdf" "02-BEATSHEET_8BG_Act2B-3Outline_v01_240406.pdf"
safe_rename "GENIE 2ND HALF BEATS 092724.pages" "02-BEATSHEET_8BG_SecondHalfBeats_v01_240927.pages"
safe_rename "GENIE BEATS 2ND HALF BEATS -- RR 9-26 PM draft.pages" "02-BEATSHEET_8BG_SecondHalfBeats_v02-RR_240926.pages"
safe_rename "REVISED GENIE BEATS 091924-RR.pages" "02-BEATSHEET_8BG_RevisedBeats_v01-RR_240919.pages"
safe_rename "8BGact3BEATS-RR NOTES.pages" "02-BEATSHEET_8BG_Act3Beats_v01-RR_240415.pages"
safe_rename "Act3quickBEATS.pages" "02-BEATSHEET_8BG_Act3QuickBeats_v01_240415.pages"
safe_rename "Act3quickBEATS-MMRR.pages" "02-BEATSHEET_8BG_Act3QuickBeats_v02-MM-RR_240416.pages"
safe_rename "2b potential beatsREVISED (1).pages" "02-BEATSHEET_8BG_Act2BPotentialBeats_v02_240410.pages"
safe_rename "ROBBIEedBEATSrevised--RR.pages" "02-BEATSHEET_8BG_RobbieBeatsRevised_v01-RR_240920.pages"
safe_rename "SethiFamilyRevisedBeats.pages" "02-BEATSHEET_8BG_SethiFamilyBeats_v01_240921.pages"
safe_rename "ZoomerBeatsRevised.pages" "02-BEATSHEET_8BG_ZoomerBeats_v01_240922.pages"
safe_rename "ZoomerBeatsRevised copy.pages" "02-BEATSHEET_8BG_ZoomerBeats_v02_240923.pages"

# TREATMENTS
safe_rename "GENIEStreatmentCUTDOWN -- VER 2.pages" "03-TREATMENT_8BG_Short_v02_240516.pages"
safe_rename "Official Official Treatent 1 3.15.24.rtfd" "03-TREATMENT_8BG_Official_v01_240315.rtfd"
safe_rename "Genies Official Treatment:Scriptment 1.rtfd" "03-TREATMENT_8BG_Scriptment_v01_240320.rtfd"

# VOMIT DRAFTS
safe_rename "First Half of Genies Script (Vomit Draft - Needs Revision When Script is Complete) 012225.pdf" "04-VOMDRAFT_8BG_FirstHalf_v01_250122.pdf"

# WORKING DRAFTS
safe_rename "GENIES012225.fdx" "05-DRAFT_8BG_Working_v01_250122.fdx"
safe_rename "GENIES012225.pdf" "05-DRAFT_8BG_Working_v01_250122.pdf"
safe_rename "GENIES012225-RR.fdx" "05-DRAFT_8BG_Working_v01-RR_250122.fdx"
safe_rename "GENIES101924.fdx" "05-DRAFT_8BG_Working_v01_241019.fdx"
safe_rename "GENIES101924-RR.fdx" "05-DRAFT_8BG_Working_v01-RR_241019.fdx"
safe_rename "GENIES1111124.pdf" "05-DRAFT_8BG_Working_v01_241111.pdf"

# OPENING HALF DRAFTS (MM collaboration)
safe_rename "GENIES032625-MMopeninghalf.fdx" "05-DRAFT_8BG_OpeningHalf_v01-MM_250326.fdx"
safe_rename "GENIES032625-MMopeninghalf -- RR Notes.fdx" "05-DRAFT_8BG_OpeningHalf_v02-RR-MM_250326.fdx"
safe_rename "GENIES032625-MMopeninghalf -- RR Notes.pdf" "05-DRAFT_8BG_OpeningHalf_v02-RR-MM_250326.pdf"
safe_rename "GENIES032625-MMopeninghalf -- RR Notes2.fdx" "05-DRAFT_8BG_OpeningHalf_v03-RR-MM_250326.fdx"
safe_rename "GENIES032625-MMopeninghalf -- RR Notes3.fdx" "05-DRAFT_8BG_OpeningHalf_v04-RR-MM_250326.fdx"
safe_rename "GENIES032625-MMopeninghalf -- RR Notes3.pdf" "05-DRAFT_8BG_OpeningHalf_v04-RR-MM_250326.pdf"
safe_rename "GENIES032625-MMopeninghalf -- RR Notes v2.pdf" "05-DRAFT_8BG_OpeningHalf_v03-RR-MM_250326.pdf"
safe_rename "GENIES032625-MMopeninghalf -- RR Notes4.pdf" "05-DRAFT_8BG_OpeningHalf_v05-RR-MM_250326.pdf"
safe_rename "GENIES032625-MMopeninghalf -- RR Notes5.pdf" "05-DRAFT_8BG_OpeningHalf_v06-RR-MM_250326.pdf"
safe_rename "GENIES032625-MMopeninghalf -- RR Notes6.pdf" "05-DRAFT_8BG_OpeningHalf_v07-RR-MM_250326.pdf"
safe_rename "GENIES032625-MMopeninghalf -- RR Notes7.pdf" "05-DRAFT_8BG_OpeningHalf_v08-RR-MM_250326.pdf"
safe_rename "GENIES032625-MMopeninghalf -- RR Notes8.pdf" "05-DRAFT_8BG_OpeningHalf_v09-RR-MM_250326.pdf"

# ACT 2B DRAFTS
safe_rename "GENIES-ACT 2B- 0225025 -RR.fdx" "05-DRAFT_8BG_Act2B_v01-RR_250225.fdx"
safe_rename "GENIES-ACT 2B- 0225025 -RR.pdf" "05-DRAFT_8BG_Act2B_v01-RR_250225.pdf"
safe_rename "GENIES-ACT 2B- 0311025 -RR.fdx" "05-DRAFT_8BG_Act2B_v02-RR_250311.fdx"
safe_rename "GENIES-ACT 2B- 0311025 -RR.pdf" "05-DRAFT_8BG_Act2B_v02-RR_250311.pdf"
safe_rename "GENIES-ACT 2B- 0312025 -RR.fdx" "05-DRAFT_8BG_Act2B_v03-RR_250312.fdx"

# COLLATED VERSIONS (with time stamps in your preferred 425PM format)
safe_rename "GENIES040624- COLLATED.fdx" "05-DRAFT_8BG_Collated_v01_240406.fdx"
safe_rename "GENIES040624- COLLATED.pdf" "05-DRAFT_8BG_Collated_v01_240406.pdf"
safe_rename "GENIES040624- COLLATED -- 420.fdx" "05-DRAFT_8BG_Collated_v02_240406-420PM.fdx"
safe_rename "GENIES- COLLATED -- 422 - FORMATTED.fdx" "05-DRAFT_8BG_Collated_v01_250422-422PM.fdx"
safe_rename "GENIES- COLLATED -- 422pm - FORMATTED.fdx" "05-DRAFT_8BG_Collated_v02_250422-422PM.fdx"
safe_rename "GENIES- COLLATED -- 423pm - FORMATTED.fdx" "05-DRAFT_8BG_Collated_v03_250422-423PM.fdx"
safe_rename "GENIES- COLLATED -- 424pm - FORMATTED.-- fd12fdx.fdx" "05-DRAFT_8BG_Collated_v04_250422-424PM-corrupt.fdx"
safe_rename "GENIES- COLLATED -- 424pm - FORMATTED.fdx" "05-DRAFT_8BG_Collated_v05_250422-424PM.fdx"
safe_rename "GENIES- COLLATED -- 424pm - FORMATTED.pdf" "05-DRAFT_8BG_Collated_v05_250422-424PM.pdf"
safe_rename "GENIES- COLLATED -- 425pm - FORMATTED.pdf" "05-DRAFT_8BG_Collated_v06_250422-425PM.pdf"
safe_rename "GENIES- COLLATED -- 425pm - PARTIAL FORMATTED.pdf" "05-DRAFT_8BG_Collated_v07_250422-425PM-partial.pdf"
safe_rename "GENIES- COLLATED -- 425pm - PARTIAL FORMATTED v3.pdf" "05-DRAFT_8BG_Collated_v08_250422-425PM-partialv3.pdf"
safe_rename "GENIES- COLLATED -- 428 RR V5 - FORMATTED.fdx" "05-DRAFT_8BG_Collated_v09-RR_250422-428PM.fdx"
safe_rename "GENIES- COLLATED -- 428pm - FORMATTED.fdx" "05-DRAFT_8BG_Collated_v10_250422-428PM.fdx"
safe_rename "GENIES- COLLATED -- 428pm - FORMATTED.pdf" "05-DRAFT_8BG_Collated_v10_250422-428PM.pdf"
safe_rename "GENIES- COLLATED -- 428pm v2 - FORMATTED.pdf" "05-DRAFT_8BG_Collated_v11_250422-428PM.pdf"
safe_rename "GENIES- COLLATED -- 429 RR - FORMATTED.fdx" "05-DRAFT_8BG_Collated_v12-RR_250429.fdx"

# OFFICIAL DRAFTS
safe_rename "Eight Billion Genies42925.fdx" "06-OFFICIAL_8BG_FirstDraft_v01_250429.fdx"
safe_rename "Eight Billion Genies42925.pdf" "06-OFFICIAL_8BG_FirstDraft_v01_250429.pdf"
safe_rename "Eight Billion Genies - First Official Draft - RR - 42925.pdf" "06-OFFICIAL_8BG_FirstDraft_v01-RR_250429.pdf"
safe_rename "Eight Billion Genies -- First Oficial Draft -- 042925.pdf" "06-OFFICIAL_8BG_FirstDraft_v01_250429-alt.pdf"
safe_rename "8BG 4:10:25.pdf" "06-OFFICIAL_8BG_Draft_v01_250410.pdf"

# HERO/FINAL SCRIPTS
safe_rename "GENIES-428 SK HERO SCRIPT.fdx" "07-FINAL_8BG_HeroScript_v01-SK_250428.fdx"
safe_rename "GENIES-429 RR HERO SCRIPT.fdx" "07-FINAL_8BG_HeroScript_v02-RR_250429.fdx"
safe_rename "GENIES-429 RR PM HERO SCRIPT.fdx" "07-FINAL_8BG_HeroScript_v03-RR_250429-PM.fdx"
safe_rename "GENIES-429 RR PM V2HERO SCRIPT.pdf" "07-FINAL_8BG_HeroScript_v04-RR_250429-PM.pdf"
safe_rename "GENIES-516 RR PM V2HERO SCRIPT.fdx" "07-FINAL_8BG_HeroScript_v05-RR_250516-PM.fdx"

# SUPPLEMENTAL MATERIALS
safe_rename "CHARACTER OVERVIEW DOC+ SUPPLEMENTAL.pdf" "00-INFO_8BG_CharacterOverview_v01_240415.pdf"
safe_rename "CHARACTER OVERVIEW DOC+ SUPPLEMENTAL.rtfd" "00-INFO_8BG_CharacterOverview_v01_240415.rtfd"
safe_rename "GENIES BLUE SKY PITCHES.pdf" "00-INFO_8BG_BlueSkyPitches_v01_240501.pdf"

# WORK AREAS
safe_rename "work area.pages" "09-ARCHIVE_8BG_WorkArea_v01_250422.pages"
safe_rename "work area2.pages" "09-ARCHIVE_8BG_WorkArea_v02_250423.pages"

# OTHER PROJECT FILE (shouldn't be here)
safe_rename "Burnt -- First Act + 30 Pages.fdx" "99-WRONGFOLDER_BURNT_FirstAct_v01.fdx"

# Summary
echo "=================================" >> "$LOG_FILE"
echo "Completed at: $(date)" >> "$LOG_FILE"
RENAMED=$(grep -c "✓ Renamed:" "$LOG_FILE")
SKIPPED=$(grep -c "✗ Skipped:" "$LOG_FILE")
NOTFOUND=$(grep -c "✗ Not found:" "$LOG_FILE")

echo ""
echo "RENAME COMPLETE!"
echo "================"
echo "✓ Successfully renamed: $RENAMED files"
echo "⚠ Skipped (already exist): $SKIPPED files"  
echo "✗ Not found: $NOTFOUND files"
echo ""
echo "Check $LOG_FILE for details"
echo ""
echo "Next steps:"
echo "1. Create folder structure: mkdir -p {00-INFO,01-NOTES,02-BEATSHEETS,03-TREATMENTS,04-VOMDRAFTS,05-DRAFTS,06-OFFICIAL,07-FINAL,09-ARCHIVE}"
echo "2. Move files to folders: for f in 01-NOTES-*; do mv \"\$f\" 01-NOTES/; done"
