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
  - Feature views: `NowView`, `SpotsMapView`, `ListView`, `ChatView`.
  - Shared components: `SpotCard`, `FilterPill`, `TagList`, `QuickActionGrid`.
  - Layout defaults to cards and horizontally scrolling pill filters.
- **Domain Model**
  - `LocationSpot` with enums for `Tier`, `PlaceType`, `AttributeTag`; booleans for flags; `CriticalFieldNotes` string for friction cues.
  - `SpotQuery` and `SpotSort` encapsulate filter/sort intent.
  - `SessionPreset` for ADHD-friendly quick filters (Deep Focus, Body Doubling, Quick Sprint, Late Night).
- **Data Layer**
  - `SpotStore` loads bundled JSON/CSV, normalizes attributes into enums, and caches in-memory.
  - `CompositeSpotLoader` tries bundle resources first and falls back to the repo path so previews/CLI tests can run without Xcode bundling.
  - `SpotRepository` exposes query APIs (`apply(query:context:)`) and computed distances via `CLLocation`.
  - **Sync boundary:** `SyncSource` protocol for future Google Sheets/Notion pull/push; current implementation is a stub.
- **AI Layer**
  - `AIRecommendationService` protocol with DTOs: `AIRecommendationRequest`, `AIRecommendationResponse`, `AIRecommendationItem`.
  - `SimulatedAIService` implements offline rule-based intent parsing (time-of-day + attribute heuristics) so the app works without an API key.
  - `OpenAIService` is an optional live client; it caps the candidate payload (12 spots), emits a compact JSON context, and returns parsed `AIRecommendationResponse`. Provide `OPENAI_API_KEY` at runtime to use it; otherwise the app falls back to the simulated service.
  - When networked, plug in an OpenAI-compatible client that receives compact spot summaries plus user context; the model returns filter/sort preferences only.
- **Location & Distance**
  - `LocationProvider` wraps `CLLocationManager`, publishes authorization state, and provides the latest coordinate. `AppModel` wires it into `SpotStore` so distance sorts update as location changes.
  - Distance computed via `CLLocation` from user position to cached spot coordinates; a geocoded `Latitude/Longitude` column now ships in the dataset so pins and distance sorts work out of the box. When location permission is missing, fall back to a Westchester/Sawtelle anchor or user “close to home/work” hints.

## Screens (first-pass)
- **NowView**: top 1–3 recommendations for "right now" with swipeable cards, quick action buttons (Deep Focus, Body Doubling, Quick Sprint ≤90m, Late Night Work), and a "Show map" button.
- **MapView**: MapKit pins filtered by the same pill filters; list drawer shows ranked nearby spots, quick favorite toggles, and callouts with Tier/OpenLate badges.
- **ListView**: full catalog with sticky filter bar (Tier, Neighborhood, PlaceType, Attributes, booleans) and sort selector (Distance, SentimentScore, Tier, Time-of-day fit) plus a filter summary/clear control.
- **ChatView**: chat-like UI; user query → AI intent → local filtering; responses cite attributes, distance, and `CriticalFieldNotes` and never invent new venues. Recommendations render as cards with map/list deep links and show which filters/sorts were applied.

## Data Model Snapshot
Core schema mirrors the CSV in `data/westside_remote_work_master_verified.csv`:
- Strings: `Name`, `City`, `Neighborhood`, `PlaceType`, `Tier`, `CostBasis`, `Attributes`, `CriticalFieldNotes`, `Status`
- Numbers: `SentimentScore`
- Booleans: `OpenLate`, `CloseToHome`, `CloseToWork`, `SafeToLeaveComputer`, `WalkingFriendlyLocation`, `ExerciseWellnessAvailable`, `ChargedLaptopBrickOnly`

## CSV/JSON ingestion strategy
1. Bundle `westside_remote_work_master_verified.json` (already exported from the CSV) with the app. The CSV now includes `Latitude`/`Longitude` columns; keep them in sync when editing.
2. On first launch, decode into `LocationSpot` and store in memory (or Core Data/SQLite for persistence + favorites/history). User state (favorites/recents) is persisted to `spotstore_state.json` in the app Documents directory.
3. Optionally convert CSV → JSON at build time using a small script; runtime only reads JSON.
4. `AppExperienceView` wires `AppModel`, `QueryModel`, and the feature tabs (Now/Map/List/Chat) so shared filters and AI recommendations stay in sync.

## AI contract (extendable)
- **Request**: user message, current time/day, coarse location (lat/lng), optional active filters, plus a small list of candidate spots (name, neighborhood, tier, attributes, critical notes, distance).
- **Response**: normalized `filters`, `sort`, `preset`, and `recommendations` (ids + rationale). Model is instructed not to invent spots.
- **Fallback**: `SimulatedAIService` applies deterministic heuristics: time-of-day presets, attribute matches, distance sorting, friction warnings (e.g., `ChargedLaptopBrickOnly`).

## How to update the dataset
1. Edit `data/westside_remote_work_master_verified.csv` (or the JSON twin) to add/update rows.
2. Ensure columns follow the schema above; attributes should use the controlled emoji list.
3. Re-run the CSV→JSON export (or copy/paste) so `westside_remote_work_master_verified.json` stays in sync.
4. Avoid renaming columns; add new fields by extending `LocationSpot` and updating the CSV/JSON headers.

IDs are deterministic and derived from `Name + Neighborhood` so favorites/history remain stable even if the data reloads.

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

## What’s Next (short list)
* Ship end-to-end UI tests in Xcode CI (use the stubs in `Tests/WestsideWorkDeciderTests` as a starting point) to lock in presets, chat responses, and filter sharing.
* Add user notes + “last meal/coffee order” stickers to cards, persisted alongside favorites/history.
* Add directions handoff (Maps/Google Maps) and calendar drop-in (“block 90 minutes”) from SpotCard actions.
