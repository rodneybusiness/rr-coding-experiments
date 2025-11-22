# Westside Work Decider (SwiftUI)

An ADHD-friendly iOS decision tool that recommends the best remote-work spot on LA's Westside using a curated CSV dataset. The project prioritizes low-friction choices, quick presets, and AI-assisted intent parsing while keeping a local, offline-first source of truth.

## Goals & Scope
- **Now screen** with 1–3 low-friction picks for the current context (time of day, location, intent presets).
- **Map + list** with pill filters for Tier, Neighborhood, PlaceType, attributes, and boolean flags.
- **Chat** that translates free-text questions into filters/sorts against the local dataset (no hallucinated venues).
- **Offline-first data** loaded from a bundled CSV/JSON into a single local store, with an abstracted sync layer for Sheets/Notion later.
- **ADHD-friendly UX**: high contrast, large tap targets, presets over manual steps, minimal clutter.

## Architecture Overview
- **UI (SwiftUI, iOS 17+)**
  - Feature views: `NowView`, `MapView`, `ListView`, `ChatView`.
  - Shared components: `SpotCard`, `FilterPill`, `TagList`, `QuickActionGrid`.
  - Layout defaults to cards and horizontally scrolling pill filters.
- **Domain Model**
  - `LocationSpot` with enums for `Tier`, `PlaceType`, `AttributeTag`; booleans for flags; `CriticalFieldNotes` string for friction cues.
  - `SpotQuery` and `SpotSort` encapsulate filter/sort intent.
  - `SessionPreset` for ADHD-friendly quick filters (Deep Focus, Body Doubling, Quick Sprint, Late Night).
- **Data Layer**
  - `SpotStore` loads bundled JSON/CSV, normalizes attributes into enums, and caches in-memory.
  - `SpotRepository` exposes query APIs (`apply(query:context:)`) and computed distances via `CLLocation`.
  - **Sync boundary:** `SyncSource` protocol for future Google Sheets/Notion pull/push; current implementation is a stub.
- **AI Layer**
  - `AIRecommendationService` protocol with DTOs: `AIRecommendationRequest`, `AIRecommendationResponse`, `AIRecommendationItem`.
  - `SimulatedAIService` implements offline rule-based intent parsing (time-of-day + attribute heuristics) so the app works without an API key.
  - When networked, plug in an OpenAI-compatible client that receives compact spot summaries plus user context; the model returns filter/sort preferences only.
- **Location & Distance**
  - `LocationProvider` wraps `CLLocationManager`, publishes authorization state, and provides the latest coordinate.
  - Distance computed via `CLLocation` from user position to cached spot coordinates (later swapped for geocoded lat/lng column or precomputed cache). Geocoder utility should run once and persist results to avoid runtime churn.

## Screens (first-pass)
- **NowView**: top 1–3 recommendations for "right now" with swipeable cards, quick action buttons (Deep Focus, Body Doubling, Quick Sprint ≤90m, Late Night Work), and a "Show map" button.
- **MapView**: MapKit pins filtered by the same pill filters; list drawer shows ranked nearby spots.
- **ListView**: full catalog with sticky filter bar (Tier, Neighborhood, PlaceType, Attributes, booleans) and sort selector (Distance, SentimentScore, Tier, Time-of-day fit).
- **ChatView**: chat-like UI; user query → AI intent → local filtering; responses cite attributes, distance, and `CriticalFieldNotes` and never invent new venues.

## Data Model Snapshot
Core schema mirrors the CSV in `data/westside_remote_work_master_verified.csv`:
- Strings: `Name`, `City`, `Neighborhood`, `PlaceType`, `Tier`, `CostBasis`, `Attributes`, `CriticalFieldNotes`, `Status`
- Numbers: `SentimentScore`
- Booleans: `OpenLate`, `CloseToHome`, `CloseToWork`, `SafeToLeaveComputer`, `WalkingFriendlyLocation`, `ExerciseWellnessAvailable`, `ChargedLaptopBrickOnly`

## CSV/JSON ingestion strategy
1. Bundle `westside_remote_work_master_verified.json` (already exported from the CSV) with the app.
2. On first launch, decode into `LocationSpot` and store in memory (or Core Data/SQLite for persistence + favorites/history).
3. Optionally convert CSV → JSON at build time using a small script; runtime only reads JSON.

## AI contract (extendable)
- **Request**: user message, current time/day, coarse location (lat/lng), optional active filters, plus a small list of candidate spots (name, neighborhood, tier, attributes, critical notes, distance).
- **Response**: normalized `filters`, `sort`, `preset`, and `recommendations` (ids + rationale). Model is instructed not to invent spots.
- **Fallback**: `SimulatedAIService` applies deterministic heuristics: time-of-day presets, attribute matches, distance sorting, friction warnings (e.g., `ChargedLaptopBrickOnly`).

## How to update the dataset
1. Edit `data/westside_remote_work_master_verified.csv` (or the JSON twin) to add/update rows.
2. Ensure columns follow the schema above; attributes should use the controlled emoji list.
3. Re-run the CSV→JSON export (or copy/paste) so `westside_remote_work_master_verified.json` stays in sync.
4. Avoid renaming columns; add new fields by extending `LocationSpot` and updating the CSV/JSON headers.

## Adding new metadata safely
- Add new columns to CSV/JSON; mark them as optional in `LocationSpot` with sensible defaults.
- Update `SpotStore` parsing to map the new fields; keep filter logic resilient to missing data.
- Prefer enums for new controlled vocabularies; add cases with an `unknown` fallback to preserve decoding.

## Future sync (Sheets/Notion)
- Implement a `SyncSource` that fetches rows and writes to the local store; local store remains the runtime source of truth.
- Conflict policy: local user data (favorites, notes, history) always merged on top of remote updates.
- Consider background refresh + pull-to-refresh on List/Now screens.

## Run/Preview
This repo only ships the Swift source and sample data. Create an Xcode project (iOS 17 target), drop the `Sources` folder and `data` assets into the project, and wire `SpotStore` into an `@MainActor` `AppModel` (examples provided in code).
