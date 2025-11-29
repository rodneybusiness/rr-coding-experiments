import SwiftUI
import CoreLocation

// MARK: - Premium SpotCard 2025

struct SpotCard: View {
    let spot: LocationSpot
    let distanceMeters: Double?
    let showNavigateButton: Bool
    var isFavorite: Bool = false
    var onFavorite: (() -> Void)? = nil
    var onTap: (() -> Void)? = nil

    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @Environment(\.colorScheme) private var colorScheme
    @State private var isPressed = false
    @State private var hasAppeared = false

    init(
        spot: LocationSpot,
        distanceMeters: Double? = nil,
        showNavigateButton: Bool = true,
        isFavorite: Bool = false,
        onFavorite: (() -> Void)? = nil,
        onTap: (() -> Void)? = nil
    ) {
        self.spot = spot
        self.distanceMeters = distanceMeters
        self.showNavigateButton = showNavigateButton
        self.isFavorite = isFavorite
        self.onFavorite = onFavorite
        self.onTap = onTap
    }

    // Legacy initializer for compatibility
    init(
        spot: LocationSpot,
        distanceText: String?,
        frictionBadge: String?,
        isFavorite: Bool = false,
        onFavorite: (() -> Void)? = nil,
        onTap: (() -> Void)? = nil
    ) {
        self.spot = spot
        if let text = distanceText {
            let numericPart = text.replacingOccurrences(of: " mi", with: "")
                .replacingOccurrences(of: "< ", with: "")
            if let miles = Double(numericPart) {
                self.distanceMeters = miles * 1609.34
            } else {
                self.distanceMeters = nil
            }
        } else {
            self.distanceMeters = nil
        }
        self.showNavigateButton = true
        self.isFavorite = isFavorite
        self.onFavorite = onFavorite
        self.onTap = onTap
    }

    var body: some View {
        VStack(alignment: .leading, spacing: DS.Spacing.sm) {
            // Header row: Name, tier badge, favorite
            headerRow

            // Subtitle row: neighborhood, type
            subtitleRow

            // Status row: open/closed, time warning
            statusRow

            // Notes with elegant typography
            notesSection

            // Attributes as premium pills
            attributeRow

            // Last visited indicator
            lastVisitedRow

            // Friction warning with icon
            frictionRow

            // Navigate button with premium style
            if showNavigateButton {
                navigateRow
            }
        }
        .padding(DS.Spacing.md)
        .glassCard(cornerRadius: DS.Radius.xl, tier: spot.tier)
        .scaleEffect(isPressed ? 0.98 : 1)
        .animation(DS.Animation.snappy, value: isPressed)
        .opacity(hasAppeared ? 1 : 0)
        .offset(y: hasAppeared ? 0 : 20)
        .onAppear {
            withAnimation(DS.Animation.springy.delay(0.1)) {
                hasAppeared = true
            }
        }
        .contentShape(Rectangle())
        .onTapGesture {
            HapticFeedback.light()
            onTap?()
        }
        .onLongPressGesture(minimumDuration: 0.1, pressing: { pressing in
            isPressed = pressing
        }, perform: {})
        .accessibilityElement(children: .combine)
        .accessibilityLabel(accessibilityDescription)
        .accessibilityHint("Double tap to mark as visited")
        .accessibilityAddTraits(.isButton)
    }

    // MARK: - Subviews

