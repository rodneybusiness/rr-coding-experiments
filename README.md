# RR Coding Experiments
**A Collection of Creative Technology Projects**

## Overview
This repository contains various coding projects and experiments, from **production-ready enterprise applications** to creative file management systems, data analysis pipelines, and retro game development. Each project solves real-world problems or explores interesting technical challenges.

---

## 🌟 Featured Project: Film Financing Navigator

**Status:** ✅ **PRODUCTION READY** (v1.0.0 - October 2025)

### [Independent Animated Film Financing Model v1](./active-projects/Independent%20Animated%20Film%20Financing%20Model%20v1/)

A **world-class financial simulation platform** for animation film financing. This is a complete, production-ready full-stack application with enterprise-grade architecture.

**What It Does:**
- Calculates tax incentives across 25+ global jurisdictions
- Executes industry-standard recoupment waterfalls with Monte Carlo simulation
- Optimizes capital stack scenarios using multi-objective optimization
- Provides IRR, NPV, and Cash-on-Cash analysis for investors

**Technology Stack:**
- **Backend:** Python 3.11, FastAPI, PostgreSQL, Redis
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS, Recharts
- **Infrastructure:** Docker, docker-compose, Nginx
- **Advanced:** PyMC (Bayesian simulation), SciPy (optimization)

**Key Features:**
- 🎯 **3 Calculation Engines:** Tax Incentives, Waterfall Executor, Scenario Optimizer
- 🐳 **Docker Deployment:** One-command deployment with `make install`
- 🔒 **Production Ready:** Health checks, monitoring, security hardening
- 📊 **Rich Visualizations:** Interactive charts, tables, radar plots
- ✅ **Tested:** 60+ integration tests, TypeScript: 0 errors
- 📚 **Well Documented:** 900+ line deployment guide

**Quick Start:**
```bash
cd "active-projects/Independent Animated Film Financing Model v1"
make install && make up
# Visit http://localhost:3000
```

**Expert Review:** 8.2/10 code quality score - Production approved

[📖 Full Documentation](./active-projects/Independent%20Animated%20Film%20Financing%20Model%20v1/README.md) | [🐳 Docker Guide](./active-projects/Independent%20Animated%20Film%20Financing%20Model%20v1/DOCKER_DEPLOYMENT.md)

---

## Other Projects

### 🎬 [8BG Renaming Tools](./8bg-renaming-tools/)
A universal file naming system for creative projects. Originally developed for film production, now applicable to any collaborative creative work. Solves the chaos of version control in creative industries.

### 🏢 [MM Area + Sub-Area Taxonomy](./active-projects/MM%20--%20Area%20+%20Sub-Area%20Taxonomy/)
Modern Magic's canonical 8-area organizational taxonomy with lifecycle phases. Features GitHub→Notion sync, stable IDs, and clear DRI assignments for project lifecycle management.

### 🧠 [CogRepo](./active-projects/cogrepo/)
Transform LLM conversations into a searchable knowledge base. Captures, indexes, and analyzes AI chat history to extract insights, patterns, and strategic opportunities from thousands of conversations.

### ✈️ [Family Travel Analysis](./family-travel-analysis/)
Data mining pipeline for analyzing years of family travel conversations. Extracts patterns, preferences, and planning insights from chat history to understand travel dynamics and improve future trip planning.

### 🎌 [Anime Directors Analysis](./anime-directors-analysis/)
Analyzes conversations about legendary animation directors like Miyazaki and Satoshi Kon. Tracks discussion patterns, film references, and thematic connections across 308+ conversations about anime.

### 🧟 [Zombie Quest](./zombie-quest/)
A retro Sierra-style adventure game built in Python with Pygame. Features authentic VGA palette and classic point-and-click gameplay, combining nostalgia with modern zombie themes.

### 🔧 [Miscellaneous Experiments](./misc-experiments/)
One-off scripts and uncategorized utilities. The staging ground for new ideas and quick experiments that haven't evolved into full projects yet.

