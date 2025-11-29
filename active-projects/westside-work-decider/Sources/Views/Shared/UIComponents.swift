import SwiftUI
import CoreLocation

// MARK: - Loading State View

/// Displays loading, error, or content states based on LoadingState
struct LoadingStateView<T, Content: View>: View {
    let state: LoadingState<T>
    let retryAction: (() -> Void)?
    @ViewBuilder let content: (T) -> Content

    init(
        state: LoadingState<T>,
        retryAction: (() -> Void)? = nil,
        @ViewBuilder content: @escaping (T) -> Content
    ) {
        self.state = state
        self.retryAction = retryAction
        self.content = content
    }

    var body: some View {
        switch state {
        case .idle:
            Color.clear
        case .loading:
            LoadingIndicator()
        case .loaded(let value):
            content(value)
        case .failed(let error):
            ErrorStateView(error: error, retryAction: retryAction)
        }
    }
}

// MARK: - Loading Indicator

struct LoadingIndicator: View {
    @State private var isAnimating = false

    var body: some View {
        VStack(spacing: 16) {
            ProgressView()
                .scaleEffect(1.5)
                .tint(.blue)
            Text("Finding your perfect spot...")
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Loading spots")
    }
}

// MARK: - Error State View

struct ErrorStateView: View {
    let error: Error
    let retryAction: (() -> Void)?

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 48))
                .foregroundStyle(.orange)

            Text(errorTitle)
                .font(.headline)

            Text(errorMessage)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)

            if let suggestion = errorSuggestion {
                Text(suggestion)
                    .font(.caption)
                    .foregroundStyle(.tertiary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }

            if let retryAction, isRetryable {
                Button(action: retryAction) {
                    Label("Try Again", systemImage: "arrow.clockwise")
                        .padding(.horizontal, 20)
                        .padding(.vertical, 10)
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Error: \(errorMessage)")
    }

    private var errorTitle: String {
        "Something went wrong"
    }

    private var errorMessage: String {
        if let localized = error as? LocalizedError {
            return localized.errorDescription ?? error.localizedDescription
        }
        return error.localizedDescription
    }

    private var errorSuggestion: String? {
        (error as? LocalizedError)?.recoverySuggestion
    }

    private var isRetryable: Bool {
        if let aiError = error as? AIServiceError {
            return aiError.isRetryable
        }
        return true
    }
}

// MARK: - Error Toast Modifier

struct ErrorToastModifier: ViewModifier {
    @Binding var error: DisplayableError?

    func body(content: Content) -> some View {
        content
            .alert(
                error?.title ?? "Error",
                isPresented: .init(
                    get: { error != nil },
                    set: { if !$0 { error = nil } }
                ),
                presenting: error
            ) { displayError in
                Button("OK") { error = nil }
                if displayError.isRetryable, let retry = displayError.retryAction {
                    Button("Retry") {
                        error = nil
                        retry()
                    }
                }
            } message: { displayError in
                VStack {
                    Text(displayError.message)
                    if let suggestion = displayError.suggestion {
                        Text(suggestion)
                    }
                }
            }
    }
}

extension View {
    func errorToast(_ error: Binding<DisplayableError?>) -> some View {
        modifier(ErrorToastModifier(error: error))
    }
}

// MARK: - Open/Closed Badge

struct OpenClosedBadge: View {
    let spot: LocationSpot
    let currentDate: Date

    init(spot: LocationSpot, currentDate: Date = Date()) {
        self.spot = spot
        self.currentDate = currentDate
    }

    var body: some View {
        if let hours = spot.operatingHours {
            let isOpen = hours.isOpen(at: currentDate, calendar: .current)
            HStack(spacing: 4) {
                Circle()
                    .fill(isOpen ? Color.green : Color.red)
                    .frame(width: 8, height: 8)
                Text(isOpen ? "Open" : "Closed")
                    .font(.caption.weight(.medium))
                    .foregroundStyle(isOpen ? .green : .red)
            }
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(
                Capsule()
                    .fill((isOpen ? Color.green : Color.red).opacity(0.12))
            )
            .accessibilityLabel(isOpen ? "Currently open" : "Currently closed")
        }
    }
}

// MARK: - Tier Badge

struct TierBadge: View {
    let tier: Tier

    var body: some View {
        Text(tier.rawValue.capitalized)
            .font(.caption.weight(.semibold))
            .foregroundStyle(tierTextColor)
            .padding(.horizontal, 10)
            .padding(.vertical, 5)
            .background(
                Capsule()
                    .fill(tierBackgroundColor)
            )
            .accessibilityLabel("\(tier.rawValue) tier")
    }

    private var tierTextColor: Color {
        switch tier {
        case .elite: return .purple
        case .reliable: return .blue
        case .unknown: return .gray
        }
    }

    private var tierBackgroundColor: Color {
        switch tier {
        case .elite: return .purple.opacity(0.15)
        case .reliable: return .blue.opacity(0.12)
        case .unknown: return .gray.opacity(0.12)
        }
    }
}

// MARK: - Time Sensitive Warning

struct TimeSensitiveWarning: View {
    let spot: LocationSpot
    let currentDate: Date

    init(spot: LocationSpot, currentDate: Date = Date()) {
        self.spot = spot
        self.currentDate = currentDate
    }

    var body: some View {
        if let warning = closingWarning {
            Label(warning, systemImage: "clock.badge.exclamationmark.fill")
                .font(.caption.weight(.medium))
                .foregroundStyle(.orange)
                .accessibilityLabel(warning)
        }
    }

    private var closingWarning: String? {
        guard let hours = spot.operatingHours else { return nil }
        guard hours.isOpen(at: currentDate, calendar: .current) else { return nil }

        let calendar = Calendar.current
        let weekday = calendar.component(.weekday, from: currentDate)

        guard let todayHours = hours.hours(for: weekday) else { return nil }

        // Parse close time
        let components = todayHours.close.split(separator: ":")
        guard components.count >= 2,
              let closeHour = Int(components[0]),
              let closeMinute = Int(components[1]) else { return nil }

        var closeComponents = calendar.dateComponents([.year, .month, .day], from: currentDate)
        closeComponents.hour = closeHour
        closeComponents.minute = closeMinute

        guard let closeDate = calendar.date(from: closeComponents) else { return nil }

        let minutesUntilClose = calendar.dateComponents([.minute], from: currentDate, to: closeDate).minute ?? 0

        if minutesUntilClose <= 0 {
            return nil
        } else if minutesUntilClose <= 30 {
            return "Closes in \(minutesUntilClose) min!"
        } else if minutesUntilClose <= 60 {
            return "Closes in ~1 hour"
        } else if minutesUntilClose <= 90 {
            return "Closes in ~1.5 hours"
        }
        return nil
    }
}

// MARK: - Navigate Button

struct NavigateButton: View {
    let spot: LocationSpot
    let travelMode: TravelMode

    init(spot: LocationSpot, travelMode: TravelMode = .driving) {
        self.spot = spot
        self.travelMode = travelMode
    }

    var body: some View {
        Button(action: openInMaps) {
            Label("Navigate", systemImage: "arrow.triangle.turn.up.right.circle.fill")
                .font(.subheadline.weight(.medium))
        }
        .buttonStyle(.borderedProminent)
        .tint(.blue)
        .accessibilityLabel("Navigate to \(spot.name)")
        .accessibilityHint("Opens in Apple Maps")
    }

    private func openInMaps() {
        let coordinate = spot.coordinate
        let modeParam: String
        switch travelMode {
        case .walking: modeParam = "w"
        case .driving: modeParam = "d"
        case .transit: modeParam = "r"
        }

        let encodedName = spot.name.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? spot.name
        let urlString = "http://maps.apple.com/?daddr=\(coordinate.latitude),\(coordinate.longitude)&dirflg=\(modeParam)&q=\(encodedName)"

        if let url = URL(string: urlString) {
            UIApplication.shared.open(url)
        }
    }
}

// MARK: - Offline Indicator

struct OfflineIndicator: View {
    let isUsingCachedData: Bool

    var body: some View {
        if isUsingCachedData {
            HStack(spacing: 6) {
                Image(systemName: "icloud.slash")
                    .font(.caption)
                Text("Using cached data")
                    .font(.caption)
            }
            .foregroundStyle(.secondary)
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(
                Capsule()
                    .fill(Color.gray.opacity(0.15))
            )
            .accessibilityLabel("Using cached data, you may be offline")
        }
    }
}

// MARK: - Feedback View

struct FeedbackView: View {
    let spotName: String
    let onFeedback: (FeedbackType) -> Void
    @State private var submitted = false

    enum FeedbackType {
        case helpful, notHelpful
    }

    var body: some View {
        if submitted {
            Text("Thanks for your feedback!")
                .font(.caption)
                .foregroundStyle(.secondary)
                .transition(.opacity)
        } else {
            HStack(spacing: 12) {
                Text("Was this helpful?")
                    .font(.caption)
                    .foregroundStyle(.secondary)

                Button {
                    withAnimation { submitted = true }
                    onFeedback(.helpful)
                } label: {
                    Image(systemName: "hand.thumbsup")
                }
                .buttonStyle(.bordered)
                .tint(.green)

                Button {
                    withAnimation { submitted = true }
                    onFeedback(.notHelpful)
                } label: {
                    Image(systemName: "hand.thumbsdown")
                }
                .buttonStyle(.bordered)
                .tint(.red)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("Was this recommendation helpful?")
        }
    }
}

// MARK: - Location Permission View

struct LocationPermissionView: View {
    let status: CLAuthorizationStatus
    let onRequestPermission: () -> Void
    let onSelectNeighborhood: () -> Void

    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: statusIcon)
                .font(.system(size: 56))
                .foregroundStyle(statusColor)

            Text(statusTitle)
                .font(.title2.weight(.semibold))

            Text(statusMessage)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)

            VStack(spacing: 12) {
                if status == .notDetermined {
                    Button("Enable Location", action: onRequestPermission)
                        .buttonStyle(.borderedProminent)
                } else if status == .denied || status == .restricted {
                    Button("Open Settings") {
                        if let url = URL(string: UIApplication.openSettingsURLString) {
                            UIApplication.shared.open(url)
                        }
                    }
                    .buttonStyle(.borderedProminent)
                }

                Button("Select Neighborhood Instead", action: onSelectNeighborhood)
                    .buttonStyle(.bordered)
            }
        }
        .frame(maxWidth: .infinity)
        .padding()
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(statusTitle). \(statusMessage)")
    }

    private var statusIcon: String {
        switch status {
        case .notDetermined: return "location.circle"
        case .denied, .restricted: return "location.slash.circle"
        default: return "location.circle.fill"
        }
    }

    private var statusColor: Color {
        switch status {
        case .notDetermined: return .blue
        case .denied, .restricted: return .red
        default: return .green
        }
    }

    private var statusTitle: String {
        switch status {
        case .notDetermined: return "Enable Location"
        case .denied: return "Location Access Denied"
        case .restricted: return "Location Restricted"
        default: return "Location Enabled"
        }
    }

    private var statusMessage: String {
        switch status {
        case .notDetermined:
            return "We use your location to find nearby work spots and calculate distances."
        case .denied:
            return "Location access was denied. Enable it in Settings to see distances, or select a neighborhood manually."
        case .restricted:
            return "Location access is restricted on this device. You can select a neighborhood manually."
        default:
            return "Your location is being used to find nearby spots."
        }
    }
}