    private var headerRow: some View {
        HStack(alignment: .top, spacing: DS.Spacing.sm) {
            VStack(alignment: .leading, spacing: DS.Spacing.xxs) {
                Text(spot.name)
                    .font(.system(size: 18, weight: .semibold, design: .default))
                    .foregroundStyle(.primary)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Spacer(minLength: DS.Spacing.xs)

            // Premium tier badge
            PremiumTierBadge(tier: spot.tier)

            if let distanceMeters {
                PremiumDistanceDisplay(meters: distanceMeters, showWalkTime: distanceMeters < 2000)
            }

            if let onFavorite {
                Button(action: {
                    HapticFeedback.medium()
                    onFavorite()
                }) {
                    Image(systemName: isFavorite ? "heart.fill" : "heart")
                        .font(.system(size: 20, weight: .medium))
                        .foregroundStyle(isFavorite ? .red : .secondary)
                        .symbolEffect(.bounce, value: isFavorite)
                }
                .buttonStyle(.plain)
                .accessibilityLabel(isFavorite ? "Remove from favorites" : "Add to favorites")
            }
        }
    }

    private var subtitleRow: some View {
        HStack(spacing: DS.Spacing.xs) {
            // Place type icon with subtle background
            HStack(spacing: DS.Spacing.xxs) {
                Image(systemName: placeTypeIcon)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundStyle(tierAccentColor.opacity(0.8))

                Text(spot.neighborhood)
                    .font(.system(size: 14, weight: .medium, design: .rounded))
                    .foregroundStyle(.secondary)
            }
            .padding(.horizontal, DS.Spacing.xs)
            .padding(.vertical, DS.Spacing.xxs)
            .background(
                Capsule()
                    .fill(tierAccentColor.opacity(0.1))
            )

            Text("•")
                .foregroundStyle(.tertiary)

            Text(spot.placeType.rawValue)
                .font(.system(size: 13, weight: .regular))
                .foregroundStyle(.tertiary)

            Spacer()
        }
    }

    private var statusRow: some View {
        HStack(spacing: DS.Spacing.sm) {
            PremiumOpenClosedBadge(spot: spot)
            PremiumTimeSensitiveWarning(spot: spot)
            Spacer()
        }
    }

    private var notesSection: some View {
        Text(spot.criticalFieldNotes)
            .font(.system(size: 14, weight: .regular, design: .default))
            .foregroundStyle(.secondary)
            .lineLimit(dynamicTypeSize > .large ? 4 : 3)
            .fixedSize(horizontal: false, vertical: true)
            .lineSpacing(2)
    }

    private var attributeRow: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: DS.Spacing.xs) {
                ForEach(spot.attributes.prefix(6)) { tag in
                    PremiumAttributePill(tag: tag, showLabel: dynamicTypeSize <= .large)
                }
            }
        }
    }

    private var lastVisitedRow: some View {
        Group {
            if let lastVisited = spot.lastVisited {
                HStack(spacing: DS.Spacing.xxs) {
                    Image(systemName: "clock.arrow.circlepath")
                        .font(.system(size: 11, weight: .medium))
                    Text(RelativeTimeFormatter.lastVisited(lastVisited) ?? "")
                        .font(.system(size: 12, weight: .medium, design: .rounded))
                }
                .foregroundStyle(.tertiary)
            }
        }
    }

    private var frictionRow: some View {
        Group {
            if let warning = FrictionBadge.evaluate(for: spot) {
                HStack(spacing: DS.Spacing.xs) {
                    Image(systemName: warning.icon)
                        .font(.system(size: 12, weight: .semibold))
                        .symbolEffect(.pulse)
                    Text(warning.message)
                        .font(.system(size: 12, weight: .medium))
                }
                .foregroundStyle(warning.severity == .high ? DS.Colors.error : DS.Colors.warning)
                .padding(.horizontal, DS.Spacing.sm)
                .padding(.vertical, DS.Spacing.xs)
                .background(
                    Capsule()
                        .fill((warning.severity == .high ? DS.Colors.error : DS.Colors.warning).opacity(0.15))
                )
            }
        }
    }

    private var navigateRow: some View {
        HStack {
            Spacer()
            PremiumNavigateButton(spot: spot, travelMode: .driving)
        }
    }

    // MARK: - Helpers

    private var placeTypeIcon: String {
        switch spot.placeType {
        case .cafe: return "cup.and.saucer.fill"
        case .coworking: return "building.2.fill"
        case .library: return "book.fill"
        case .hotelLobby: return "building.fill"
        case .cafeRestaurant: return "fork.knife"
        case .club: return "building.columns.fill"
        case .bookstoreCafe: return "books.vertical.fill"
        case .bankCafe: return "dollarsign.circle.fill"
        case .unknown: return "mappin.circle.fill"
        }
    }

    private var tierAccentColor: Color {
        switch spot.tier {
        case .elite: return DS.Colors.accentGold
        case .reliable: return DS.Colors.accentSlate
        case .unknown: return .gray
        }
    }

    private var accessibilityDescription: String {
        var parts: [String] = []
        parts.append(spot.name)
        parts.append("\(spot.tier.rawValue) tier \(spot.placeType.rawValue)")
        parts.append("in \(spot.neighborhood)")

        if let distanceMeters {
            parts.append(DistanceFormatter.format(meters: distanceMeters))
        }

        if let hours = spot.operatingHours, hours.isOpen(at: Date(), calendar: .current) {
            parts.append("Currently open")
        }

        if isFavorite {
            parts.append("Favorited")
        }

        parts.append(spot.criticalFieldNotes)

        return parts.joined(separator: ". ")
    }
}

