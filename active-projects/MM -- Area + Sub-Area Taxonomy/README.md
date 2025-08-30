# Modern Magic Area + Sub-Area Taxonomy

**Canonical source for Modern Magic's 8-area organizational taxonomy with lifecycle phases and GitHub→Notion sync capability.**

## Current Version: v1.3.0 ✨

### Latest Updates (August 2025)
- **New Origin Phase**: Separated talent outreach from concept vetting
- **CP-ORIG Sub-Area**: Dedicated creative origination and vetting function
- **Phase DRI System**: Clear ownership assignments for each lifecycle stage
- **Gate Structure**: G_ORIGIN_APPROVED now controls entry into Development

## Structure

```
MM -- Area + Sub-Area Taxonomy/
├── README.md                           # This documentation
├── areas_v1.3.yaml                     # 8 canonical areas with codes & descriptions
├── phases_v1.3.yaml                    # Lifecycle phases with DRI assignments
├── sub_areas_v1.3.yaml                 # 16 sub-areas with scope definitions  
├── taxonomy_context_addendum_v1.3.md   # Change documentation
├── schema/                             # Legacy schema files
│   ├── areas.yaml                      # Previous areas definition
│   └── sub_areas-examples.yaml         # Sub-area examples
├── mapping/
│   └── notion_mapping.yaml             # Notion database integration config
├── scripts/
│   ├── validate.py                     # Schema validation
│   └── sync_notion.py                  # GitHub→Notion sync tool
├── data/                               # Source CSV exports
│   ├── mm_areas_subareas.csv           # Core areas/sub-areas data
│   ├── mm_areas_subareas_all.csv       # Complete export with metadata
│   ├── modern_magic_role_taxonomy_v3.1.csv  # Latest role classifications (763 roles)
│   ├── modern_magic_role_taxonomy_v3.0.csv  # Previous version
│   └── modern_magic_role_taxonomy_v2.7.csv  # Earlier iteration
├── requirements.txt                    # Python dependencies
└── project breadcrume file.rtf        # Planning and context notes
```

## 8-Area Taxonomy v1.3.0

1. **Creative Projects** (CP) - DRI for ORIGIN and PROD phases
2. **Technology & Pipeline** (TP) - Technical infrastructure and data  
3. **Talent Acquisition & Casting** (TA) - External talent pipeline
4. **People & Culture** (PC) - Internal team development
5. **Business & Partnerships** (BP) - External relationships and deals
6. **Finance** (FIN) - Financial control and project financing
7. **Studio Operations & Legal** (SOL) - Infrastructure and risk management
8. **Marketing & Community** (MC) - DRI for RELEASE phase

## Lifecycle Phases v1.3.0

1. **DISCOVER** (Origin) - DRI: CP-ORIG → Gate: G_ORIGIN_APPROVED
2. **DEV** (Creative Development) - DRI: CP-DEV → Gate: G_GREENLIGHT  
3. **DEALS** (Project Financing) - DRI: FIN-PROJ + BP-DEALS → Gate: G_FUNDED
4. **PROD** (Production) - DRI: CP-PROD → Gate: G_DELIVERED
5. **RELEASE** (Release & Growth) - DRI: MC-COMMUNITY → Gate: G_POST_EVAL

## Key Changes in v1.3.0
- **CP-ORIG added**: Separates concept vetting from talent pipeline
- **Origin phase rename**: DISCOVER phase now called "Origin" for clarity
- **DRI assignments**: Each phase has clear owner and partner sub-areas
- **Gate evolution**: G_ORIGIN_APPROVED replaces G_DEV_APPROVED

## Status
- **Current Version**: v1.3.0 (August 2025)
- **Branch**: `new-model-updates` 
- **GitHub**: [new-model-updates branch](https://github.com/rodneybusiness/rr-coding-experiments/tree/new-model-updates)
- **Role Taxonomy**: 763 roles defined in v3.1
- **Implementation**: Ready for Notion sync

## Next Steps
1. Configure Notion database IDs in `mapping/notion_mapping.yaml`
2. Set up Notion integration and GitHub secrets  
3. Run `python scripts/sync_notion.py` to deploy v1.3.0 to Notion
4. Enable GitHub Actions for automated sync on schema changes

---
*Consolidated from CogRepo conversation analysis and CSV exports*