# 8BG Renaming Tools Scripts

This directory contains scripts for implementing the 8BG naming convention across creative project files.

## Current Scripts

### Core Scripts
- `rename_8bg_complete.sh` - Main complete renaming script with logging
- `rename_8bg_files.py` - Python implementation of the renaming logic
- `burnt_filename_generator.sh` - Generator for BURNT naming convention filenames

### Utility Scripts  
- `8bg_final_cleanup.sh` - Final cleanup and organization
- `8bg_flatten_and_fix.sh` - Flatten directory structure and fix naming issues

## Usage

The main script to use is `rename_8bg_complete.sh` which provides:
- Safe file renaming with conflict detection
- Comprehensive logging
- Dry-run capability

Run with:
```bash
./rename_8bg_complete.sh
```

## Naming Convention

The 8BG convention uses this format:
```
[NUMBER]-[TYPE]-[SUBTYPE]_[PROJECT]_[DESCRIPTION]_[VERSION]_[DATE].[ext]
```

Examples:
- `01-NOTES-PERSONAL_8BG_TreatmentNotes_v01-RR_240315.pages`
- `02-BEATSHEET_8BG_FastBeats_v01_241002.pdf`
- `03-TREATMENT_8BG_MainTreatment_v02-MM_240418.pdf`

## Historical Note

Several scripts in this directory represent different iterations of the same renaming project and are kept for reference. The `rename_8bg_complete.sh` script represents the final, most comprehensive implementation.