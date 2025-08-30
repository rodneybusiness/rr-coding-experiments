#!/usr/bin/env python3
"""
Extract top 10,000 pages from the sorted Roam links file
"""

def extract_top_10000(input_file='roam_links_sorted.txt'):
    """Extract the top 10,000 pages from the sorted list"""
    
    output_file = 'roam_links_top10000.txt'
    
    print("Reading sorted pages...")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Skip the header lines
    header = lines[:2]
    data_lines = lines[2:]
    
    # Extract top 10,000
    selected_lines = data_lines[:10000]
    
    # Write to output file
    print(f"Writing top 10,000 pages to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Top 10,000 Most Linked Pages\n")
        f.write("=" * 50 + "\n\n")
        
        for i, line in enumerate(selected_lines, 1):
            if line.strip():  # Skip empty lines
                try:
                    page, count = line.strip().split('\t')
                    f.write(f"{i}. {page} ({count} links)\n")
                except:
                    # Handle any malformed lines
                    f.write(f"{i}. {line.strip()}\n")
    
    print(f"✅ Extracted top 10,000 pages to {output_file}")
    
    # Print summary
    print("\nSummary:")
    print(f"- Total pages extracted: {len(selected_lines)}")
    print(f"- File saved as: {output_file}")
    
    # Show samples
    print("\nFirst 5 pages:")
    for i, line in enumerate(selected_lines[:5], 1):
        try:
            page, count = line.strip().split('\t')
            print(f"{i}. {page} ({count} links)")
        except:
            print(f"{i}. {line.strip()}")
    
    print("\n...")
    
    print(f"\nPages around 5,000:")
    for i, line in enumerate(selected_lines[4995:5005], 4996):
        try:
            page, count = line.strip().split('\t')
            print(f"{i}. {page} ({count} links)")
        except:
            print(f"{i}. {line.strip()}")
    
    print("\n...")
    
    print(f"\nLast 5 pages (of the top 10,000):")
    for i, line in enumerate(selected_lines[-5:], 9996):
        try:
            page, count = line.strip().split('\t')
            print(f"{i}. {page} ({count} links)")
        except:
            print(f"{i}. {line.strip()}")

if __name__ == "__main__":
    extract_top_10000()
