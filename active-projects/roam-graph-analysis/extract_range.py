#!/usr/bin/env python3
"""
Extract specific ranges from the sorted Roam links file
"""

import sys

def extract_range(start, end, input_file='roam_links_sorted.txt'):
    """Extract a specific range of pages from the sorted list"""
    
    output_file = f'roam_links_{start}-{end}.txt'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Skip the header lines
    header = lines[:2]
    data_lines = lines[2:]
    
    # Extract the requested range (adjusting for 0-based indexing)
    start_idx = start - 1
    end_idx = end
    selected_lines = data_lines[start_idx:end_idx]
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Pages Ranked {start}-{end} by Link Count\n")
        f.write("=" * 50 + "\n\n")
        
        for i, line in enumerate(selected_lines, start):
            page, count = line.strip().split('\t')
            f.write(f"{i}. {page} ({count} links)\n")
    
    print(f"Extracted pages {start}-{end} to {output_file}")
    
    # Also print first 20 to console
    print(f"\nFirst 20 pages from range {start}-{end}:")
    print("-" * 50)
    for i, line in enumerate(selected_lines[:20], start):
        page, count = line.strip().split('\t')
        print(f"{i}. {page} ({count} links)")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Default: extract 500-1000
        extract_range(500, 1000)
    elif len(sys.argv) == 3:
        # Custom range
        start = int(sys.argv[1])
        end = int(sys.argv[2])
        extract_range(start, end)
    else:
        print("Usage:")
        print("  python extract_range.py          # Extract pages 500-1000")
        print("  python extract_range.py 100 200  # Extract pages 100-200")
