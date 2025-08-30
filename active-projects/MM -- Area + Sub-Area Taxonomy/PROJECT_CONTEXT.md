# MM Taxonomy Project Context & Breadcrumbs

## Project Evolution

### v1.3.0 Updates (August 30, 2025)
- **Branch**: `new-model-updates` 
- **Key Change**: Separated talent outreach from concept vetting
- **New Sub-Area**: CP-ORIG (Creative Origination & Vetting)
- **Phase Rename**: DISCOVER → "Origin" (ID unchanged for stability)
- **Gate Update**: G_ORIGIN_APPROVED replaces G_DEV_APPROVED

### Background
This project started as CSV exports from Notion and evolved into a canonical GitHub-based taxonomy with automated Notion sync capability. The goal is to maintain Modern Magic's 8-area organizational structure as the single source of truth while keeping Notion databases current.

## Architecture Philosophy

### Areas (8 Canonical)
- **Stable IDs**: Never change (e.g., `CREATIVE_PROJECTS`)
- **Flexible Names**: Can evolve (e.g., "Creative Projects")  
- **Codes**: Short identifiers for analytics (`CP`)
- **Ownership**: Each area owns specific lifecycle phases

### Sub-Areas (16 Operational)
- **Scope Definition**: Clear `owns` and `exclusions` boundaries
- **Parent Mapping**: Links to canonical areas
- **DRI Assignments**: Specific lifecycle phase ownership
- **Operational Focus**: Day-to-day responsibility areas

### Phases (5 Lifecycle)
- **Sequential Gates**: Clear progression from Origin → Release
- **DRI Model**: Single owner with defined partners
- **Evidence Requirements**: Specific deliverables for gate passage
- **Stable IDs**: Phase evolution tracked without breaking integrations

## Current Status

### Implementation
- ✅ YAML schemas defined (areas, sub_areas, phases)
- ✅ Context documentation complete
- ✅ Git branch structure organized
- ⏳ Notion sync configuration pending
- ⏳ GitHub Actions workflow pending

### Next Actions
1. **Configure Notion Integration**
   - Create Notion integration token
   - Share target databases with integration
   - Update `mapping/notion_mapping.yaml` with database IDs

2. **Deploy v1.3.0**
   - Test sync with `python scripts/sync_notion.py`
   - Set up GitHub Actions for automated sync
   - Validate Notion select options update correctly

3. **Migration Planning**
   - Map existing Pillars DB entries to new Areas
   - Separate personal vs. Modern Magic pillars using Pillar Group field
   - Create relation fields linking to canonical taxonomy

## Key Design Decisions

### Why GitHub as Canonical Source
- **Version Control**: PR-gated changes with diff visibility
- **Stability**: Immutable IDs with flexible presentation
- **Automation**: GitHub Actions sync to keep Notion current
- **Collaboration**: Team review process for taxonomy changes

### Why Separate Phases from Areas
- **Clarity**: Areas = organizational buckets, Phases = temporal workflow
- **DRI Model**: Clear ownership at each lifecycle stage
- **Flexibility**: Phase evolution without disrupting area structure
- **Reporting**: Better project lifecycle tracking and analytics

### Why Sub-Areas Matter
- **Operational Clarity**: Day-to-day responsibility boundaries
- **Exclusion Boundaries**: Prevents overlap and confusion
- **Scalability**: Detailed scope without area proliferation
- **Integration**: Maps to existing Notion workflows and team structure

---
*This context file replaces project breadcrume file.rtf with cleaner markdown format*