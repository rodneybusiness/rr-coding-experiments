#!/usr/bin/env python3
"""
Roam Knowledge Ontology Builder - Enhanced for 10,000 pages
Analyzes your top pages to create a structured MOC/Index with automated categorization
"""

import re
from collections import defaultdict, Counter
import json
import os

def load_top_pages(filename='roam_links_top10000.txt'):
    """Load the top pages from the file"""
    pages = []
    print("Loading pages...")
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()[3:]  # Skip header
        for i, line in enumerate(lines):
            if i % 1000 == 0:
                print(f"  Loaded {i} pages...")
            if line.strip():
                match = re.match(r'(\d+)\.\s+(.+?)\s+\((\d+)\s+links\)', line.strip())
                if match:
                    rank, title, count = match.groups()
                    pages.append({
                        'rank': int(rank),
                        'title': title,
                        'links': int(count)
                    })
    return pages

def advanced_categorize_pages(pages):
    """Advanced categorization with pattern matching and keyword analysis"""
    categories = defaultdict(list)
    
    # Define sophisticated patterns for categorization
    patterns = {
        'Daily Pages': [
            r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d+',
            r'^\d{2}-\d{2}-\d{4}$'
        ],
        'Projects': [
            r'\(Project\)',
            r'Project/',
            r'^Project\s',
            r'\sProject$'
        ],
        'People': [
            r'^[A-Z][a-z]+\s+[A-Z][a-z]+$',  # First Last
            r'^[A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+$',  # First M. Last
            r'^Dr\.\s+[A-Z][a-z]+',
            r'^Prof\.\s+[A-Z][a-z]+'
        ],
        'Companies & Organizations': [
            r'\b(Inc|LLC|Ltd|Corp|Company|Studios?|Films?|Pictures|Entertainment|Productions?|Agency|Group)\b',
            r'^[A-Z]{2,}(\s+[A-Z]{2,})*$'  # All caps abbreviations
        ],
        'Tools & Systems': [
            r'^roam/',
            r'SmartBlock',
            r'Template',
            r'\bAPI\b',
            r'\bPlugin\b',
            r'\bExtension\b',
            r'\bScript\b'
        ],
        'Literature & Media': [
            r'\(highlights\)',
            r'\(Book\)',
            r'\(Article\)',
            r'\(Paper\)',
            r'\(Film\)',
            r'\(Movie\)',
            r'\(Series\)',
            r'\(Podcast\)',
            r'^Book:',
            r'^Article:',
            r'^Film:',
            r'^Podcast:'
        ],
        'Tasks & Workflow': [
            r'\bTODO\b',
            r'\bDONE\b',
            r'\bTask\b',
            r'\bWorkflow\b',
            r'\bChecklist\b',
            r'\bInbox\b',
            r'^#waiting',
            r'^#blocked'
        ],
        'Meeting & Events': [
            r'\bMeeting\b',
            r'\bCall\b',
            r'\bEvent\b',
            r'\bConference\b',
            r'\bWorkshop\b',
            r'\bWebinar\b',
            r'\b1:1\b',
            r'\bSync\b'
        ],
        'Writing & Creative': [
            r'\bStory\b',
            r'\bScript\b',
            r'\bDraft\b',
            r'\bOutline\b',
            r'\bCharacter\b',
            r'\bPlot\b',
            r'\bScene\b',
            r'\bDialogue\b',
            r'\bNarrative\b'
        ],
        'Research & Learning': [
            r'\bResearch\b',
            r'\bStudy\b',
            r'\bAnalysis\b',
            r'\bHypothesis\b',
            r'\bExperiment\b',
            r'\bFindings\b',
            r'\bData\b',
            r'\bEvidence\b'
        ],
        'Ideas & Concepts': [
            r'^#[A-Za-z]',  # Tags
            r'\bIdea\b',
            r'\bConcept\b',
            r'\bTheory\b',
            r'\bPrinciple\b',
            r'\bFramework\b',
            r'\bModel\b'
        ],
        'Questions & Problems': [
            r'\?$',  # Ends with question mark
            r'^Question:',
            r'^Q:',
            r'\bProblem\b',
            r'\bIssue\b',
            r'\bChallenge\b',
            r'^How\s',
            r'^What\s',
            r'^Why\s',
            r'^When\s'
        ],
        'Goals & Planning': [
            r'\bGoal\b',
            r'\bPlan\b',
            r'\bStrategy\b',
            r'\bRoadmap\b',
            r'\bMilestone\b',
            r'\bObjective\b',
            r'\bTarget\b',
            r'\bVision\b'
        ],
        'Reviews & Retrospectives': [
            r'\bReview\b',
            r'\bRetrospective\b',
            r'\bReflection\b',
            r'\bSummary\b',
            r'\bRecap\b',
            r'\bLessons\s+Learned\b',
            r'Weekly\s+Review',
            r'Monthly\s+Review'
        ],
        'Technical & Development': [
            r'\bCode\b',
            r'\bProgramming\b',
            r'\bDevelopment\b',
            r'\bTechnical\b',
            r'\bEngineering\b',
            r'\bSoftware\b',
            r'\bHardware\b',
            r'\bAlgorithm\b',
            r'\bDatabase\b'
        ],
        'Finance & Business': [
            r'\bBudget\b',
            r'\bFinance\b',
            r'\bRevenue\b',
            r'\bProfit\b',
            r'\bInvestment\b',
            r'\bFunding\b',
            r'\bBusiness\b',
            r'\bMarket\b',
            r'\bSales\b'
        ],
        'Health & Wellness': [
            r'\bHealth\b',
            r'\bWellness\b',
            r'\bExercise\b',
            r'\bMeditation\b',
            r'\bSleep\b',
            r'\bNutrition\b',
            r'\bMental\s+Health\b',
            r'\bTherapy\b'
        ],
        'Relationships & Social': [
            r'\bRelationship\b',
            r'\bFamily\b',
            r'\bFriend\b',
            r'\bPartner\b',
            r'\bTeam\b',
            r'\bCommunity\b',
            r'\bNetwork\b',
            r'\bCollaboration\b'
        ]
    }
    
    # Process each page
    uncategorized = []
    for i, page in enumerate(pages):
        if i % 1000 == 0:
            print(f"  Categorizing page {i}...")
            
        title = page['title']
        categorized = False
        
        # Check against all patterns
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, title, re.IGNORECASE):
                    categories[category].append(page)
                    categorized = True
                    break
            if categorized:
                break
        
        # If not categorized, add to uncategorized for second pass
        if not categorized:
            uncategorized.append(page)
    
    # Second pass for uncategorized pages - use word analysis
    for page in uncategorized:
        title = page['title']
        words = title.lower().split()
        
        # Default categories based on common patterns
        if len(words) == 1:
            categories['Single Word Concepts'].append(page)
        elif len(words) == 2:
            categories['Topics & Ideas'].append(page)
        elif any(word in ['the', 'of', 'and', 'in', 'on', 'at', 'for'] for word in words):
            categories['Articles & Resources'].append(page)
        else:
            categories['General Topics'].append(page)
    
    return categories

