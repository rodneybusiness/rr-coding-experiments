#!/usr/bin/env python3
"""
Extract top 1000 pages from the sorted Roam links file
"""

def extract_top_1000(input_file='roam_links_sorted.txt'):
    """Extract the top 1000 pages from the sorted list"""
    
    output_file = 'roam_links_top1000.txt'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Skip the header lines
    header = lines[:2]
    data_lines = lines[2:]
    
    # Extract top 1000
    selected_lines = data_lines[:1000]
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Top 1000 Most Linked Pages\n")
        f.write("=" * 50 + "\n\n")
        
        for i, line in enumerate(selected_lines, 1):
            page, count = line.strip().split('\t')
            f.write(f"{i}. {page} ({count} links)\n")
    
    print(f"Extracted top 1000 pages to {output_file}")
    
    # Print summary
    print("\nSummary:")
    print(f"- Total pages extracted: {len(selected_lines)}")
    print(f"- File saved as: {output_file}")
    
    # Show first and last few entries
    print("\nFirst 10 pages:")
    for i, line in enumerate(selected_lines[:10], 1):
        page, count = line.strip().split('\t')
        print(f"{i}. {page} ({count} links)")
    
    print("\n...")
    print("\nLast 10 pages (of the top 1000):")
    for i, line in enumerate(selected_lines[-10:], 991):
        page, count = line.strip().split('\t')
        print(f"{i}. {page} ({count} links)")

if __name__ == "__main__":
    extract_top_1000()
