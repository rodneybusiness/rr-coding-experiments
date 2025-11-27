# Westside Work Decider (SwiftUI)

An ADHD-friendly iOS decision tool that recommends the best remote-work spot on LA's Westside using a curated dataset. The project prioritizes low-friction choices, quick presets, and AI-assisted intent parsing while keeping a local, offline-first source of truth.

## Recent Updates (November 2025)

### New Features
- **Real-time Open/Closed Status** - Shows whether each spot is currently open based on operating hours
- **Time-Sensitive Warnings** - "Closes in 30 min!" nudges help avoid wasted trips
- **One-Tap Navigation** - Navigate button opens Apple Maps with directions
- **Smart Friction Alerts** - Rush hour parking warnings, night safety reminders
- **Tier Color System** - Visual hierarchy: Purple (Elite), Blue (Reliable), Gray (Unknown)
- **AI Feedback Loop** - Thumbs up/down after recommendations to improve suggestions
- **State Restoration** - App remembers your tab and filters when reopening

### Data Enhancements
- All 44 spots now include operating hours, WiFi quality ratings, and noise levels
- Enhanced AI keyword detection (60+ keywords for better intent parsing)

### Accessibility
- Comprehensive VoiceOver labels throughout
- Dynamic Type support for all text
- Location permission graceful fallback with neighborhood picker

### Testing
- 95+ unit tests covering core functionality
- Integration tests for AI services, formatters, and error handling

---

## Goals & Scope
- **Now screen** with recommendations for the current context (time of day, location, intent presets)
- **Map + list** with pill filters for Tier, Neighborhood, PlaceType, attributes, and boolean flags
- **Chat** that translates free-text questions into filters/sorts against the local dataset (no hallucinated venues)
- **Offline-first data** loaded from bundled JSON into a single local store
- **ADHD-friendly UX**: high contrast, large tap targets, presets over manual steps, minimal clutter

## Architecture Overview

### UI (SwiftUI, iOS 17+)
- **Feature views**: `NowView`, `SpotsMapView`, `SpotListView`, `ChatView`
- **Shared components**: `SpotCard`, `UIComponents` (LoadingStateView, TierBadge, OpenClosedBadge, NavigateButton, FeedbackView, etc.)
- Layout defaults to cards and horizontally scrolling pill filters

### Domain Model
- `LocationSpot` with enums for `Tier`, `PlaceType`, `AttributeTag`; booleans for flags; `CriticalFieldNotes` for friction cues
- `OperatingHours` with per-day schedules and `isOpen(at:)` checking
- `WiFiQuality` and `NoiseLevel` enums for amenity filtering
- `SpotQuery` and `SpotSort` encapsulate filter/sort intent
- `SessionPreset` for ADHD-friendly quick filters (Deep Focus, Body Doubling, Quick Sprint, Late Night)

### Data Layer
- `SpotStore` loads bundled JSON, normalizes attributes, caches with indexed lookups
- `LoadingState<T>` enum provides proper loading/error states to UI
- `QueryCache` with TTL for efficient repeated queries
- User state (favorites/recents) persisted to Documents directory

### AI Layer
- `AIRecommendationService` protocol with DTOs for requests/responses
- `SimulatedAIService` - offline rule-based intent parsing with 60+ keyword mappings
- `OpenAIService` - optional live client with caching, retry logic, and automatic fallback
- Both services share the same response format for seamless switching

### Error Handling
- Domain-specific errors: `SpotDataError`, `AIServiceError`, `LocationError`
- `DisplayableError` for user-friendly error presentation
- `ErrorRecovery` builder for chaining fallback operations
- Error toast modifier for consistent UI feedback

### Location & Distance
- `LocationProvider` wraps `CLLocationManager` with authorization state
- `LocationPermissionView` handles denial gracefully with neighborhood picker fallback
- `DistanceFormatter` for consistent distance display with travel time estimates
- `OfflineIndicator` shows when using cached data

## Screens

### NowView
- Time-based greetings ("Good morning!", "Night owl mode")
- Quick preset buttons (Deep Focus, Body Doubling, Quick Sprint, Late Night)
- Full spot list with all matching results
- Navigate and favorite actions on each card

### MapView
- MapKit pins filtered by current query
- List drawer with ranked spots
- Distance-sorted by default

### ListView
- Full catalog with sticky filter bar
- Sort options: Distance, Sentiment, Tier, Time-of-day fit
- Results count displayed

### ChatView
- Welcome message with suggested prompts
- Typing indicator while processing
- AI recommendations with reasons
- Feedback buttons after each response
- Quick actions to jump to list/map

## Data Model

The dataset includes 44 verified LA Westside work spots with:

### Core Fields
- Name, City, Neighborhood, PlaceType, Tier
- SentimentScore (1-10)
- CriticalFieldNotes (friction cues and tips)

### Boolean Flags
- OpenLate, CloseToHome, CloseToWork
- SafeToLeaveComputer, WalkingFriendlyLocation
- ExerciseWellnessAvailable, ChargedLaptopBrickOnly

### New Fields
- `OperatingHours` - Per-day open/close times
- `WifiQuality` - excellent/good/adequate/poor
- `NoiseLevel` - quiet/moderate/lively

### Attributes
Power Heavy, Easy Parking, Ergonomic, Body Doubling, Deep Focus, Real Food, Call Friendly, Patio Power, Day Pass, Early Bird, Night Owl, Luxury, Elite Coffee

## Shared UI Components

Located in `Sources/Views/Shared/UIComponents.swift`:

| Component | Description |
|-----------|-------------|
| `LoadingStateView` | Generic loading/error/content handler |
| `LoadingIndicator` | Animated spinner with message |
| `ErrorStateView` | Error display with retry button |
| `OpenClosedBadge` | Real-time open/closed status |
| `TierBadge` | Color-coded tier display |
| `TimeSensitiveWarning` | "Closes soon" alerts |
| `NavigateButton` | Apple Maps deep link |
| `OfflineIndicator` | Cached data warning |
| `FeedbackView` | Thumbs up/down buttons |
| `LocationPermissionView` | Permission request/denial |
| `NeighborhoodPicker` | Manual location selection |
| `DistanceDisplay` | Formatted distance with walk time |

## Testing

### Test Files
- `SpotStoreRoundTripTests.swift` - Query, sort, filter tests
- `IntegrationTests.swift` - Cross-component integration tests
- `ErrorSimulationTests.swift` - Error handling and edge cases

### Running Tests
```bash
# Via Xcode
⌘U in Xcode

# Via command line (if swift package)
swift test
```

## Setup

1. Create an iOS 17+ Xcode project
2. Add the `Sources` folder to your project
3. Add `data/westside_remote_work_master_verified.json` to the bundle
4. Wire `AppExperienceView` as your root view
5. (Optional) Set `OPENAI_API_KEY` environment variable for live AI

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Optional. Enables live OpenAI recommendations. Falls back to SimulatedAI if not set. |

## What's Next

- [ ] Widget support (iOS home screen widget)
- [ ] Apple Watch companion
- [ ] Calendar integration ("block 90 minutes")
- [ ] Check-in functionality with crowd sourcing
- [ ] Shortcuts/Siri integration

## License

Private repository - all rights reserved.