// MARK: - Premium Tier Badge

struct PremiumTierBadge: View {
    let tier: Tier
    @State private var isAnimating = false

    var body: some View {
        HStack(spacing: DS.Spacing.xxs) {
            if tier == .elite {
                Image(systemName: "sparkles")
                    .font(.system(size: 10, weight: .bold))
                    .symbolEffect(.pulse, isActive: isAnimating)
            }
            Text(tier.rawValue.capitalized)
                .font(.system(size: 11, weight: .bold, design: .rounded))
                .textCase(.uppercase)
                .tracking(0.5)
        }
        .foregroundStyle(tierTextColor)
        .padding(.horizontal, DS.Spacing.sm)
        .padding(.vertical, DS.Spacing.xs)
        .background(
            Capsule()
                .fill(tierBackgroundGradient)
        )
        .overlay(
            Capsule()
                .stroke(tierBorderColor.opacity(0.3), lineWidth: 0.5)
        )
        .shadow(color: tierGlowColor.opacity(0.4), radius: 8, x: 0, y: 2)
        .onAppear {
            if tier == .elite {
                isAnimating = true
            }
        }
        .accessibilityLabel("\(tier.rawValue) tier")
    }

    private var tierTextColor: Color {
        switch tier {
        case .elite: return Color(hex: "1A1A1F") // Dark text on gold
        case .reliable: return DS.Colors.textPrimary
        case .unknown: return .gray
        }
    }

    private var tierBackgroundGradient: LinearGradient {
        switch tier {
        case .elite:
            return LinearGradient(
                colors: [DS.Colors.accentGold, DS.Colors.accentAmber],
                startPoint: .leading,
                endPoint: .trailing
            )
        case .reliable:
            return LinearGradient(
                colors: [DS.Colors.accentSlate.opacity(0.25), DS.Colors.accentBlue.opacity(0.15)],
                startPoint: .leading,
                endPoint: .trailing
            )
        case .unknown:
            return LinearGradient(
                colors: [Color.gray.opacity(0.15)],
                startPoint: .leading,
                endPoint: .trailing
            )
        }
    }

    private var tierBorderColor: Color {
        switch tier {
        case .elite: return DS.Colors.accentAmber
        case .reliable: return DS.Colors.accentSlate
        case .unknown: return .gray
        }
    }

    private var tierGlowColor: Color {
        switch tier {
        case .elite: return DS.Colors.accentGold
        case .reliable: return DS.Colors.accentBlue
        case .unknown: return .clear
        }
    }
}

// MARK: - Premium Open/Closed Badge

struct PremiumOpenClosedBadge: View {
    let spot: LocationSpot
    let currentDate: Date

    init(spot: LocationSpot, currentDate: Date = Date()) {
        self.spot = spot
        self.currentDate = currentDate
    }

    var body: some View {
        if let hours = spot.operatingHours {
            let isOpen = hours.isOpen(at: currentDate, calendar: .current)
            HStack(spacing: DS.Spacing.xxs) {
                Circle()
                    .fill(isOpen ? DS.Colors.success : DS.Colors.error)
                    .frame(width: 6, height: 6)
                    .overlay(
                        Circle()
                            .stroke(isOpen ? DS.Colors.success : DS.Colors.error, lineWidth: 2)
                            .scaleEffect(1.5)
                            .opacity(isOpen ? 0.3 : 0)
                    )
                Text(isOpen ? "Open" : "Closed")
                    .font(.system(size: 12, weight: .semibold, design: .rounded))
            }
            .foregroundStyle(isOpen ? DS.Colors.success : DS.Colors.error)
            .padding(.horizontal, DS.Spacing.sm)
            .padding(.vertical, DS.Spacing.xs)
            .background(
                Capsule()
                    .fill((isOpen ? DS.Colors.success : DS.Colors.error).opacity(0.12))
            )
            .accessibilityLabel(isOpen ? "Currently open" : "Currently closed")
        }
    }
}

// MARK: - Premium Time Sensitive Warning

