# Roam Research Link Counter

## The Problem
Your Roam graph has 22,205 pages. The API can't handle returning all pages with their link counts in one query due to size limitations (1MB response limit).

## The Solution
Export your Roam graph and analyze it locally. This gets you EXACTLY what you want - all pages sorted by how many times they're linked.

## Steps

1. **Export your Roam graph:**
   - In Roam, click the `...` menu (top right)
   - Select `Export All`
   - Choose `JSON` format
   - Save to this folder (`/Users/newuser/Desktop/roam_analysis/`)

2. **Run the analysis:**
   ```bash
   cd /Users/newuser/Desktop/roam_analysis/
   python3 roam_link_counter.py your_roam_export.json
   ```

3. **Get your results:**
   - `roam_links_sorted.txt` - ALL pages sorted by link count
   - `roam_links_top100.txt` - Just the top 100 for easy reading
   - Console output shows top 20

## What the script does
- Parses your entire Roam graph
- Counts every `[[Page Reference]]`, `#[[Tag Reference]]`, and `#Tag`
- Sorts all 22,205 pages by how many times they're referenced
- Saves the complete sorted list

## Time estimate
- Export: 1-2 minutes
- Analysis: 10-30 seconds depending on graph size
- Total: Under 3 minutes to get exactly what you want

No API limitations, no pagination, no incomplete results. Just a complete sorted list.
