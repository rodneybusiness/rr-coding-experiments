#!/usr/bin/env python3
"""
Query and analyze family travel conversations from COGREPO
"""

import json
from datetime import datetime
from collections import Counter

print("🌍 Family Travel Conversation Analysis")
print("=" * 60)

# Read existing family travel file
try:
    # Try multiple possible locations for the data file
    possible_data_paths = [
        '../data/family_travel_conversations.json',
        'family_travel_conversations.json',
        '/Users/newuser/Desktop/family_travel_conversations.json'
    ]
    
    data_path = None
    for path in possible_data_paths:
        if Path(path).exists():
            data_path = path
            break
    
    if not data_path:
        print(f"❌ Error: Could not find family_travel_conversations.json")
        print(f"Tried: {possible_data_paths}")
        sys.exit(1)
    
    with open(data_path, 'r') as f:
        conversations = json.load(f)
    print(f"✅ Found {len(conversations)} family travel conversations\n")
except:
    print("❌ Couldn't read family_travel_conversations.json")
    exit(1)

# Analyze sources
sources = Counter(c.get('source', 'Unknown') for c in conversations)
print("📊 Conversations by source:")
for source, count in sources.most_common():
    print(f"   {source}: {count}")

# Extract mentioned destinations
destinations = []
keywords = ['Paris', 'Stockholm', 'San Sebastián', 'Tokyo', 'New York', 'Sydney', 
            'Byron Bay', 'Vermont', 'Bali', 'Costa Rica', 'Norway', 'Thailand',
            'Amsterdam', 'Barcelona', 'Rome', 'Iceland', 'Cape Town', 'Montreal']

print("\n🗺️ Most mentioned destinations:")
dest_count = Counter()

for convo in conversations:
    text = convo.get('raw_text', '').upper()
    for dest in keywords:
        if dest.upper() in text:
            dest_count[dest] += 1

for dest, count in dest_count.most_common(10):
    print(f"   {dest}: mentioned in {count} conversations")

# Date range
dates = [c.get('timestamp', '') for c in conversations if c.get('timestamp')]
if dates:
    dates.sort()
    print(f"\n📅 Date range: {dates[0][:10]} to {dates[-1][:10]}")

# Sample conversation titles
print("\n📝 Sample conversation topics:")
for i, convo in enumerate(conversations[:5]):
    title = convo.get('generated_title', 'Untitled')
    print(f"   {i+1}. {title}")

# Search for specific travel planning keywords
planning_keywords = ['itinerary', 'hotel', 'flight', 'booking', 'reservation', 
                    'budget', 'visa', 'passport', 'pack', 'airport']

print("\n🎯 Travel planning mentions:")
for keyword in planning_keywords[:5]:
    count = sum(1 for c in conversations if keyword.lower() in c.get('raw_text', '').lower())
    if count > 0:
        print(f"   {keyword}: {count} conversations")

# Save a filtered subset for easier viewing
filtered = []
search_terms = input("\n🔍 Enter search terms (or press Enter for 'family vacation'): ").strip()
if not search_terms:
    search_terms = "family vacation"

for convo in conversations:
    text = (convo.get('raw_text', '') + ' ' + 
            convo.get('generated_title', '') + ' ' + 
            convo.get('summary_abstractive', '')).lower()
    if search_terms.lower() in text:
        filtered.append({
            'date': convo.get('timestamp', '')[:10] if convo.get('timestamp') else 'Unknown',
            'title': convo.get('generated_title', 'Untitled'),
            'summary': convo.get('summary_abstractive', '')[:500] if convo.get('summary_abstractive') else '',
            'convo_id': convo.get('convo_id', 'Unknown')
        })

# Save filtered results
output_file = f'../data/family_travel_filtered_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(output_file, 'w') as f:
    json.dump(filtered, f, indent=2)

print(f"\n💾 Saved {len(filtered)} filtered conversations to:")
print(f"   {output_file}")
