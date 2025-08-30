#!/usr/bin/env python3
"""
Roam Research Link Counter
Analyzes a Roam export (JSON or MessagePack) to count page links

Usage: 
1. Export your Roam graph
2. Run: python roam_link_counter.py your_export.json
   OR:  python roam_link_counter.py your_export.msgpack
"""

import json
import msgpack
import re
from collections import defaultdict
import sys
import os

def extract_page_references(text):
    """Extract all page references from a block of text"""
    if not isinstance(text, str):
        return []
    
    # Pattern matches [[Page Name]] and #[[Page Name]] and #PageName
    pattern = r'\[\[([^\]]+)\]\]|#\[\[([^\]]+)\]\]|#(\w+)'
    matches = re.findall(pattern, text)
    # Flatten the groups and remove empty strings
    refs = []
    for match in matches:
        for group in match:
            if group:
                refs.append(group)
    return refs

def load_roam_export(filename):
    """Load Roam export from either JSON or MessagePack format"""
    
    print(f"Loading {filename}...")
    
    if filename.endswith('.json'):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif filename.endswith('.msgpack'):
        with open(filename, 'rb') as f:
            # Try different encoding options for msgpack
            try:
                # First try with UTF-8 strict
                return msgpack.unpack(f, raw=False, strict_map_key=False)
            except:
                # If that fails, try with raw mode and handle encoding ourselves
                f.seek(0)
                return msgpack.unpack(f, raw=True, strict_map_key=False)
    else:
        raise ValueError("File must be either .json or .msgpack format")

def safe_decode(data):
    """Safely decode bytes to string, handling various encodings"""
    if isinstance(data, bytes):
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                return data.decode(encoding)
            except:
                continue
        # If all fail, use utf-8 with error handling
        return data.decode('utf-8', errors='ignore')
    elif isinstance(data, dict):
        return {safe_decode(k): safe_decode(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [safe_decode(item) for item in data]
    else:
        return data

def analyze_roam_export(filename):
    """Analyze Roam export and count page references"""
    
    raw_data = load_roam_export(filename)
    
    # Handle encoding issues
    print("Processing data...")
    data = safe_decode(raw_data)
    
    # Dictionary to store link counts
    link_counts = defaultdict(int)
    
    # Set to store all page titles
    all_pages = set()
    
    # First pass: collect all page titles
    for page in data:
        if 'title' in page:
            title = page['title']
            if isinstance(title, str):
                all_pages.add(title)
    
    print(f"Found {len(all_pages)} pages")
    print("Counting references...")
    
    # Second pass: count references
    processed = 0
    for page in data:
        processed += 1
        if processed % 1000 == 0:
            print(f"Processed {processed}/{len(data)} pages...")
            
        if 'children' in page:
            # Recursive function to process all blocks
            def process_blocks(blocks):
                if not isinstance(blocks, list):
                    return
                    
                for block in blocks:
                    if not isinstance(block, dict):
                        continue
                        
                    if 'string' in block:
                        string_content = block['string']
                        if isinstance(string_content, str):
                            refs = extract_page_references(string_content)
                            for ref in refs:
                                # Only count if it's an actual page
                                if ref in all_pages:
                                    link_counts[ref] += 1
                    
                    if 'children' in block:
                        process_blocks(block['children'])
            
            process_blocks(page['children'])
    
    # Sort by link count (descending)
    sorted_pages = sorted(link_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Also include pages with 0 links
    for page in all_pages:
        if page not in link_counts:
            sorted_pages.append((page, 0))
    
    return sorted_pages

def save_results(sorted_pages, output_file='roam_links_sorted.txt'):
    """Save results to a file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Page Title\tLink Count\n")
        f.write("-" * 50 + "\n")
        for page, count in sorted_pages:
            f.write(f"{page}\t{count}\n")
    
    print(f"\nResults saved to {output_file}")
    
    # Save multiple range files
    ranges = [
        (1, 100, 'roam_links_top100.txt'),
        (1, 500, 'roam_links_top500.txt'),
        (500, 1000, 'roam_links_500-1000.txt'),
        (1000, 2000, 'roam_links_1000-2000.txt')
    ]
    
    for start, end, filename in ranges:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Pages Ranked {start}-{end} by Link Count\n")
            f.write("=" * 50 + "\n\n")
            for i, (page, count) in enumerate(sorted_pages[start-1:end], start):
                f.write(f"{i}. {page} ({count} links)\n")
        print(f"Saved pages {start}-{end} to {filename}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python roam_link_counter.py <roam_export_file>")
        print("Example: python roam_link_counter.py backup-Rodney_Graph_1-2024-12-29-20-08-24.msgpack")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found")
        print("\nMake sure the file is in the current directory or provide the full path")
        sys.exit(1)
    
    try:
        # First check if msgpack is installed
        try:
            import msgpack
        except ImportError:
            if filename.endswith('.msgpack'):
                print("Error: msgpack library not installed")
                print("Install it with: pip3 install msgpack")
                sys.exit(1)
        
        sorted_pages = analyze_roam_export(filename)
        save_results(sorted_pages)
        
        # Print top 20 to console
        print("\nTop 20 Most Linked Pages:")
        print("=" * 50)
        for i, (page, count) in enumerate(sorted_pages[:20], 1):
            print(f"{i}. {page} ({count} links)")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
