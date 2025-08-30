# Modern Magic Area + Sub-Area Taxonomy

**Canonical source for Modern Magic's 8-bucket organizational taxonomy with GitHub→Notion sync capability.**

## Structure

```
MM -- Area + Sub-Area Taxonomy/
├── README.md                    # This documentation
├── schema/
│   ├── areas.yaml              # 8 primary areas with stable IDs
│   └── sub_areas.yaml          # Sub-areas with parent relationships
├── mapping/
│   └── notion_mapping.yaml     # Notion database integration config
├── scripts/
│   ├── validate.py             # Schema validation
│   └── sync_notion.py          # GitHub→Notion sync tool
├── data/                       # Source CSV exports
│   ├── mm_areas_subareas.csv           # Core areas/sub-areas data
│   ├── mm_areas_subareas_all.csv       # Complete export with metadata
│   ├── modern_magic_role_taxonomy_v3.1.csv  # Latest role classifications (763 roles)
│   ├── modern_magic_role_taxonomy_v3.0.csv  # Previous version
│   └── modern_magic_role_taxonomy_v2.7.csv  # Earlier iteration
├── requirements.txt            # Python dependencies
└── mm-taxonomy.txt            # Project structure notes
```

## Final 8-Bucket Taxonomy (Frozen April 2025)

1. **Creative Projects** (CP) - Content creation and curation
2. **Technology & Pipeline** (TP) - Technical infrastructure  
3. **Talent Acquisition & Casting** (TC) - External recruitment
4. **People & Culture** (PC) - Internal employee development
5. **Business & Partnerships** (BP) - External relationships
6. **Finance** (FIN) - Financial control
7. **Studio Operations & Legal** (SOL) - Infrastructure and risk
8. **Marketing & Community** (MC) - Audience engagement

## Status
- **Validated**: 256 projects classified with 100% coverage
- **Role Taxonomy**: 763 roles defined in v3.1
- **Implementation Ready**: YAML schemas and sync scripts prepared
- **Development Complete**: Taxonomy frozen as of April 2025

## Next Steps
1. Configure Notion database IDs in `mapping/notion_mapping.yaml`
2. Set up Notion integration and GitHub secrets
3. Run `python scripts/sync_notion.py` to deploy to Notion
4. Enable GitHub Actions for automated sync on schema changes

---
*Consolidated from CogRepo conversation analysis and CSV exports*