def analyze_category_patterns(categories):
    """Analyze patterns within categories to create sub-groupings"""
    patterns = {}
    
    for category, pages in categories.items():
        if len(pages) > 20:  # Only analyze categories with significant pages
            # Extract common words
            word_freq = Counter()
            for page in pages[:100]:  # Sample first 100
                words = re.findall(r'\b[A-Za-z]{3,}\b', page['title'].lower())
                word_freq.update(words)
            
            # Find most common meaningful words
            common_words = [word for word, count in word_freq.most_common(20) 
                          if word not in ['the', 'and', 'for', 'with', 'from', 'that', 'this', 'have', 'been']]
            
            patterns[category] = {
                'total': len(pages),
                'common_words': common_words[:10],
                'top_pages': pages[:20]
            }
    
    return patterns

def generate_smart_block_categorizer():
    """Generate SmartBlock code for automated categorization"""
    
    smartblock = """```javascript
// Roam Ontology Auto-Categorizer SmartBlock
// Run this on any page to suggest its category

var pageTitle = roam42.common.currentPageName();
var suggestedCategories = [];

// Pattern matching for categories
var patterns = {
    'Daily Pages': [/^(January|February|March|April|May|June|July|August|September|October|November|December)\\s+\\d+/],
    'Projects': [/\\(Project\\)/, /Project\\//, /^Project\\s/, /\\sProject$/],
    'People': [/^[A-Z][a-z]+\\s+[A-Z][a-z]+$/],
    'Companies': [/\\b(Inc|LLC|Ltd|Corp|Company|Studios?)\\b/],
    'Literature': [/\\(highlights\\)/, /\\(Book\\)/, /^Book:/, /^Article:/],
    'Tasks': [/\\bTODO\\b/, /\\bDONE\\b/, /\\bTask\\b/],
    'Writing': [/\\bStory\\b/, /\\bScript\\b/, /\\bDraft\\b/, /\\bCharacter\\b/],
    'Ideas': [/^#/, /\\bIdea\\b/, /\\bConcept\\b/],
    'Questions': [/\\?$/, /^Question:/, /^How\\s/, /^What\\s/, /^Why\\s/]
};

// Check patterns
for (var category in patterns) {
    for (var i = 0; i < patterns[category].length; i++) {
        if (patterns[category][i].test(pageTitle)) {
            suggestedCategories.push(category);
            break;
        }
    }
}

// Create categorization block
var output = "**Suggested Categories:**\\n";
if (suggestedCategories.length > 0) {
    suggestedCategories.forEach(function(cat) {
        output += "- [[Ontology/" + cat + "]]\\n";
    });
} else {
    output += "- [[Ontology/General Topics]]\\n";
}

output += "\\n**Add to Master Index:**\\n";
output += "- {{[[TODO]]}} Add [[" + pageTitle + "]] to [[Master Index]]\\n";
output += "\\n**Related Pages:** (add relevant links here)\\n- \\n";

return output;
```
"""
    return smartblock

