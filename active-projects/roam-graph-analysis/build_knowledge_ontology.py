#!/usr/bin/env python3
"""
Roam Knowledge Ontology Builder
Analyzes your top pages to help create a structured MOC/Index
"""

import re
from collections import defaultdict
import json

def load_top_pages(filename='roam_links_top1000.txt'):
    """Load the top pages from the file"""
    pages = []
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()[3:]  # Skip header
        for line in lines:
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

def categorize_pages(pages):
    """Categorize pages based on patterns in their titles"""
    categories = defaultdict(list)
    
    for page in pages:
        title = page['title']
        
        # Date pages
        if re.match(r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d+', title):
            categories['Daily Pages'].append(page)
        
        # Project pages
        elif '(Project)' in title or 'Project/' in title:
            categories['Projects'].append(page)
        
        # People
        elif re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+$', title) or '[[' in title and ']]' in title:
            if not any(x in title for x in ['TODO', 'DONE', 'Project']):
                categories['People'].append(page)
        
        # System/Workflow pages
        elif any(x in title for x in ['TODO', 'DONE', 'roam/', 'SmartBlock', 'Template']):
            categories['System & Workflow'].append(page)
        
        # Literature/Media
        elif '(highlights)' in title or 'Book:' in title or 'Article:' in title:
            categories['Literature & Media'].append(page)
        
        # Hub/Index pages
        elif any(x in title for x in ['Hub', 'Index', 'MOC', 'Main']):
            categories['Existing Hubs'].append(page)
        
        # Tags/Concepts
        elif title.startswith('#') or len(title.split()) <= 2:
            categories['Concepts & Tags'].append(page)
        
        # Multi-word topics
        else:
            categories['Topics & Ideas'].append(page)
    
    return categories

def analyze_knowledge_domains(categories):
    """Analyze categories to identify main knowledge domains"""
    domains = {}
    
    # Count pages per category
    for cat, pages in categories.items():
        domains[cat] = {
            'count': len(pages),
            'top_pages': pages[:10],  # Top 10 in each category
            'total_links': sum(p['links'] for p in pages)
        }
    
    return domains

def generate_moc_structure(domains, categories):
    """Generate a suggested MOC structure"""
    
    structure = {
        "🧭 Navigation & Meta": {
            "description": "Core navigation and system pages",
            "sections": {
                "📊 Dashboards & Workflows": ["TODO", "Daily Pages", "Weekly Reviews"],
                "🔧 System & Tools": ["SmartBlocks", "Templates", "Roam Settings"],
                "🗺️ Existing Hubs": []
            }
        },
        "🎯 Active Projects": {
            "description": "Current projects and initiatives",
            "sections": {
                "🎬 Creative Projects": [],
                "💼 Professional Projects": [],
                "🔬 Research Projects": []
            }
        },
        "👥 People & Networks": {
            "description": "Contacts, collaborators, and relationships",
            "sections": {
                "🤝 Collaborators": [],
                "🏢 Companies & Organizations": [],
                "👨‍👩‍👧‍👦 Personal": []
            }
        },
        "💡 Knowledge & Ideas": {
            "description": "Core concepts, theories, and insights",
            "sections": {
                "🧠 Core Concepts": [],
                "🎨 Creative Ideas": [],
                "🔍 Research Topics": []
            }
        },
        "📚 Resources & References": {
            "description": "Books, articles, and external knowledge",
            "sections": {
                "📖 Books & Literature": [],
                "📰 Articles & Essays": [],
                "🎥 Media & Videos": []
            }
        },
        "🌟 Personal Development": {
            "description": "Growth, learning, and self-improvement",
            "sections": {
                "🎯 Goals & Aspirations": [],
                "📝 Reflections & Journals": [],
                "🧘 Habits & Practices": []
            }
        }
    }
    
    return structure

def create_roam_moc_template(structure, top_pages):
    """Create a Roam-formatted MOC template"""
    
    template = """# 🏛️ Master Index & Knowledge Ontology

> *A living map of my knowledge graph, organized for clarity and discovery*

---

## 🎯 Quick Access
- [[TODO]] | [[Today]] | [[Questions]] | [[Ideas]]
- [[Current Sprint]] | [[This Week]] | [[This Month]]

---

## 📊 Knowledge Architecture

"""
    
    # Add main sections
    for main_cat, details in structure.items():
        template += f"### {main_cat}\n"
        template += f"*{details['description']}*\n\n"
        
        for subsection, pages in details['sections'].items():
            template += f"- **{subsection}**\n"
            if pages:
                for page in pages[:5]:  # Limit to 5 per subsection
                    template += f"    - [[{page}]]\n"
            else:
                template += f"    - `Add relevant pages here`\n"
        template += "\n"
    
    template += """---

## 🔍 Discovery Paths

### By Domain
- [[🎬 Film & Animation]]
- [[💻 Technology & Innovation]]
- [[🎨 Creative Process]]
- [[🧠 Psychology & Philosophy]]
- [[💼 Business & Strategy]]

### By Time
- [[2025]] | [[2024]] | [[2023]]
- [[Quarterly Reviews]]
- [[Project Timeline]]

### By Type
- [[🎯 Active Projects]]
- [[💭 Explorations]]
- [[📚 Reading List]]
- [[✅ Completed]]

---

## 🌐 Meta-Organization

### Ontology Principles
- **Hierarchy**: Main categories → Subcategories → Individual pages
- **Cross-linking**: Every page should link to at least 2 others
- **Emergence**: Allow organic growth while maintaining structure
- **Regular Review**: Weekly cleanup and monthly restructure

### Maintenance Tasks
- {{[[TODO]]}} Weekly: Review and categorize new pages
- {{[[TODO]]}} Monthly: Refactor categories based on usage
- {{[[TODO]]}} Quarterly: Major ontology review

---

## 📈 Graph Analytics
- Total Pages: 22,205
- Total Links: `Run analysis`
- Most Connected: See [[Top 1000 Pages]]
- Orphan Pages: [[Unlinked Pages]]

---

*Last Updated: {{[[CURRENT_DATE]]}}}*
"""
    
    return template

def save_analysis_results(categories, domains, template):
    """Save all analysis results"""
    
    # Save categorized pages
    with open('roam_ontology_categories.json', 'w', encoding='utf-8') as f:
        cat_data = {}
        for cat, pages in categories.items():
            cat_data[cat] = [{'title': p['title'], 'links': p['links']} for p in pages[:50]]
        json.dump(cat_data, f, indent=2)
    
    # Save MOC template
    with open('roam_moc_template.md', 'w', encoding='utf-8') as f:
        f.write(template)
    
    # Save implementation guide
    with open('moc_implementation_guide.md', 'w', encoding='utf-8') as f:
        f.write(create_implementation_guide())
    
    print("✅ Analysis complete! Generated files:")
    print("- roam_ontology_categories.json (your pages categorized)")
    print("- roam_moc_template.md (your MOC template)")
    print("- moc_implementation_guide.md (step-by-step guide)")

def create_implementation_guide():
    """Create a step-by-step implementation guide"""
    
    guide = """# Implementing Your Knowledge Ontology in Roam

## Phase 1: Create the Master Index (15 minutes)

1. **Create a new page** called "Master Index" or "🏛️ Knowledge Ontology"
2. **Copy the template** from `roam_moc_template.md`
3. **Pin this page** to your shortcuts for easy access

## Phase 2: Populate Categories (45 minutes)

1. **Open** `roam_ontology_categories.json` 
2. **For each category**, add your top 10-20 pages to the appropriate sections
3. **Create new category pages** as needed (e.g., [[Film Projects]], [[People]])

## Phase 3: Create Domain Hubs (30 minutes)

Based on your top pages, create these domain-specific hubs:

1. **[[🎬 Film & Animation Hub]]**
   - Ludo (Project)
   - Modern Magic
   - Animation Techniques
   - Collaborators

2. **[[📝 Writing & Creative Hub]]**
   - Story Development
   - Scriptwriting
   - Character Development
   - World Building

3. **[[🧠 Knowledge Management Hub]]**
   - Zettelkasten
   - Roam Techniques
   - Learning Systems
   - Information Architecture

4. **[[👥 People & Network Hub]]**
   - Collaborators
   - Mentors
   - Industry Contacts
   - Personal Relationships

## Phase 4: Establish Linking Patterns (20 minutes)

1. **Bidirectional Links**: Ensure all pages link back to their parent hub
2. **Cross-Domain Links**: Connect related concepts across domains
3. **Trail Guides**: Create "See also:" sections on key pages

## Phase 5: Create Navigation Flows

### Daily Flow
- Start at Master Index
- Check [[TODO]] and [[Today]]
- Navigate to active project hub
- Drill down to specific work

### Weekly Review Flow
- Master Index → [[Weekly Review Template]]
- Check each domain hub for updates
- Reorganize as needed

### Discovery Flow
- Use [[Questions]] and [[Open Loops]]
- Follow "See also" trails
- Use block references to connect ideas

## Phase 6: Maintenance Systems

### Daily (2 minutes)
- Tag new pages with domain markers
- Link to relevant hubs

### Weekly (15 minutes)
- Review uncategorized pages
- Update domain hubs
- Clean up orphan pages

### Monthly (30 minutes)
- Refactor categories
- Create new hubs as needed
- Archive inactive projects

## Best Practices for 2025+ Knowledge Management

1. **AI-Ready Structure**
   - Clear hierarchies for LLM navigation
   - Semantic categorization
   - Rich metadata

2. **Emergent Organization**
   - Let patterns emerge from usage
   - Regular refactoring
   - Flexible categories

3. **Connection Over Collection**
   - Prioritize linking over capturing
   - Build knowledge trails
   - Create multiple paths to information

4. **Active vs Archive**
   - Clear separation of current/historical
   - Regular archiving process
   - Easy retrieval system

## Quick Start Checklist

- [ ] Create Master Index page
- [ ] Copy template structure
- [ ] Add top 20 pages to each category
- [ ] Create 4 domain hubs
- [ ] Link domain hubs to Master Index
- [ ] Set up daily/weekly maintenance reminders
- [ ] Create your first "trail guide" between related topics

## Advanced Techniques

### Smart Blocks for Ontology
- Create templates for new pages that auto-link to hubs
- Build category assignment workflows
- Automate weekly reorganization

### Query-Driven Sections
- {{[[query]]: {and: [[Active]] [[Project]]}}}
- {{[[query]]: {and: [[Question]] {not: [[Answered]]}}}}
- {{[[query]]: {between: [[January 1st, 2025]] [[December 31st, 2025]]}}}

### Visual Mapping
- Use Roam's diagram feature for visual ontologies
- Create mind maps of domain relationships
- Build concept hierarchies

Remember: The best ontology is one you'll actually use. Start simple, iterate often!
"""
    
    return guide

def main():
    print("🔍 Analyzing your knowledge graph...")
    
    # Load top pages
    pages = load_top_pages()
    print(f"✅ Loaded {len(pages)} top pages")
    
    # Categorize pages
    categories = categorize_pages(pages)
    print(f"✅ Categorized into {len(categories)} groups")
    
    # Analyze domains
    domains = analyze_knowledge_domains(categories)
    
    # Print summary
    print("\n📊 Your Knowledge Domains:")
    for domain, info in sorted(domains.items(), key=lambda x: x[1]['total_links'], reverse=True):
        print(f"- {domain}: {info['count']} pages ({info['total_links']:,} total links)")
    
    # Generate MOC structure
    structure = generate_moc_structure(domains, categories)
    
    # Create template
    template = create_roam_moc_template(structure, pages[:100])
    
    # Save everything
    save_analysis_results(categories, domains, template)
    
    print("\n🎯 Next Steps:")
    print("1. Review 'moc_implementation_guide.md' for detailed instructions")
    print("2. Open 'roam_moc_template.md' to see your MOC structure")
    print("3. Check 'roam_ontology_categories.json' to see how your pages were categorized")

if __name__ == "__main__":
    main()
