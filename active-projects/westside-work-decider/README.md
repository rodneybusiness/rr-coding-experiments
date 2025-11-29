# Westside Work Decider

An ADHD-friendly iOS app that recommends the best remote-work spots. Originally focused on LA's Westside, now expanded to include favorite spots across multiple cities. Features quick presets, AI-assisted intent parsing, real-time open/closed status, and an offline-first local database of 48 verified locations.

**Platform:** iOS 17+ (iOS 26 enhanced) | **Framework:** SwiftUI | **Status:** Ready for Xcode

---

## Design System

### iOS 26 Liquid Glass
The app features a premium design system optimized for iOS 26's Liquid Glass aesthetic:

- **Native `.glassEffect()`** on iOS 26+ for authentic depth and refraction
- **Warm luxury palette** — gold (#D4A853) for Elite tier, slate (#64748B) for Reliable
- **Editorial serif typography** for distinctive, non-generic appearance
- **Motion-reactive glass** with fluid morph animations
- **Full iOS 17+ backward compatibility** with material fallbacks

### Visual Hierarchy
| Tier | Color | Effect |
|------|-------|--------|
| **Elite** | Warm Gold | Liquid Glass with gold tint, pulsing sparkle |
| **Reliable** | Sophisticated Slate | Liquid Glass with slate tint |
| **Unknown** | Neutral Gray | Standard glass effect |

---

## Quick Start (Xcode Setup)

### Prerequisites

- macOS with **Xcode 15+** (free from App Store)
- **Apple ID** (free tier works, or $99/year Developer account)
- iPhone running **iOS 17+** with USB cable

### Step 1: Create Xcode Project

1. Open Xcode → File → New → Project
2. Select **iOS** → **App** → Next
3. Configure:
   - **Product Name:** `WestsideWorkDecider`
   - **Team:** Your Apple ID
   - **Organization Identifier:** `com.yourname`
   - **Interface:** SwiftUI
   - **Language:** Swift
   - **Minimum Deployment:** iOS 17.0
4. Save the project

### Step 2: Add Source Files

1. In Xcode's Project Navigator, delete the auto-generated `ContentView.swift`
2. Right-click on your project → **Add Files to "WestsideWorkDecider"**
3. Select the entire `Sources` folder from this repo
4. Check:
   - ✅ Copy items if needed
   - ✅ Create groups
5. Click Add

### Step 3: Add Data File

1. Right-click project → **Add Files**
2. Select `data/westside_remote_work_master_verified.json`
3. Ensure **Target Membership** shows your app checked
4. Click Add

### Step 4: Add App Icon

1. In your Xcode project, find `Assets.xcassets`
2. Drag the `Assets/AppIcon.appiconset` folder into Assets.xcassets
3. Or copy the PNG files from `Assets/AppIcon.appiconset/` into the existing AppIcon set

**Icon Design:** Premium gradient with coffee cup, WiFi waves, and location pin—representing remote work connectivity and place discovery.

### Step 5: Set Root View

Edit your app's entry file (e.g., `WestsideWorkDeciderApp.swift`):

```swift
import SwiftUI

@main
struct WestsideWorkDeciderApp: App {
    var body: some Scene {
        WindowGroup {
            AppExperienceView()
        }
    }
}
```

### Step 6: Build & Run

1. Connect your iPhone via USB
2. On iPhone: Settings → Privacy & Security → Developer Mode → ON
3. Trust your Mac when prompted
4. Select your iPhone from Xcode's device dropdown
5. Press **⌘R** to build and run
6. On first launch: Settings → General → VPN & Device Management → Trust your developer certificate

---

## Features

### Now Screen
- Time-based greetings ("Good morning!", "Night owl mode")
- Quick presets: Deep Focus, Body Doubling, Quick Sprint, Late Night
- Real-time open/closed status with "Closes soon!" warnings
- One-tap navigation to Apple Maps

### Map + List Views
- MapKit pins filtered by current query
- Pill filters for Tier, Neighborhood, PlaceType, and attributes
- Sort by distance, sentiment, tier, or time-of-day fit

### Chat
- Natural language queries ("I need a quiet spot with great WiFi")
- AI parses intent into filters (no hallucinated venues)
- Thumbs up/down feedback after recommendations

### ADHD-Friendly Design
- High contrast, large tap targets
- Presets over manual configuration
- Friction warnings (parking, closing time, safety)
- State restoration (remembers your tab and filters)

---

## Data Model

The app includes **48 verified work spots** across multiple locations:

### Coverage Areas
| Region | Cities/Areas |
|--------|--------------|
| **LA Westside** | Santa Monica, Venice, Culver City, Mar Vista, Westwood, Marina del Rey, Playa Vista, Palms, Westchester |
| **New York** | Scarsdale (Westchester County) |
| **California Desert** | Palm Springs Area, Joshua Tree |
| **Utah** | Salt Lake City |

### Spot Data Fields

| Field | Description |
|-------|-------------|
| Name, City, Neighborhood | Location info |
| PlaceType | Coffee shop, coworking, library, hotel lobby, etc. |
| Tier | Elite (gold), Reliable (slate), Unknown (gray) |
| SentimentScore | 1-10 rating |
| OperatingHours | Per-day open/close times with `isOpen(at:)` |
| WiFiQuality | excellent, good, adequate, poor |
| NoiseLevel | quiet, moderate, lively |
| Attributes | Power Heavy, Easy Parking, Ergonomic, Body Doubling, Deep Focus, Real Food, Call Friendly, Patio Power, Day Pass, Early Bird, Night Owl, Luxury, Elite Coffee |
| Boolean Flags | OpenLate, CloseToHome, CloseToWork, SafeToLeaveComputer, WalkingFriendly, ExerciseWellness, ChargedLaptopOnly |
| CriticalFieldNotes | Friction cues and tips |

---

## Architecture

```
Sources/
├── App/
│   ├── AppExperienceView.swift   # Root view with tab navigation
│   ├── AppModel.swift            # App-wide state
│   └── QueryModel.swift          # Filter/sort state
├── Data/
│   └── SpotStore.swift           # JSON loading, caching, indexed lookups
├── Model/
│   └── LocationSpot.swift        # Domain model with OperatingHours
├── Services/
│   ├── AI/
│   │   ├── AIModels.swift        # DTOs for AI requests/responses
│   │   ├── SimulatedAIService.swift  # Offline rule-based AI (60+ keywords)
│   │   └── OpenAIService.swift   # Optional live AI with caching/retry
│   └── Location/
│       └── LocationProvider.swift    # CLLocationManager wrapper
├── Utils/
│   ├── Errors.swift              # Domain errors, LoadingState, ErrorRecovery
│   ├── Formatters.swift          # Distance, time, friction formatters
│   └── TimeOfDayScoring.swift    # Time-based relevance scoring
└── Views/
    ├── Features/
    │   ├── NowView.swift         # Main recommendation screen
    │   ├── ChatView.swift        # Natural language interface
    │   ├── SpotListView.swift    # Full catalog with filters
    │   └── SpotsMapView.swift    # MapKit integration
    └── Shared/
        ├── DesignSystem.swift    # iOS 26 Liquid Glass design tokens
        ├── SpotCard.swift        # Premium spot card with glass effects
        ├── UIComponents.swift    # Badges, buttons, loading states
        ├── FiltersBar.swift      # Pill filter UI
        └── ActiveFiltersSummary.swift

Tests/
└── WestsideWorkDeciderTests/
    ├── SpotStoreRoundTripTests.swift  # Query/sort/filter tests
    ├── IntegrationTests.swift         # Cross-component tests
    └── ErrorSimulationTests.swift     # Error handling tests

Assets/
├── AppIcon.appiconset/           # iOS app icons (all sizes)
│   ├── Contents.json
│   └── icon_*.png                # 1024, 180, 167, 152, 120, etc.
├── AppIcon.svg                   # Source vector
└── generate_icon.py              # Icon generation script

data/
├── westside_remote_work_master_verified.json  # Main dataset (44 spots)
└── westside_remote_work_rejected.csv          # Excluded venues
```

---

## UI Components

### Design System (`DesignSystem.swift`)

| Component | Description |
|-----------|-------------|
| `DS.Colors` | Warm luxury palette with gold/slate/amber accents |
| `DS.LiquidGlass` | iOS 26 refraction and depth configuration |
| `DS.Typography` | Editorial serif for hero, rounded for body |
| `DS.Animation` | Spring animations including glassMorph/glassRipple |
| `.glassCard()` | Native Liquid Glass on iOS 26, material fallback |
| `.liquidGlassProminent()` | Elevated glass for CTAs |
| `.liquidGlassButton()` | Glass-styled buttons |
| `LiquidGlassContainer` | Groups glass elements for shared context |

### Premium Components (`SpotCard.swift`)

| Component | Description |
|-----------|-------------|
| `SpotCard` | Full spot display with Liquid Glass background |
| `PremiumTierBadge` | Gold/slate badges with glass effects |
| `PremiumNavigateButton` | Glass morphing navigate action |
| `PremiumOpenClosedBadge` | Real-time status with pulse animation |
| `PremiumAttributePill` | Tier-aware attribute tags |
| `PremiumDistanceDisplay` | Walk time with icon |

### Shared Components (`UIComponents.swift`)

| Component | Description |
|-----------|-------------|
| `LoadingStateView` | Generic loading/error/content handler |
| `OpenClosedBadge` | Real-time open/closed status |
| `TierBadge` | Color-coded tier display (gold/slate/gray) |
| `TimeSensitiveWarning` | "Closes in 30 min!" alerts |
| `NavigateButton` | Apple Maps deep link |
| `FeedbackView` | Thumbs up/down buttons |
| `OfflineIndicator` | Cached data warning |
| `LocationPermissionView` | Permission handling with fallback |
| `NeighborhoodPicker` | Manual location selection |

---

## Configuration

### Environment Variables (Optional)

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Enables live OpenAI recommendations. Without this, the app uses SimulatedAI which works great offline. |

To set in Xcode: Product → Scheme → Edit Scheme → Run → Arguments → Environment Variables

---

## Testing

**95+ tests** covering core functionality:

```bash
# In Xcode
⌘U

# Command line (Swift Package Manager)
swift test
```

| Test File | Coverage |
|-----------|----------|
| `SpotStoreRoundTripTests.swift` | SpotQuery, LocationSpot, sorting |
| `IntegrationTests.swift` | Formatters, LoadingState, SpotStore, AI |
| `ErrorSimulationTests.swift` | Error types, recovery, edge cases |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Untrusted Developer" | Settings → General → VPN & Device Management → Trust |
| "Device not found" | Unlock iPhone, tap "Trust This Computer" |
| Build errors about iOS version | Set Minimum Deployment to iOS 17.0 |
| App expires after 7 days | Re-run from Xcode (free tier) or get Developer account |
| Missing JSON data | Ensure `westside_remote_work_master_verified.json` has Target Membership checked |

---

## Future Roadmap

- [ ] iOS Widget (home screen quick access)
- [ ] Apple Watch companion
- [ ] Calendar integration ("block 90 minutes")
- [ ] Check-in with crowd-sourced data
- [ ] Siri Shortcuts integration

---

## License

Private repository - all rights reserved.