def generate_batch_processor():
    """Generate a tool to process multiple pages at once"""
    
    processor = """# Batch Page Processor for Ontology

## How to Use:
1. Copy the list of pages you want to categorize
2. Run the Python script below
3. It will output Roam-formatted links organized by category

```python
#!/usr/bin/env python3
import re

def categorize_page_list(page_list):
    '''Categorize a list of page titles'''
    
    categories = {
        'Daily Pages': [],
        'Projects': [],
        'People': [],
        'Companies': [],
        'Literature': [],
        'Tasks': [],
        'Writing': [],
        'Ideas': [],
        'Questions': [],
        'Other': []
    }
    
    patterns = {
        'Daily Pages': [r'^(January|February|March|April|May|June|July|August|September|October|November|December)\\s+\\d+'],
        'Projects': [r'\\(Project\\)', r'Project/'],
        'People': [r'^[A-Z][a-z]+\\s+[A-Z][a-z]+$'],
        'Companies': [r'\\b(Inc|LLC|Ltd|Corp|Company|Studios?)\\b'],
        'Literature': [r'\\(highlights\\)', r'\\(Book\\)', r'^Book:'],
        'Tasks': [r'\\bTODO\\b', r'\\bDONE\\b'],
        'Writing': [r'\\bStory\\b', r'\\bScript\\b', r'\\bDraft\\b'],
        'Ideas': [r'^#', r'\\bIdea\\b', r'\\bConcept\\b'],
        'Questions': [r'\\?$', r'^Question:', r'^How\\s', r'^What\\s']
    }
    
    for page in page_list:
        page = page.strip()
        if not page:
            continue
            
        categorized = False
        for cat, pats in patterns.items():
            for pat in pats:
                if re.search(pat, page, re.IGNORECASE):
                    categories[cat].append(page)
                    categorized = True
                    break
            if categorized:
                break
        
        if not categorized:
            categories['Other'].append(page)
    
    # Output Roam-formatted results
    output = []
    for cat, pages in categories.items():
        if pages:
            output.append(f"## {cat}")
            for page in pages:
                output.append(f"- [[{page}]]")
            output.append("")
    
    return "\\n".join(output)

# Example usage:
if __name__ == "__main__":
    # Paste your page list here
    pages = '''
    Ludo (Project)
    Adam Rosenberg
    March 22nd, 2021
    TODO
    Story Development Ideas
    '''.strip().split('\\n')
    
    print(categorize_page_list(pages))
```
"""
    return processor

