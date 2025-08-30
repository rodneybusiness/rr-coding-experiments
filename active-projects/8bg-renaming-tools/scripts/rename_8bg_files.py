import os
import re
import shutil
from datetime import datetime

# Define the base path
base_path = "/Users/newuser/Dropbox/***Documents/*** Current Film Projects/8 Billion Genies"

# Create mapping of old filenames to new filenames
rename_map = {
    # NOTES - RESEARCH
    "Earliest Notes on Fillm Adaptation 3-29.rtf": "01-NOTES-RESEARCH_8BG_FilmAdaptation_v01_230329.rtf",
    "Notes on Comic Books  3-29-2023.rtf": "01-NOTES-RESEARCH_8BG_ComicBookResearch_v01_230329.rtf",
    
    # NOTES - FEEDBACK
    "Amazon:Studio Notes on Treatment.rtf": "01-NOTES-FEEDBACK_8BG_AmazonStudioNotes_v01_240515.rtf",
    "Point Grey Notes on Treatment 1.rtf": "01-NOTES-FEEDBACK_8BG_PointGreyNotes_v01_240315.rtf",
    
    # NOTES - PERSONAL
    "Genies treatment notes-RR.pages": "01-NOTES-PERSONAL_8BG_TreatmentNotes_v01-RR_240315.pages",
    "THE DIAMOND AGE_4.19.24 RR Notes.pages": "01-NOTES-PERSONAL_8BG_DiamondAge_v01-RR_240419.pages",
    "Notes as I plan new beats for finale.rtf": "01-NOTES-PERSONAL_8BG_FinaleBeatsPlanning_v01_241015.rtf",
    "*** Important Rewrite.rtf": "01-NOTES-PERSONAL_8BG_ImportantRewrite_v01_250429.rtf",
    
    # NOTES - MEETING
    "Meetings and Work Leading to Treatment 1.rtfd": "01-NOTES-MEETING_8BG_TreatmentMeetings_v01_240315.rtfd",
    "Meetings to Rebreak Story after Vomit Draft.rtf": "01-NOTES-MEETING_8BG_StoryRebreak_v01_241020.rtf",
    "Work Meetings and PRocess Fall 2024.rtf": "01-NOTES-MEETING_8BG_WorkMeetingsFall2024_v01_241001.rtf",
    
    # BEATSHEETS
    "GENIES fast beats 100224-RR.pages": "02-BEATSHEET_8BG_FastBeats_v01-RR_241002.pages",
    "GENIES fast beats 100224-RR.pdf": "02-BEATSHEET_8BG_FastBeats_v01-RR_241002.pdf",
    "Outline -- Genie Fast Beats 10-1-24.rtf": "02-BEATSHEET_8BG_FastBeatsOutline_v01_241001.rtf",
    "Act 2b + 3 Rough Ouline + Plan.pages": "02-BEATSHEET_8BG_Act2B-3Outline_v01_240406.pages",
    "Act 2b + 3 Rough Ouline + Plan.pdf": "02-BEATSHEET_8BG_Act2B-3Outline_v01_240406.pdf",
    "GENIE 2ND HALF BEATS 092724.pages": "02-BEATSHEET_8BG_SecondHalfBeats_v01_240927.pages",
    "GENIE BEATS 2ND HALF BEATS -- RR 9-26 PM draft.pages": "02-BEATSHEET_8BG_SecondHalfBeats_v02-RR_240926.pages",
    "REVISED GENIE BEATS 091924-RR.pages": "02-BEATSHEET_8BG_RevisedBeats_v01-RR_240919.pages",
    "8BGact3BEATS-RR NOTES.pages": "02-BEATSHEET_8BG_Act3Beats_v01-RR_240415.pages",
    "Act3quickBEATS.pages": "02-BEATSHEET_8BG_Act3QuickBeats_v01_240415.pages",
    "Act3quickBEATS-MMRR.pages": "02-BEATSHEET_8BG_Act3QuickBeats_v02-MM-RR_240416.pages",
    "2b potential beatsREVISED (1).pages": "02-BEATSHEET_8BG_Act2BPotentialBeats_v02_240410.pages",
    "ROBBIEedBEATSrevised--RR.pages": "02-BEATSHEET_8BG_RobbieBeatsRevised_v01-RR_240920.pages",
    "SethiFamilyRevisedBeats.pages": "02-BEATSHEET_8BG_SethiFamilyBeats_v01_240921.pages",
    "ZoomerBeatsRevised.pages": "02-BEATSHEET_8BG_ZoomerBeats_v01_240922.pages",
    "ZoomerBeatsRevised copy.pages": "02-BEATSHEET_8BG_ZoomerBeats_v02_240923.pages",
    
    # TREATMENTS
    "8BG TREATMENT 5_15_24 .pdf": "03-TREATMENT_8BG_Official_v01_240515.pdf",
    "GENIEStreatmentCUTDOWN.pages": "03-TREATMENT_8BG_Short_v01_240515.pages",
    "GENIEStreatmentCUTDOWN -- VER 2.pages": "03-TREATMENT_8BG_Short_v02_240516.pages",
    "Official Official Treatent 1 3.15.24.rtfd": "03-TREATMENT_8BG_Official_v01_240315.rtfd",
    "Genies Official Treatment:Scriptment 1.rtfd": "03-TREATMENT_8BG_Scriptment_v01_240320.rtfd",
    
    # VOMIT DRAFTS
    "***Vomit Draft Fall 2024 First Half (Important).rtf": "04-VOMDRAFT_8BG_FirstHalf_v01_241015.rtf",
    "First Half of Genies Script (Vomit Draft - Needs Revision When Script is Complete) 012225.pdf": "04-VOMDRAFT_8BG_FirstHalf_v01_250122.pdf",
    
    # WORKING DRAFTS
    "GENIES012225.fdx": "05-DRAFT_8BG_Working_v01_250122.fdx",
    "GENIES012225.pdf": "05-DRAFT_8BG_Working_v01_250122.pdf",
    "GENIES012225-RR.fdx": "05-DRAFT_8BG_Working_v01-RR_250122.fdx",
    "GENIES101924.fdx": "05-DRAFT_8BG_Working_v01_241019.fdx",
    "GENIES101924-RR.fdx": "05-DRAFT_8BG_Working_v01-RR_241019.fdx",
    "GENIES1111124.pdf": "05-DRAFT_8BG_Working_v01_241111.pdf",
    
    # OPENING HALF DRAFTS (MM collaboration)
    "GENIES032625-MMopeninghalf.fdx": "05-DRAFT_8BG_OpeningHalf_v01-MM_250326.fdx",
    "GENIES032625-MMopeninghalf -- RR Notes.fdx": "05-DRAFT_8BG_OpeningHalf_v02-RR-MM_250326.fdx",
    "GENIES032625-MMopeninghalf -- RR Notes.pdf": "05-DRAFT_8BG_OpeningHalf_v02-RR-MM_250326.pdf",
    "GENIES032625-MMopeninghalf -- RR Notes2.fdx": "05-DRAFT_8BG_OpeningHalf_v03-RR-MM_250326.fdx",
    "GENIES032625-MMopeninghalf -- RR Notes3.fdx": "05-DRAFT_8BG_OpeningHalf_v04-RR-MM_250326.fdx",
    "GENIES032625-MMopeninghalf -- RR Notes3.pdf": "05-DRAFT_8BG_OpeningHalf_v04-RR-MM_250326.pdf",
    "GENIES032625-MMopeninghalf -- RR Notes v2.pdf": "05-DRAFT_8BG_OpeningHalf_v03-RR-MM_250326.pdf",
    "GENIES032625-MMopeninghalf -- RR Notes4.pdf": "05-DRAFT_8BG_OpeningHalf_v05-RR-MM_250326.pdf",
    "GENIES032625-MMopeninghalf -- RR Notes5.pdf": "05-DRAFT_8BG_OpeningHalf_v06-RR-MM_250326.pdf",
    "GENIES032625-MMopeninghalf -- RR Notes6.pdf": "05-DRAFT_8BG_OpeningHalf_v07-RR-MM_250326.pdf",
    "GENIES032625-MMopeninghalf -- RR Notes7.pdf": "05-DRAFT_8BG_OpeningHalf_v08-RR-MM_250326.pdf",
    "GENIES032625-MMopeninghalf -- RR Notes8.pdf": "05-DRAFT_8BG_OpeningHalf_v09-RR-MM_250326.pdf",
    
    # ACT 2B DRAFTS
    "GENIES-ACT 2B- 0225025 -RR.fdx": "05-DRAFT_8BG_Act2B_v01-RR_250225.fdx",
    "GENIES-ACT 2B- 0225025 -RR.pdf": "05-DRAFT_8BG_Act2B_v01-RR_250225.pdf",
    "GENIES-ACT 2B- 0311025 -RR.fdx": "05-DRAFT_8BG_Act2B_v02-RR_250311.fdx",
    "GENIES-ACT 2B- 0311025 -RR.pdf": "05-DRAFT_8BG_Act2B_v02-RR_250311.pdf",
    "GENIES-ACT 2B- 0312025 -RR.fdx": "05-DRAFT_8BG_Act2B_v03-RR_250312.fdx",
    
    # COLLATED VERSIONS (with time stamps)
    "GENIES040624- COLLATED.fdx": "05-DRAFT_8BG_Collated_v01_240406.fdx",
    "GENIES040624- COLLATED.pdf": "05-DRAFT_8BG_Collated_v01_240406.pdf",
    "GENIES040624- COLLATED -- 420.fdx": "05-DRAFT_8BG_Collated_v02_240406-420PM.fdx",
    "GENIES- COLLATED -- 422 - FORMATTED.fdx": "05-DRAFT_8BG_Collated_v01_250422-422PM.fdx",
    "GENIES- COLLATED -- 422pm - FORMATTED.fdx": "05-DRAFT_8BG_Collated_v02_250422-422PM.fdx",
    "GENIES- COLLATED -- 423pm - FORMATTED.fdx": "05-DRAFT_8BG_Collated_v03_250422-423PM.fdx",
    "GENIES- COLLATED -- 424pm - FORMATTED.-- fd12fdx.fdx": "05-DRAFT_8BG_Collated_v04_250422-424PM-corrupt.fdx",
    "GENIES- COLLATED -- 424pm - FORMATTED.fdx": "05-DRAFT_8BG_Collated_v05_250422-424PM.fdx",
    "GENIES- COLLATED -- 424pm - FORMATTED.pdf": "05-DRAFT_8BG_Collated_v05_250422-424PM.pdf",
    "GENIES- COLLATED -- 425pm - FORMATTED.fdx": "05-DRAFT_8BG_Collated_v06_250422-425PM.fdx",
    "GENIES- COLLATED -- 425pm - FORMATTED.pdf": "05-DRAFT_8BG_Collated_v06_250422-425PM.pdf",
    "GENIES- COLLATED -- 425pm - PARTIAL FORMATTED.pdf": "05-DRAFT_8BG_Collated_v07_250422-425PM-partial.pdf",
    "GENIES- COLLATED -- 425pm - PARTIAL FORMATTED v3.pdf": "05-DRAFT_8BG_Collated_v08_250422-425PM-partialv3.pdf",
    "GENIES- COLLATED -- 428 RR V5 - FORMATTED.fdx": "05-DRAFT_8BG_Collated_v09-RR_250422-428PM.fdx",
    "GENIES- COLLATED -- 428pm - FORMATTED.fdx": "05-DRAFT_8BG_Collated_v10_250422-428PM.fdx",
    "GENIES- COLLATED -- 428pm - FORMATTED.pdf": "05-DRAFT_8BG_Collated_v10_250422-428PM.pdf",
    "GENIES- COLLATED -- 428pm v2 - FORMATTED.pdf": "05-DRAFT_8BG_Collated_v11_250422-428PM.pdf",
    "GENIES- COLLATED -- 429 RR - FORMATTED.fdx": "05-DRAFT_8BG_Collated_v12-RR_250429.fdx",
    
    # OFFICIAL DRAFTS
    "Eight Billion Genies42925.fdx": "06-OFFICIAL_8BG_FirstDraft_v01_250429.fdx",
    "Eight Billion Genies42925.pdf": "06-OFFICIAL_8BG_FirstDraft_v01_250429.pdf",
    "Eight Billion Genies - First Official Draft - RR - 42925.pdf": "06-OFFICIAL_8BG_FirstDraft_v01-RR_250429.pdf",
    "Eight Billion Genies -- First Oficial Draft -- 042925.pdf": "06-OFFICIAL_8BG_FirstDraft_v01_250429-alt.pdf",
    "8BG 4:10:25.pdf": "06-OFFICIAL_8BG_Draft_v01_250410.pdf",
    
    # HERO/FINAL SCRIPTS
    "GENIES-428 SK HERO SCRIPT.fdx": "07-FINAL_8BG_HeroScript_v01-SK_250428.fdx",
    "GENIES-429 RR HERO SCRIPT.fdx": "07-FINAL_8BG_HeroScript_v02-RR_250429.fdx",
    "GENIES-429 RR PM HERO SCRIPT.fdx": "07-FINAL_8BG_HeroScript_v03-RR_250429-PM.fdx",
    "GENIES-429 RR PM V2HERO SCRIPT.fdx": "07-FINAL_8BG_HeroScript_v04-RR_250429-PM.fdx",
    "GENIES-429 RR PM V2HERO SCRIPT.pdf": "07-FINAL_8BG_HeroScript_v04-RR_250429-PM.pdf",
    "GENIES-516 RR PM V2HERO SCRIPT.fdx": "07-FINAL_8BG_HeroScript_v05-RR_250516-PM.fdx",
    "*** MOST IMPORTANT ___ GENIES- COLLATED -- 422pm - FORMATTED.pdf": "07-FINAL_8BG_HeroScript_LOCKED_250422-422PM.pdf",
    
    # SUPPLEMENTAL MATERIALS
    "CHARACTER OVERVIEW DOC+ SUPPLEMENTAL.pdf": "00-INFO_8BG_CharacterOverview_v01_240415.pdf",
    "CHARACTER OVERVIEW DOC+ SUPPLEMENTAL.rtfd": "00-INFO_8BG_CharacterOverview_v01_240415.rtfd",
    "GENIES BLUE SKY PITCHES.pdf": "00-INFO_8BG_BlueSkyPitches_v01_240501.pdf",
    
    # WORK AREAS
    "work area.pages": "09-ARCHIVE_8BG_WorkArea_v01_250422.pages",
    "work area2.pages": "09-ARCHIVE_8BG_WorkArea_v02_250423.pages",
    
    # OTHER PROJECT FILE (shouldn't be here)
    "Burnt -- First Act + 30 Pages.fdx": "99-WRONGFOLDER_BURNT_FirstAct_v01.fdx",
}

