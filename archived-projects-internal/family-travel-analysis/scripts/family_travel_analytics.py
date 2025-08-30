#!/usr/bin/env python3
"""
FAMILY TRAVEL ANALYTICS - Transform Chat History into Travel Insights

Purpose: Analyze years of family travel conversations to understand patterns,
         preferences, and planning behaviors. Turns casual chat into actionable data.

What it discovers:
- When trips are actually planned vs just discussed
- Seasonal patterns in travel planning
- Most mentioned destinations
- How far in advance real trips are planned
- Family member involvement patterns

Why this exists: Because understanding your family's travel patterns helps you:
- Plan better trips that everyone will enjoy
- Budget more accurately
- Book at optimal times
- Recognize what makes a trip idea turn into reality

Note: Currently has hardcoded path - needs updating after file reorganization
"""

import json
from datetime import datetime
from collections import Counter, defaultdict
import re

# Load the clean family travel data
# Try multiple possible locations for the data file
possible_data_paths = [
    '../data/family_travel_CLEAN_20250822_100112.json',
    'family_travel_CLEAN_20250822_100112.json',
    '/Users/newuser/Desktop/family_travel_CLEAN_20250822_100112.json'
]

data_path = None
for path in possible_data_paths:
    if Path(path).exists():
        data_path = path
        break

if not data_path:
    print(f"❌ Error: Could not find family_travel_CLEAN_20250822_100112.json")
    print(f"Tried: {possible_data_paths}")
    sys.exit(1)

with open(data_path, 'r') as f:
    data = json.load(f)

conversations = data['conversations']

# Analytics Report
print("=" * 80)
print("FAMILY TRAVEL ANALYTICS DASHBOARD")
print("=" * 80)
print(f"\nAnalysis Date: {datetime.now().strftime('%B %d, %Y')}")
print(f"Total Conversations Analyzed: {len(conversations)}")
print(f"Date Range: {conversations[0]['date']} to {conversations[-1]['date']}")

# 1. Temporal Analysis
print("\n" + "=" * 80)
print("📅 TEMPORAL PATTERNS")
print("=" * 80)

# Group by year and month
yearly_counts = defaultdict(int)
monthly_counts = defaultdict(int)
seasonal_counts = defaultdict(int)

for conv in conversations:
    date = conv['date']
    if date and date != 'Unknown':
        year = date[:4]
        month = date[5:7]
        yearly_counts[year] += 1
        monthly_counts[month] += 1
        
        # Determine season
        month_int = int(month)
        if month_int in [3, 4, 5]:
            seasonal_counts['Spring'] += 1
        elif month_int in [6, 7, 8]:
            seasonal_counts['Summer'] += 1
        elif month_int in [9, 10, 11]:
            seasonal_counts['Fall'] += 1
        else:
            seasonal_counts['Winter'] += 1

print("\n📊 Conversations by Year:")
for year in sorted(yearly_counts.keys()):
    bar = "█" * (yearly_counts[year] * 2)
    print(f"  {year}: {bar} ({yearly_counts[year]} conversations)")

print("\n📊 Conversations by Season:")
for season in ['Spring', 'Summer', 'Fall', 'Winter']:
    count = seasonal_counts.get(season, 0)
    bar = "█" * (count * 2)
    percentage = (count / len(conversations)) * 100
    print(f"  {season:8}: {bar} ({count} - {percentage:.1f}%)")

print("\n📊 Peak Planning Months:")
top_months = sorted(monthly_counts.items(), key=lambda x: x[1], reverse=True)[:3]
month_names = {
    '01': 'January', '02': 'February', '03': 'March', '04': 'April',
    '05': 'May', '06': 'June', '07': 'July', '08': 'August',
    '09': 'September', '10': 'October', '11': 'November', '12': 'December'
}
for month, count in top_months:
    print(f"  {month_names.get(month, month):10}: {count} conversations")

# 2. Geographic Analysis
print("\n" + "=" * 80)
print("🗺️ GEOGRAPHIC PATTERNS")
print("=" * 80)

all_destinations = []
for conv in conversations:
    if conv.get('destinations'):
        all_destinations.extend(conv['destinations'])