def generate_enhanced_moc_template(categories, patterns):
    """Generate an enhanced MOC template based on 10,000 page analysis"""
    
    template = """# 🏛️ Master Knowledge Ontology
> *A comprehensive map of {total_pages:,} pages, organized for maximum discoverability*

---

## 🚀 Quick Navigation

### 📍 Primary Hubs
- [[📊 Dashboard]] | [[📝 Active Work]] | [[🎯 Current Focus]]
- [[❓ Open Questions]] | [[💡 Ideas Inbox]] | [[🔍 Research Queue]]

### ⏰ Temporal Navigation  
- [[Today]] | [[This Week]] | [[This Month]] | [[This Quarter]]
- [[2025]] | [[2024]] | [[2023]] | [[Archive]]

### 🏷️ By Status
- [[🟢 Active]] | [[🟡 On Hold]] | [[🔴 Blocked]] | [[✅ Complete]]

---

## 🗂️ Knowledge Architecture

"""
    
    # Sort categories by size
    sorted_cats = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)
    
    # Group into major sections
    major_sections = {
        "🚀 Action & Execution": [
            "Tasks & Workflow", "Projects", "Goals & Planning", 
            "Meeting & Events", "Reviews & Retrospectives"
        ],
        "👥 People & Networks": [
            "People", "Companies & Organizations", "Relationships & Social"
        ],
        "💡 Knowledge & Creation": [
            "Ideas & Concepts", "Writing & Creative", "Research & Learning",
            "Questions & Problems", "Technical & Development"
        ],
        "📚 Resources & References": [
            "Literature & Media", "Articles & Resources", "Tools & Systems"
        ],
        "📅 Time-Based": [
            "Daily Pages"
        ],
        "🏷️ Topics & Categories": [
            "Finance & Business", "Health & Wellness", "Topics & Ideas",
            "General Topics", "Single Word Concepts"
        ]
    }
    
    # Add categorized content
    for section, included_cats in major_sections.items():
        template += f"### {section}\n\n"
        
        for cat_name in included_cats:
            if cat_name in categories and categories[cat_name]:
                pages = categories[cat_name]
                template += f"#### [[Ontology/{cat_name}]] ({len(pages):,} pages)\n"
                
                # Add top 10 pages
                for page in pages[:10]:
                    template += f"- [[{page['title']}]] ({page['links']} links)\n"
                
                if len(pages) > 10:
                    template += f"- *... and {len(pages)-10:,} more pages*\n"
                template += "\n"
        
        template += "---\n\n"
    
    # Add uncategorized section
    uncategorized_count = sum(1 for cat, pages in categories.items() 
                            if cat not in sum(major_sections.values(), []))
    
    if uncategorized_count > 0:
        template += f"### 🔍 Other Categories ({uncategorized_count} types)\n\n"
        for cat, pages in sorted_cats:
            if cat not in sum(major_sections.values(), []) and len(pages) > 5:
                template += f"- [[Ontology/{cat}]] ({len(pages)} pages)\n"
        template += "\n---\n\n"
    
    # Add maintenance section
    template += """## 🛠️ Ontology Maintenance

### Daily Tasks (2 min)
- {{[[TODO]]}} Tag new pages with category: `#[[Ontology/Category]]`
- {{[[TODO]]}} Link important pages to relevant hubs
- {{[[TODO]]}} Check [[Uncategorized Pages]]

### Weekly Tasks (15 min)  
- {{[[TODO]]}} Review and categorize [[Recent Pages]]
- {{[[TODO]]}} Update category pages with new entries
- {{[[TODO]]}} Merge duplicate categories

### Monthly Tasks (30 min)
- {{[[TODO]]}} Audit category sizes and split if > 500 pages
- {{[[TODO]]}} Create new domain hubs as needed
- {{[[TODO]]}} Archive inactive projects

---

## 📊 Ontology Statistics

- **Total Pages**: {total_pages:,}
- **Categorized**: {categorized:,}
- **Categories**: {num_categories}
- **Avg Pages/Category**: {avg_per_cat:.0f}
- **Largest Category**: {largest_cat} ({largest_size:,} pages)

---

## 🔧 Automation Tools

### Quick Categorization
- [[SmartBlock: Auto-Categorize Page]]
- [[SmartBlock: Batch Process Pages]]
- [[SmartBlock: Weekly Ontology Review]]

### Queries for Discovery
```
{{[[query]]: {and: [[Ontology/Projects]] [[Active]]}}}
{{[[query]]: {and: [[Question]] {not: [[Answered]]}}}}
{{[[query]]: {and: [[Idea]] {created-after: -7}}}}}
```

---

*Generated from top 10,000 pages | Last updated: {{[[date]]}}}*
"""
    
    # Calculate statistics
    total_pages = sum(len(pages) for pages in categories.values())
    largest_cat = max(categories.items(), key=lambda x: len(x[1]))
    
    template = template.format(
        total_pages=10000,
        categorized=total_pages,
        num_categories=len(categories),
        avg_per_cat=total_pages/len(categories) if categories else 0,
        largest_cat=largest_cat[0],
        largest_size=len(largest_cat[1])
    )
    
    return template

