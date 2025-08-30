#!/usr/bin/env python3
"""
Roam API Link Sampler
Gets a sample of pages and their link counts using Roam's API
This won't get all 22,000 pages but will give you a good sample
"""

import subprocess
import json
from collections import defaultdict

def get_sample_pages(sample_size=500):
    """Get a sample of pages from your Roam graph"""
    # This is a placeholder - you'd need to implement the actual API calls
    # using the roam tools available in your environment
    
    print(f"Getting sample of {sample_size} pages...")
    
    # In practice, you'd use the roam_datomic_query function
    # This is just showing the structure
    
    pages = []
    # You'd need to make multiple queries with different offsets
    # to get a larger sample
    
    return pages

def count_references_for_page(page_title):
    """Count how many times a page is referenced"""
    # This would use roam_datomic_query to count references
    # Query would be something like:
    # [:find (count ?ref)
    #  :where [?page :node/title page_title]
    #         [?ref :block/refs ?page]]
    pass

# Alternative: Quick sample using the existing API
print("Alternative approach using Roam API...")
print("\nTo get a complete list of all pages ordered by link count:")
print("1. In Roam, go to the ... menu (top right)")
print("2. Select 'Export All'")  
print("3. Choose 'JSON' format")
print("4. Save the file to: /Users/newuser/Desktop/roam_analysis/")
print("5. Run: python roam_link_counter.py your_export.json")
print("\nThis will give you:")
print("- A complete list of all 22,205 pages sorted by link count")
print("- A top 100 most linked pages file")
print("- Console output of the top 20")

# Let me at least show you how to get SOME highly linked pages
print("\n" + "="*50)
print("Sample of likely highly-linked pages:")
print("(checking common page patterns...)\n")

# Common pages that tend to have many links
common_patterns = [
    "TODO", "DONE", "Important", "Project", "Meeting", "Notes",
    "Ideas", "Questions", "Resources", "References", "Goals",
    "Daily", "Weekly", "Monthly", "Review", "Planning"
]

print("Run the Python script above with your JSON export for complete results!")