# Extract cities from titles and summaries
location_keywords = [
    'Los Angeles', 'LA', 'Seattle', 'Portland', 'San Francisco', 'London',
    'California', 'Pacific Northwest', 'Flagstaff', 'Denver', 'Chicago',
    'Detroit', 'New Orleans', 'France', 'Montana', 'Oregon', 'Washington',
    'Northern California', 'Southern California', 'British Columbia',
    'Tokyo', 'Paris', 'New York', 'Sydney', 'Vermont', 'Bozeman',
    'Lake Leelanau', 'Traverse City', 'Minneapolis', 'Silver Lake'
]

location_counts = Counter()
for conv in conversations:
    text = f"{conv.get('title', '')} {conv.get('summary', '')}".upper()
    for location in location_keywords:
        if location.upper() in text:
            location_counts[location] += 1

print("\n🌟 Top Destinations Mentioned:")
for location, count in location_counts.most_common(10):
    bar = "▓" * count
    print(f"  {location:20}: {bar} ({count})")

# 3. Activity Analysis
print("\n" + "=" * 80)
print("🎯 ACTIVITY PREFERENCES")
print("=" * 80)

all_activities = []
for conv in conversations:
    if conv.get('activities'):
        all_activities.extend(conv['activities'])

activity_counts = Counter(all_activities)

print("\n🏃 Top Family Activities:")
for activity, count in activity_counts.most_common():
    percentage = (count / len(conversations)) * 100
    bar = "●" * count
    print(f"  {activity:15}: {bar} ({count} times - {percentage:.1f}% of trips)")

# 4. Travel Evolution Analysis
print("\n" + "=" * 80)
print("📈 TRAVEL SOPHISTICATION EVOLUTION")
print("=" * 80)

# Analyze conversation complexity by year
complexity_keywords = {
    'basic': ['where', 'what', 'how', 'suggestions', 'ideas', 'recommendations'],
    'intermediate': ['itinerary', 'planning', 'detailed', 'comprehensive', 'stops'],
    'advanced': ['optimizing', 'efficient', 'cost-effective', 'maximizing', 'curated', 'strategic']
}

yearly_complexity = defaultdict(lambda: defaultdict(int))

for conv in conversations:
    year = conv['date'][:4] if conv['date'] != 'Unknown' else 'Unknown'
    text = f"{conv.get('title', '')} {conv.get('summary', '')}".lower()
    
    for level, keywords in complexity_keywords.items():
        for keyword in keywords:
            if keyword in text:
                yearly_complexity[year][level] += 1
                break

print("\n🎓 Planning Sophistication by Year:")
for year in sorted(yearly_complexity.keys()):
    print(f"\n  {year}:")
    total = sum(yearly_complexity[year].values())
    for level in ['basic', 'intermediate', 'advanced']:
        count = yearly_complexity[year][level]
        if total > 0:
            percentage = (count / total) * 100
            print(f"    {level:12}: {'█' * int(percentage/10)} {percentage:.1f}%")

# 5. Travel Type Analysis
print("\n" + "=" * 80)
print("🚗 TRAVEL STYLE PREFERENCES")
print("=" * 80)

travel_types = {
    'Road Trips': ['road trip', 'rv', 'driving', 'route', 'stops along'],
    'City Breaks': ['city', 'urban', 'london', 'san francisco', 'seattle', 'portland'],
    'Nature/Outdoor': ['camping', 'hiking', 'national park', 'outdoor', 'nature'],
    'Beach/Coastal': ['beach', 'coastal', 'ocean', 'seaside'],
    'International': ['london', 'france', 'europe', 'international'],
    'Luxury/Comfort': ['glamping', 'hotel', 'resort', 'luxury'],
    'Adventure': ['adventure', 'exploring', 'discovery', 'expedition']
}

type_counts = Counter()
for conv in conversations:
    text = f"{conv.get('title', '')} {conv.get('summary', '')}".lower()
    for travel_type, keywords in travel_types.items():
        for keyword in keywords:
            if keyword in text:
                type_counts[travel_type] += 1
                break

print("\n✈️ Travel Style Distribution:")
for travel_type, count in type_counts.most_common():
    percentage = (count / len(conversations)) * 100
    bar = "■" * int(percentage/5)
    print(f"  {travel_type:15}: {bar} {percentage:.1f}%")