struct PremiumTimeSensitiveWarning: View {
    let spot: LocationSpot
    let currentDate: Date
    @State private var isFlashing = false

    init(spot: LocationSpot, currentDate: Date = Date()) {
        self.spot = spot
        self.currentDate = currentDate
    }

    var body: some View {
        if let warning = closingWarning {
            HStack(spacing: DS.Spacing.xxs) {
                Image(systemName: "clock.badge.exclamationmark.fill")
                    .font(.system(size: 11, weight: .semibold))
                    .symbolEffect(.pulse, isActive: isFlashing)
                Text(warning)
                    .font(.system(size: 12, weight: .semibold, design: .rounded))
            }
            .foregroundStyle(DS.Colors.warning)
            .padding(.horizontal, DS.Spacing.sm)
            .padding(.vertical, DS.Spacing.xs)
            .background(
                Capsule()
                    .fill(DS.Colors.warning.opacity(0.15))
            )
            .onAppear { isFlashing = true }
            .accessibilityLabel(warning)
        }
    }

    private var closingWarning: String? {
        guard let hours = spot.operatingHours else { return nil }
        guard hours.isOpen(at: currentDate, calendar: .current) else { return nil }

        let calendar = Calendar.current
        let weekday = calendar.component(.weekday, from: currentDate)

        guard let todayHours = hours.hours(for: weekday) else { return nil }

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
            return "Closes in \(minutesUntilClose)m!"
        } else if minutesUntilClose <= 60 {
            return "Closes in ~1h"
        } else if minutesUntilClose <= 90 {
            return "Closes in ~1.5h"
        }
        return nil
    }
}

// MARK: - Premium Attribute Pill

struct PremiumAttributePill: View {
    let tag: AttributeTag
    let showLabel: Bool

    var body: some View {
        HStack(spacing: DS.Spacing.xxs) {
            Text(tag.emoji)
                .font(.system(size: 12))
            if showLabel {
                Text(tag.shortName)
                    .font(.system(size: 11, weight: .medium, design: .rounded))
            }
        }
        .padding(.horizontal, DS.Spacing.sm)
        .padding(.vertical, DS.Spacing.xs)
        .background(
            Capsule()
                .fill(attributeBackgroundColor)
        )
        .overlay(
            Capsule()
                .stroke(attributeBorderColor.opacity(0.2), lineWidth: 0.5)
        )
        .accessibilityLabel(tag.displayText)
    }

    private var attributeBackgroundColor: Color {
        switch tag {
        case .deepFocus, .powerHeavy:
            return DS.Colors.accentSlate.opacity(0.12)
        case .luxury, .eliteCoffee:
            return DS.Colors.accentGold.opacity(0.12)
        case .bodyDoubling:
            return DS.Colors.accentTeal.opacity(0.12)
        case .nightOwl, .earlyBird:
            return DS.Colors.accentAmber.opacity(0.12)
        default:
            return DS.Colors.glassBackground
        }
    }

    private var attributeBorderColor: Color {
        switch tag {
        case .deepFocus, .powerHeavy:
            return DS.Colors.accentSlate
        case .luxury, .eliteCoffee:
            return DS.Colors.accentGold
        case .bodyDoubling:
            return DS.Colors.accentTeal
        case .nightOwl, .earlyBird:
            return DS.Colors.accentAmber
        default:
            return .gray
        }
    }
}

// MARK: - Premium Distance Display

struct PremiumDistanceDisplay: View {
    let meters: Double?
    let showWalkTime: Bool

    init(meters: Double?, showWalkTime: Bool = false) {
        self.meters = meters
        self.showWalkTime = showWalkTime
    }

    var body: some View {
        if let meters {
            VStack(alignment: .trailing, spacing: 1) {
                Text(DistanceFormatter.format(meters: meters))
                    .font(.system(size: 13, weight: .bold, design: .rounded))
                    .foregroundStyle(.primary)

                if showWalkTime {
                    HStack(spacing: 2) {
                        Image(systemName: "figure.walk")
                            .font(.system(size: 9, weight: .medium))
                        Text(DistanceFormatter.estimatedTime(meters: meters, mode: .walking))
                            .font(.system(size: 10, weight: .medium, design: .rounded))
                    }
                    .foregroundStyle(.tertiary)
                }
            }
            .padding(.horizontal, DS.Spacing.sm)
            .padding(.vertical, DS.Spacing.xs)
            .background(
                Capsule()
                    .fill(DS.Colors.accentSlate.opacity(0.12))
            )
            .accessibilityLabel("Distance: \(DistanceFormatter.format(meters: meters))")
        }
    }
}