# Create log file
log_file = open(os.path.join(base_path, "rename_log.txt"), "w")
log_file.write("8 Billion Genies File Renaming Log\n")
log_file.write("=" * 50 + "\n")
log_file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

# Perform the renaming
successful_renames = 0
failed_renames = 0

for old_name, new_name in rename_map.items():
    old_path = os.path.join(base_path, old_name)
    new_path = os.path.join(base_path, new_name)
    
    try:
        if os.path.exists(old_path):
            # Check if target already exists
            if os.path.exists(new_path):
                log_file.write(f"WARNING: Target already exists, skipping: {old_name} -> {new_name}\n")
                failed_renames += 1
            else:
                # Rename the file
                os.rename(old_path, new_path)
                log_file.write(f"SUCCESS: {old_name} -> {new_name}\n")
                successful_renames += 1
        else:
            log_file.write(f"ERROR: File not found: {old_name}\n")
            failed_renames += 1
    except Exception as e:
        log_file.write(f"ERROR: Failed to rename {old_name}: {str(e)}\n")
        failed_renames += 1

# Summary
log_file.write("\n" + "=" * 50 + "\n")
log_file.write(f"SUMMARY:\n")
log_file.write(f"Successfully renamed: {successful_renames} files\n")
log_file.write(f"Failed to rename: {failed_renames} files\n")
log_file.write(f"Total processed: {len(rename_map)} files\n")

log_file.close()

print(f"Renaming complete!")
print(f"Successfully renamed: {successful_renames} files")
print(f"Failed to rename: {failed_renames} files")
print(f"Check rename_log.txt for details")