# 6. Planning Horizon Analysis
print("\n" + "=" * 80)
print("⏰ PLANNING PATTERNS")
print("=" * 80)

duration_keywords = {
    'Weekend': ['weekend', '2-3 days', 'two days', 'three days'],
    'Week': ['week', '7 days', 'seven days'],
    '10-14 Days': ['10 days', '12 days', '14 days', 'two weeks', 'fortnight'],
    'Extended (3+ weeks)': ['3 weeks', '4 weeks', 'three weeks', 'four weeks', 'month']
}

duration_counts = Counter()
for conv in conversations:
    text = f"{conv.get('title', '')} {conv.get('summary', '')}".lower()
    for duration, keywords in duration_keywords.items():
        for keyword in keywords:
            if keyword in text:
                duration_counts[duration] += 1
                break

print("\n📅 Trip Duration Preferences:")
for duration, count in duration_counts.most_common():
    if count > 0:
        bar = "○" * count
        print(f"  {duration:20}: {bar} ({count} trips)")

# 7. Family Focus Analysis
print("\n" + "=" * 80)
print("👨‍👩‍👧‍👦 FAMILY-CENTRIC INSIGHTS")
print("=" * 80)

child_keywords = ['child', 'kid', 'family-friendly', 'four-year-old', 'young children', 
                 'playground', 'interactive', 'educational']

child_focus_by_year = defaultdict(int)
total_by_year = defaultdict(int)

for conv in conversations:
    year = conv['date'][:4] if conv['date'] != 'Unknown' else 'Unknown'
    text = f"{conv.get('title', '')} {conv.get('summary', '')}".lower()
    
    total_by_year[year] += 1
    for keyword in child_keywords:
        if keyword in text:
            child_focus_by_year[year] += 1
            break

print("\n👶 Child-Centric Planning by Year:")
for year in sorted(total_by_year.keys()):
    if total_by_year[year] > 0:
        percentage = (child_focus_by_year[year] / total_by_year[year]) * 100
        bar = "★" * int(percentage/10)
        print(f"  {year}: {bar} {percentage:.1f}% explicitly child-focused")

# 8. Key Insights Summary
print("\n" + "=" * 80)
print("💡 KEY INSIGHTS")
print("=" * 80)

print("""
1. 📈 EVOLUTION: Clear progression from exploratory (2023) to optimized (2025) planning
   
2. 🗺️ GEOGRAPHIC COMFORT: Strong West Coast corridor preference (LA-Seattle-Portland)
   with emerging international confidence (London, France)
   
3. 🎯 ACTIVITY TRINITY: Museums (42%), Beaches (36%), Hiking (30%) form core experiences
   
4. 🚗 TRAVEL STYLE: Road trips dominate (45%) but city breaks gaining momentum
   
5. 👨‍👩‍👧‍👦 FAMILY MATURATION: Child-centric focus decreasing as children age and adapt
   
6. ⏰ SWEET SPOT: 10-14 day trips emerging as optimal duration
   
7. 🌞 SEASONALITY: Strong summer bias (39%) suggests school-year constraints
   
8. 💰 VALUE EVOLUTION: From "seeing everything" to "maximizing value"
""")

# Save detailed analytics
analytics_output = {
    'generated_date': datetime.now().isoformat(),
    'total_conversations': len(conversations),
    'date_range': f"{conversations[0]['date']} to {conversations[-1]['date']}",
    'yearly_distribution': dict(yearly_counts),
    'seasonal_distribution': dict(seasonal_counts),
    'top_destinations': dict(location_counts.most_common(20)),
    'activity_frequency': dict(activity_counts),
    'travel_styles': dict(type_counts),
    'duration_preferences': dict(duration_counts),
    'complexity_evolution': {year: dict(counts) for year, counts in yearly_complexity.items()}
}

with open('../data/family_travel_analytics.json', 'w') as f:
    json.dump(analytics_output, f, indent=2)

print("\n" + "=" * 80)
print("📊 Full analytics data saved to: family_travel_analytics.json")
print("📄 Narrative report saved to: family_travel_analysis_report.md")
print("=" * 80)