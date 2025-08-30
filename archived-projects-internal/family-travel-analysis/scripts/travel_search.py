#!/usr/bin/env python3
"""
Unified family travel conversation search and analysis tool
Consolidates multiple search scripts into one flexible interface
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict

# Default path to enriched repository - will be resolved dynamically
def get_default_repo_path():
    """Get the default repository path - checks multiple locations"""
    import os
    
    # Try environment variable first
    if 'COGREPO_PATH' in os.environ:
        return os.environ['COGREPO_PATH']
    
    # Try relative paths from current working directory
    possible_paths = [
        # If running from scripts directory
        "../../cogrepo/data/enriched_repository.jsonl",
        # If running from family-travel-analysis directory
        "../cogrepo/data/enriched_repository.jsonl",
        # If running from RR Coding Experiments root
        "cogrepo/data/enriched_repository.jsonl",
        # Fallback to original location (legacy)
        "/Users/newuser/Desktop/COGREPO_FINAL_20250816/enriched_repository.jsonl",
        # Current RR Coding Experiments location
        "/Users/newuser/Desktop/RR Coding Experiments/cogrepo/data/enriched_repository.jsonl"
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            return path
    
    # Return first option as default if none found
    return possible_paths[0]

DEFAULT_REPO_PATH = get_default_repo_path()

# Search terms related to family travel
FAMILY_TRAVEL_TERMS = [
    'family travel', 'family trip', 'family vacation', 
    'travel with kids', 'travel with children', 'family holiday',
    'family adventure', 'family destination', 'family flight',
    'family hotel', 'family resort', 'family cruise',
    'disney', 'disneyland', 'theme park', 'family road trip',
    'traveling with family', 'vacation with kids', 'family getaway',
    'family airbnb', 'family rental', 'family itinerary'
]

def search_conversation(convo_data, search_terms=None, custom_query=None):
    """Check if conversation matches search criteria"""
    searchable_text = []
    
    # Add raw conversation text
    if 'raw_text' in convo_data:
        searchable_text.append(convo_data['raw_text'].lower())
    
    # Add title
    if 'generated_title' in convo_data:
        searchable_text.append(convo_data['generated_title'].lower())
    
    # Add summary
    if 'summary_abstractive' in convo_data:
        searchable_text.append(convo_data['summary_abstractive'].lower())
    
    # Add tags
    if 'tags' in convo_data and isinstance(convo_data['tags'], list):
        searchable_text.append(' '.join(convo_data['tags']).lower())
    
    full_text = ' '.join(searchable_text)
    
    # Custom query search
    if custom_query:
        return custom_query.lower() in full_text
    
    # Default family travel terms
    if search_terms is None:
        search_terms = FAMILY_TRAVEL_TERMS
    
    for term in search_terms:
        if term.lower() in full_text:
            return True
    
    return False

def format_date(timestamp_str):
    """Format timestamp for display"""
    try:
        dt = datetime.strptime(timestamp_str.split('.')[0], "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return timestamp_str

def extract_destinations(conversations):
    """Extract and count destination mentions"""
    destinations = Counter()
    
    # Common destination patterns
    patterns = [
        r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),?\s*(?:California|CA|Florida|FL|New York|NY|Hawaii|HI)\b',
        r'\b(?:went to|visiting|traveled to|trip to|vacation in|flying to)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b',
        r'\b(Paris|London|Tokyo|Rome|Barcelona|Amsterdam|Berlin|Prague|Vienna|Copenhagen)\b',
    ]
    
    for convo in conversations:
        text = convo.get('raw_text', '') + ' ' + convo.get('generated_title', '')
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else match[1]
                destinations[match.title()] += 1
    
    return destinations

def analyze_conversations(conversations):
    """Generate analytics about family travel conversations"""
    print(f"\n📊 Family Travel Analytics")
    print("=" * 50)
    
    # Timeline analysis
    dates = []
    for convo in conversations:
        timestamp = convo.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.strptime(timestamp.split('.')[0], "%Y-%m-%d %H:%M:%S")
                dates.append(dt)
            except:
                continue
    
    if dates:
        dates.sort()
        print(f"📅 Date Range: {dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}")
        
        # Conversations by year
        year_counts = Counter(dt.year for dt in dates)
        print(f"📈 Conversations by Year:")
        for year, count in sorted(year_counts.items()):
            print(f"   {year}: {count} conversations")
    
    # Top destinations
    destinations = extract_destinations(conversations)
    if destinations:
        print(f"\n🌍 Top Destinations Mentioned:")
        for dest, count in destinations.most_common(10):
            print(f"   {dest}: {count} mentions")
    
    # Source analysis
    sources = Counter(convo.get('source', 'Unknown') for convo in conversations)
    print(f"\n💬 Sources:")
    for source, count in sources.most_common():
        print(f"   {source}: {count} conversations")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Search and analyze family travel conversations')
    parser.add_argument('--repo-path', default=DEFAULT_REPO_PATH, help='Path to enriched repository')
    parser.add_argument('--query', help='Custom search query')
    parser.add_argument('--analyze', action='store_true', help='Show analytics')
    parser.add_argument('--save', help='Save results to JSON file')
    parser.add_argument('--limit', type=int, help='Limit number of results shown')
    
    args = parser.parse_args()
    
    print("🔍 Searching for family travel conversations in COGREPO...\n")
    
    # Check if file exists
    if not Path(args.repo_path).exists():
        print(f"❌ Error: Could not find {args.repo_path}")
        sys.exit(1)
    
    # Read and search conversations
    matching_convos = []
    total_convos = 0
    
    print("Reading conversations...")
    with open(args.repo_path, 'r', encoding='utf-8') as f:
        for line in f:
            total_convos += 1
            try:
                convo = json.loads(line)
                if search_conversation(convo, custom_query=args.query):
                    matching_convos.append(convo)
            except json.JSONDecodeError:
                continue
            
            if total_convos % 500 == 0:
                print(f"  Processed {total_convos} conversations...")
    
    # Sort by date
    matching_convos.sort(key=lambda x: x.get('timestamp', ''))
    
    # Show analytics if requested
    if args.analyze and matching_convos:
        analyze_conversations(matching_convos)
    
    # Display results
    query_desc = f"'{args.query}'" if args.query else "family travel terms"
    print(f"\n✅ Found {len(matching_convos)} conversations matching {query_desc} out of {total_convos} total\n")
    
    if not matching_convos:
        return
    
    print("=" * 80)
    
    display_limit = args.limit if args.limit else len(matching_convos)
    for i, convo in enumerate(matching_convos[:display_limit], 1):
        date = format_date(convo.get('timestamp', 'Unknown date'))
        title = convo.get('generated_title', 'Untitled')
        source = convo.get('source', 'Unknown')
        tags = ', '.join(convo.get('tags', [])[:5])
        
        print(f"\n{i}. [{date}] - {source}")
        print(f"   Title: {title}")
        if tags:
            print(f"   Tags: {tags}")
        
        summary = convo.get('summary_abstractive', '')
        if summary:
            excerpt = summary[:150] + "..." if len(summary) > 150 else summary
            print(f"   Summary: {excerpt}")
        
        print("-" * 80)
    
    if args.limit and len(matching_convos) > args.limit:
        print(f"\n... and {len(matching_convos) - args.limit} more results")
    
    # Save results if requested
    if args.save:
        with open(args.save, 'w', encoding='utf-8') as f:
            json.dump(matching_convos, f, indent=2)
        print(f"\n📁 Results saved to: {args.save}")

if __name__ == "__main__":
    main()