## Common Themes
- **Enterprise Applications**: Production-ready full-stack platforms
- **Data Analysis**: Mining insights from conversation history
- **Creative Tools**: Systems for creative professionals
- **Financial Engineering**: Advanced simulation and optimization
- **Pattern Recognition**: Finding hidden insights in large datasets
- **Nostalgia Tech**: Recreating classic computing experiences
- **Real-World Solutions**: Tools built to solve actual problems

## Technical Stack

### Production Applications
- **Backend:** Python 3.11, FastAPI, Pydantic, SQLAlchemy
- **Frontend:** Next.js 14, React, TypeScript, Tailwind CSS
- **Database:** PostgreSQL 15, Redis 7
- **Infrastructure:** Docker, docker-compose, Nginx
- **Testing:** pytest, pytest-asyncio, React Testing Library

### Data & Analysis
- **Languages:** Python, Bash, TypeScript
- **Data Formats:** JSON, JSONL, Parquet, CSV
- **Libraries:** pandas, NumPy, SciPy, PyMC
- **Visualization:** Recharts, D3.js, matplotlib

### Development Tools
- **API:** FastAPI, Uvicorn, OpenAPI/Swagger
- **Build:** Docker multi-stage builds, npm, pip
- **Version Control:** Git, GitHub
- **Package Management:** npm, pip, requirements.txt

## Philosophy
These projects represent a belief that:
- **Excellence matters:** Production-ready code with proper testing and documentation
- **Conversations are valuable:** AI interactions and creative work deserve preservation
- **Organization enhances creativity:** Systems enable innovation, not restrict it
- **Data reveals truth:** Analysis can uncover insights about ourselves and our work
- **Technology serves people:** Build solutions to real problems, not problems for solutions
- **Simplicity when possible:** Sometimes a simple script is better than a complex system
- **Complexity when needed:** Enterprise applications require enterprise-grade architecture

## Getting Started

### 🐳 For Production Applications (Film Financing Navigator)
```bash
cd "active-projects/Independent Animated Film Financing Model v1"
make install
make up
# Visit http://localhost:3000
```

### 📦 For Other Projects
Each project has its own README with specific setup instructions. Most Python projects use standard pip-installable requirements. Shell scripts are generally standalone and ready to run.

## Repository Structure

```
rr-coding-experiments/
├── active-projects/                    # Production and active development
│   ├── Independent Animated Film Financing Model v1/  # ⭐ Featured
│   ├── cogrepo/                       # LLM conversation knowledge base
│   ├── Index Cards Project (2025)/
│   └── ... (10 active projects)
│
├── 8bg-renaming-tools/                # Creative file naming system
├── anime-directors-analysis/          # Animation discussion analysis
├── family-travel-analysis/            # Travel planning insights
├── zombie-quest/                      # Retro adventure game
└── misc-experiments/                  # Staging ground for new ideas
```

See [`active-projects/README.md`](./active-projects/README.md) for complete project catalog.

## Recent Achievements (October 2025)

✅ **Film Financing Navigator** - Complete production-ready platform
- Full-stack TypeScript/Python application
- 3 sophisticated calculation engines
- Docker deployment infrastructure
- 60+ integration tests
- Expert code review validated

✅ **Active Projects Organization** - New directory structure
- See [`active-projects/README.md`](./active-projects/README.md) for full catalog

## Future Direction
- ✅ ~~API development for tool accessibility~~ - **COMPLETED** (Film Financing Navigator)
- ✅ ~~Web interfaces for command-line tools~~ - **COMPLETED** (Next.js 14 UI)
- More integration between projects (e.g., using CogRepo to analyze creative project discussions)
- Machine learning applications for pattern recognition
- Additional financial engineering tools
- Mobile applications for key platforms

---
*Built with curiosity, maintained with purpose*
