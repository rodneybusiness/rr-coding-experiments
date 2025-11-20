# 🎭 Comedy Writer Intelligence Platform

> **Transform the chaos of comedy writing talent discovery into a data-driven competitive advantage.**

A powerful analytics platform that combines network analysis, AI-powered enrichment, and "Moneyball" optimization to help showrunners, producers, and executives discover, evaluate, and assemble world-class comedy writing teams.

![Platform Status](https://img.shields.io/badge/status-production-success)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd comedy-writers-analysis

# Install dependencies
pip install -r requirements.txt

# Launch the platform
streamlit run app.py
```

### Optional: Enable AI Features

For deep enrichment and tone analysis, set your API keys:

```bash
# OpenAI (GPT-4)
export OPENAI_API_KEY="your_key_here"

# Anthropic (Claude)
export ANTHROPIC_API_KEY="your_key_here"

# Google (Gemini 1.5 Pro)
export GOOGLE_API_KEY="your_key_here"
```

---

## ✨ Features

### 1. **🏆 The Leaderboard**

- **Moneyball Scoring**: Writers ranked by weighted impact across tiers (Prestige, Network, Cable)
- **Creator Bonuses**: Showrunners and creators get massive score multipliers
- **On-Demand Enrichment**: Click to fetch AI-powered bios, awards, and strengths

### 2. **🕸️ Network Graph**

- **Collaboration Mapping**: Visualize which writers have worked together
- **Clique Detection**: Identify tight-knit writer groups and "rooms-in-waiting"
- **Interactive & Filterable**: Explore connections by minimum score threshold

### 3. **🏗️ The Room Builder (Alpha)**

> **The Showrunner's Engine** - Define your show's creative DNA and budget, then watch the platform assemble the perfect team.

- **Tone Vector Matching**: Set 5-dimensional creative parameters (Darkness, Pace, Satire, Heart, Absurdity)
- **Budget Caps**: Realistic constraints (Low: $60K/week, Mid: $120K, High: $250K)
- **Seniority Rules**: Strict matching ensures showrunners are veterans and staff writers are juniors
- **Salary Quotes**: Each writer has an estimated "weekly quote" based on their score and role

### 4. **🕴️ The Power Brokers**

- **Agency Ecosystem**: Visualize the representation hierarchy
- **Simulated Data**: If real IMDb Pro data isn't available, the system generates realistic agency assignments (CAA, WME, UTA for top talent)

### 5. **✨ Deep Enrichment (The 10X Layer)**

- **Writer DNA**: Background (Stand-up vs Improv), Awards (Emmy, WGA), Strengths (Dialogue vs Structure)
- **Show Intelligence**: Plot summaries, key themes, cultural impact scores
- **Multi-Model AI**: Supports OpenAI, Anthropic, and Google Gemini

---

## 🧠 The Data Moat

### Scoring Algorithm

Writers are scored using a weighted formula:

```
Writing Points = Σ (Tier Score × Episode Count)
  - Prestige (A24, HBO Max): 3.0 per episode
  - Network (NBC, ABC): 2.0 per episode
  - Cable/Streaming: 1.0 per episode

Creator Points = Σ (Tier Score × 15)
  - 15x multiplier for show creators

Total Score = Writing Points + Creator Points
```

### Tone Vectors

Every show is analyzed across 5 dimensions (0-100 scale):

- **Darkness**: Light sitcom → Grim drama
- **Pace**: Slow/languid → Fast/Sorkin-esque
- **Satire**: Sincere → Cynical
- **Heart**: Cold → Warm (Ted Lasso)
- **Absurdity**: Grounded → Surreal (I Think You Should Leave)

---

## 📊 Data Sources

The platform currently includes:

- **250+ Writers** from top comedy shows of the last 10 years
- **100+ Shows** across live-action and animation
- **Global Coverage**: U.S., UK, Ireland, Europe, Asia-Pacific

### Key Shows

- **U.S.**: _The Office_, _Parks and Recreation_, _Atlanta_, _The Bear_, _Hacks_
- **UK/Ireland**: _Fleabag_, _Derry Girls_, _The IT Crowd_
- **Animation**: _Bob's Burgers_, _BoJack Horseman_, _Big Mouth_

---

## 🏗️ Architecture

```
comedy-writers-analysis/
├── app.py                   # Streamlit dashboard
├── comedy_analytics/
│   ├── models.py            # Data models (Writer, Show, Credit)
│   ├── data_manager.py      # CSV loading + FALLBACK_SHOWS
│   ├── scoring.py           # Moneyball algorithm
│   ├── enrichment.py        # Tone analysis + EnrichmentEngine
│   ├── llm_client.py        # OpenAI/Claude/Gemini integration
│   ├── room_builder.py      # The Room Builder algorithm
│   ├── reps_manager.py      # Agency data (real or simulated)
│   └── ui_components.py     # Custom CSS + writer cards
├── data/
│   ├── michelin_enriched_updated.csv
│   └── comedy_writers.csv
└── requirements.txt
```

---

## 🎯 Use Cases

### For Showrunners

- **Discover Hidden Gems**: Find undervalued writers with perfect tone fit
- **Build Realistic Rooms**: Respect both creative chemistry and budget reality
- **Leverage Networks**: Hire writers who've worked together before

### For Studio Executives

- **Talent Scouting**: Identify rising stars before they become expensive
- **Competitive Intelligence**: Track which agencies control the best talent
- **Portfolio Analysis**: Understand your current roster's strengths and gaps

### For Agents/Managers

- **Client Positioning**: Benchmark your clients against the market
- **Deal Strategy**: Understand realistic "quotes" based on scoring
- **Network Expansion**: Identify collaboration opportunities

---

## 🔮 Roadmap

### Next Features

- [ ] **Real IMDb Pro Integration**: Replace simulated agency data
- [ ] **Talent Arbitrage Metric**: Impact-to-Credit Ratio visualization
- [ ] **Diversity Analytics**: Track and optimize for inclusive hiring
- [ ] **Show Recommendation Engine**: "Shows like X but with Y tone"
- [ ] **Export to Deck**: Generate presentation-ready talent reports

---

## 🤝 Contributing

This is a private research project, but feedback is welcome! If you encounter issues or have feature requests, please open an issue.

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

Built with:

- [Streamlit](https://streamlit.io/) - The dashboard framework
- [NetworkX](https://networkx.org/) - Graph analysis
- [Plotly](https://plotly.com/) - Interactive visualizations
- [OpenAI](https://openai.com/), [Anthropic](https://anthropic.com/), [Google AI](https://ai.google.dev/) - LLM enrichment

---

**Made with ❤️ for the comedy writing community.**
