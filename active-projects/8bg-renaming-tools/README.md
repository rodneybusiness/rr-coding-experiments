# 8BG Renaming Tools
**A Universal File Naming System for Creative Projects**

## What This Is
A comprehensive file naming and organization system originally developed for the "8 Billion Genies" film project, now adapted as a universal taxonomy for ANY creative project (films, scripts, treatments, etc.). The system creates consistent, chronological, and searchable file names that eliminate confusion in collaborative creative environments.

## The Problem It Solves
- Creative projects generate hundreds of versions of scripts, notes, and documents
- Collaborators use inconsistent naming conventions 
- Files get lost or mixed up between versions
- Hard to track chronological progression of drafts
- Difficult to identify who worked on what and when

## Core Philosophy
Every file follows this pattern:
`[STAGE]-[SUBCATEGORY]_[PROJECT]_[DESCRIPTOR]_[VERSION]-[INITIALS]_[DATE](-[TIME]).[EXT]`

Example: `05-DRAFT_BURNT_FirstActRevision_v03-RR_250624.fdx`

## Key Features
- **10 Chronological Stage Prefixes** (00-INFO through 99-SYSTEM)
- **Automatic version tracking** (v01, v02, etc.)
- **Clear ownership** (initials of who made changes)
- **Precise dating** (YYMMDD format)
- **Descriptive naming** (no generic "Draft" or "Notes")
- **Subcategories for notes** (DEVELOPMENT, PERSONAL, FEEDBACK, etc.)

## The Scripts
- `burnt_filename_generator.sh` - Interactive tool to create properly named files
- `8bg_cleanup_stragglers.sh` - Finds and fixes improperly named files
- `batch_rename_8bg.sh` - Bulk renaming operations
- `rename_8bg_files.py` - Python version with more complex logic
- Various fix/cleanup scripts for specific edge cases

## Real-World Usage
Originally built for managing screenplay drafts and notes for "8 Billion Genies" and "Burnt" projects. Now applicable to any creative endeavor requiring version control and collaboration.

## Why It Matters
In creative industries, the difference between "Script_Final_FINAL_reallyFinal_v2.fdx" chaos and a clean, organized system can save hours of searching and prevent costly mistakes with wrong versions being sent to producers or studios.

---
*Created by RR for maintaining sanity in creative collaboration*