def save_enhanced_results(categories, patterns, template, smartblock, processor):
    """Save all enhanced analysis results"""
    
    # Create output directory
    output_dir = "ontology_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save categorized pages (full detail)
    with open(f'{output_dir}/full_categorization.json', 'w', encoding='utf-8') as f:
        cat_data = {}
        for cat, pages in categories.items():
            cat_data[cat] = {
                'count': len(pages),
                'pages': [{'title': p['title'], 'links': p['links']} for p in pages[:500]]  # First 500 per category
            }
        json.dump(cat_data, f, indent=2)
    
    # Save category summaries
    with open(f'{output_dir}/category_summary.txt', 'w', encoding='utf-8') as f:
        f.write("Category Summary (from 10,000 pages)\n")
        f.write("=" * 60 + "\n\n")
        for cat, pages in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
            f.write(f"{cat}: {len(pages):,} pages\n")
            f.write(f"  Top 5: {', '.join([p['title'] for p in pages[:5]])}\n\n")
    
    # Save MOC template
    with open(f'{output_dir}/master_ontology_template.md', 'w', encoding='utf-8') as f:
        f.write(template)
    
    # Save SmartBlock
    with open(f'{output_dir}/auto_categorizer_smartblock.md', 'w', encoding='utf-8') as f:
        f.write("# Auto-Categorizer SmartBlock\n\n")
        f.write("Copy this code into a new SmartBlock:\n\n")
        f.write(smartblock)
    
    # Save batch processor
    with open(f'{output_dir}/batch_processor.md', 'w', encoding='utf-8') as f:
        f.write(processor)
    
    # Save implementation guide
    with open(f'{output_dir}/implementation_guide.md', 'w', encoding='utf-8') as f:
        f.write(create_detailed_implementation_guide())
    
    print(f"\n✅ Analysis complete! All files saved to '{output_dir}/' folder:")
    print("- full_categorization.json (detailed categorization)")
    print("- category_summary.txt (overview of all categories)")
    print("- master_ontology_template.md (your MOC template)")
    print("- auto_categorizer_smartblock.md (automation tool)")
    print("- batch_processor.md (bulk categorization tool)")
    print("- implementation_guide.md (step-by-step guide)")