// MARK: - Premium Navigate Button

struct PremiumNavigateButton: View {
    let spot: LocationSpot
    let travelMode: TravelMode
    @State private var isPressed = false

    init(spot: LocationSpot, travelMode: TravelMode = .driving) {
        self.spot = spot
        self.travelMode = travelMode
    }

    var body: some View {
        Button(action: {
            HapticFeedback.medium()
            openInMaps()
        }) {
            HStack(spacing: DS.Spacing.xs) {
                Image(systemName: "arrow.triangle.turn.up.right.circle.fill")
                    .font(.system(size: 16, weight: .semibold))
                    .symbolEffect(.bounce, value: isPressed)
                Text("Navigate")
                    .font(.system(size: 14, weight: .semibold, design: .rounded))
            }
            .foregroundStyle(.white)
            .padding(.horizontal, DS.Spacing.md)
            .padding(.vertical, DS.Spacing.sm)
            .background(
                Capsule()
                    .fill(
                        LinearGradient(
                            colors: [DS.Colors.accentGold, DS.Colors.accentAmber],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
            )
            .shadow(color: DS.Colors.accentGold.opacity(0.4), radius: 8, x: 0, y: 4)
        }
        .buttonStyle(.plain)
        .scaleEffect(isPressed ? 0.95 : 1)
        .onLongPressGesture(minimumDuration: 0.1, pressing: { pressing in
            withAnimation(DS.Animation.quick) {
                isPressed = pressing
            }
        }, perform: {})
        .accessibilityLabel("Navigate to \(spot.name)")
        .accessibilityHint("Opens in Apple Maps")
    }

    private func openInMaps() {
        guard let coordinate = spot.coordinate else { return }
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

// MARK: - Preview

#Preview {
    ScrollView {
        VStack(spacing: DS.Spacing.md) {
            SpotCard(
                spot: LocationSpot.preview,
                distanceMeters: 1200,
                isFavorite: true,
                onFavorite: {},
                onTap: {}
            )

            SpotCard(
                spot: LocationSpot.previewReliable,
                distanceMeters: 5000,
                isFavorite: false,
                onFavorite: {},
                onTap: {}
            )
        }
        .padding(DS.Spacing.md)
    }
    .background(DS.Colors.backgroundPrimary)
    .preferredColorScheme(.dark)
}

// MARK: - Preview Helpers

private extension LocationSpot {
    static var preview: LocationSpot {
        LocationSpot(
            name: "Groundwork Coffee - Rose Ave",
            city: "Los Angeles",
            neighborhood: "Venice",
            placeType: .cafe,
            tier: .elite,
            sentimentScore: 9.0,
            costBasis: "$$",
            openLate: false,
            closeToHome: true,
            closeToWork: false,
            safeToLeaveComputer: false,
            walkingFriendlyLocation: true,
            exerciseWellnessAvailable: false,
            chargedLaptopBrickOnly: false,
            attributes: [.eliteCoffee, .deepFocus, .powerHeavy, .bodyDoubling, .patioPower],
            criticalFieldNotes: "One of Venice's most reliable work cafés: big patio, many plugs and very dependable wifi with a crowd that's almost all laptops and meetings.",
            status: "Active",
            latitude: 33.9925,
            longitude: -118.4695
        )
    }

    static var previewReliable: LocationSpot {
        LocationSpot(
            name: "Santa Monica Public Library",
            city: "Los Angeles",
            neighborhood: "Santa Monica",
            placeType: .library,
            tier: .reliable,
            sentimentScore: 8.0,
            costBasis: "Free",
            openLate: false,
            closeToHome: false,
            closeToWork: false,
            safeToLeaveComputer: false,
            walkingFriendlyLocation: true,
            exerciseWellnessAvailable: false,
            chargedLaptopBrickOnly: false,
            attributes: [.deepFocus, .patioPower],
            criticalFieldNotes: "Quiet, power-rich reading rooms plus a courtyard wifi signal; perfect when you want deep-focus script work.",
            status: "Active",
            latitude: 34.0142,
            longitude: -118.4921
        )
    }
}