// MARK: - Neighborhood Picker

struct NeighborhoodPicker: View {
    let neighborhoods: [String]
    @Binding var selected: String?
    let onDismiss: () -> Void

    var body: some View {
        NavigationStack {
            List(neighborhoods, id: \.self) { neighborhood in
                Button {
                    selected = neighborhood
                    onDismiss()
                } label: {
                    HStack {
                        Text(neighborhood)
                            .foregroundStyle(.primary)
                        Spacer()
                        if selected == neighborhood {
                            Image(systemName: "checkmark")
                                .foregroundStyle(.blue)
                        }
                    }
                }
            }
            .navigationTitle("Select Neighborhood")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel", action: onDismiss)
                }
            }
        }
    }
}

// MARK: - Friction Badge (Enhanced)

struct EnhancedFrictionBadge: View {
    let spot: LocationSpot
    let currentHour: Int

    init(spot: LocationSpot, currentHour: Int = Calendar.current.component(.hour, from: Date())) {
        self.spot = spot
        self.currentHour = currentHour
    }

    var body: some View {
        if let warning = FrictionBadge.evaluate(for: spot, hour: currentHour) {
            Label(warning.message, systemImage: warning.icon)
                .font(.caption)
                .foregroundStyle(warning.severity == .high ? .red : .orange)
                .accessibilityLabel(warning.message)
        }
    }
}

// MARK: - Distance Display

struct DistanceDisplay: View {
    let meters: Double?
    let showWalkTime: Bool

    init(meters: Double?, showWalkTime: Bool = false) {
        self.meters = meters
        self.showWalkTime = showWalkTime
    }

    var body: some View {
        if let meters {
            VStack(alignment: .trailing, spacing: 2) {
                Text(DistanceFormatter.format(meters: meters))
                    .font(.subheadline.weight(.semibold))

                if showWalkTime {
                    Text(DistanceFormatter.estimatedTime(meters: meters, mode: .walking))
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
            }
            .padding(8)
            .background(Capsule().fill(.blue.opacity(0.12)))
            .accessibilityLabel("Distance: \(DistanceFormatter.format(meters: meters))")
        }
    }
}