def create_detailed_implementation_guide():
    """Create a detailed implementation guide"""
    
    guide = """# Complete Ontology Implementation Guide

## Phase 1: Initial Setup (30 minutes)

### 1. Create Master Index Page
1. Create new page: "Master Knowledge Ontology" or "🏛️ Master Index"
2. Copy entire template from `master_ontology_template.md`
3. Pin to shortcuts (click star icon)

### 2. Create Category Pages
For each major category in your template:
1. Create page: "Ontology/[Category Name]"
2. Add basic structure:
   ```
   # Ontology/Projects
   
   > All project-related pages
   
   ## Active Projects
   - [[Project 1]]
   - [[Project 2]]
   
   ## On Hold
   - [[Project 3]]
   
   ## Completed
   - [[Project 4]]
   ```

### 3. Install SmartBlocks
1. Go to roam/js/smartblocks page
2. Create new SmartBlock: "Auto-Categorize Page"
3. Copy code from `auto_categorizer_smartblock.md`
4. Set trigger: ;;categorize

## Phase 2: Bulk Population (1-2 hours)

### Method 1: Batch Processing (Fastest)
1. Open `full_categorization.json`
2. For each category with 50+ pages:
   - Copy the page titles
   - Use the batch processor script
   - Paste results into category page

### Method 2: Query-Based Population
Add these queries to category pages:

```
{{[[query]]: {and: [[TODO]] [[Project]]}}}
{{[[query]]: {and: [[Person]] {not: [[Company]]}}}}
{{[[query]]: {and: {between: [[January 1st, 2025]] [[today]]} [[Meeting]]}}}
```

### Method 3: Manual Review (Most Accurate)
1. Open `category_summary.txt`
2. Review top pages in each category
3. Manually add most important ones
4. Use SmartBlock for new pages

## Phase 3: Automation Setup (30 minutes)

### Daily Automation
1. Create template: "Daily Ontology Check"
   ```
   - [ ] Run ;;categorize on new pages
   - [ ] Link important pages to hubs
   - [ ] Update [[Current Focus]]
   ```

2. Add to Daily Template:
   ```
   {{[[embed]]: [[Daily Ontology Check]]}}
   ```

### Weekly Automation
Create "Weekly Ontology Review" page:
```
## Uncategorized Pages
{{[[query]]: {and: {not: [[Ontology]]} {created-after: -7}}}}

## New Questions
{{[[query]]: {and: [[Question]] {created-after: -7}}}}

## New Ideas
{{[[query]]: {and: [[Idea]] {created-after: -7}}}}
```

## Phase 4: Advanced Features (Optional)

### 1. Visual Ontology Map
Create visual representation using Roam's diagram feature:
```
{{diagram}}
- Master Index
  - Projects
    - Active
    - Archive
  - People
    - Team
    - External
  - Knowledge
    - Concepts
    - Research
```

### 2. Cross-References
Add "See Also" sections to major pages:
```
---
See Also: [[Related Page 1]] | [[Related Page 2]] | [[Parent Category]]
```

### 3. Metadata System
Add consistent metadata to pages:
```
Type:: [[Project]]
Status:: [[Active]]
Category:: [[Ontology/Projects]]
Created:: [[January 1st, 2025]]
```

## Best Practices

### 1. Naming Conventions
- Categories: "Ontology/Category Name"
- Hubs: "Hub: Domain Name"
- Indexes: "Index: Topic"

### 2. Linking Patterns
- Every page should link to at least one category
- Categories link up to Master Index
- Cross-link related categories

### 3. Maintenance Rhythm
- Daily: 2 min quick categorization
- Weekly: 15 min review and cleanup
- Monthly: 30 min structural improvements

## Troubleshooting

### Problem: Too many pages in a category
**Solution**: Create subcategories
- Split "Projects" → "Creative Projects", "Technical Projects"
- Use queries to auto-populate

### Problem: Pages fit multiple categories
**Solution**: Use primary + secondary categories
```
Category:: [[Ontology/Projects]]
Also:: [[Ontology/Research]], [[Ontology/Writing]]
```

### Problem: Ontology feels rigid
**Solution**: Add discovery mechanisms
- Random page queries
- "Similar to this" sections
- Trail guides between related topics

## Quick Wins

1. **Start with top 100 pages** - Don't try to categorize everything at once
2. **Use queries liberally** - Let Roam do the work
3. **Iterate weekly** - Your ontology should evolve
4. **Focus on findability** - Multiple paths to same information
5. **Keep it simple** - Better to have 20 used categories than 100 unused ones

Remember: The goal is to make your knowledge more accessible, not to create perfect categories!
"""
    
    return guide

def main():
    print("🔍 Analyzing 10,000 pages for comprehensive ontology...")
    
    # Check if file exists
    if not os.path.exists('roam_links_top10000.txt'):
        print("❌ Error: roam_links_top10000.txt not found!")
        print("Please run: python3 get_top_10000.py first")
        return
    
    # Load pages
    pages = load_top_pages()
    print(f"✅ Loaded {len(pages):,} pages")
    
    # Advanced categorization
    print("🏷️ Running advanced categorization...")
    categories = advanced_categorize_pages(pages)
    
    # Analyze patterns
    print("🔬 Analyzing category patterns...")
    patterns = analyze_category_patterns(categories)
    
    # Generate outputs
    print("📝 Generating ontology templates...")
    template = generate_enhanced_moc_template(categories, patterns)
    smartblock = generate_smart_block_categorizer()
    processor = generate_batch_processor()
    
    # Save everything
    save_enhanced_results(categories, patterns, template, smartblock, processor)
    
    # Print summary
    print("\n📊 Analysis Summary:")
    print(f"- Total pages analyzed: {len(pages):,}")
    print(f"- Categories created: {len(categories)}")
    print(f"- Largest category: {max(categories.items(), key=lambda x: len(x[1]))[0]}")
    print(f"- Average pages per category: {sum(len(p) for p in categories.values()) / len(categories):.0f}")
    
    print("\n🎯 Next Steps:")
    print("1. Open 'ontology_output/implementation_guide.md' for detailed instructions")
    print("2. Copy 'ontology_output/master_ontology_template.md' to create your Master Index")
    print("3. Use 'ontology_output/auto_categorizer_smartblock.md' for automation")
    print("4. Check 'ontology_output/full_categorization.json' to see how your pages were categorized")

if __name__ == "__main__":
    main()
