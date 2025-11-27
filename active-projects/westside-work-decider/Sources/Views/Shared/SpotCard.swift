import SwiftUI
import CoreLocation

struct SpotCard: View {
    let spot: LocationSpot
    let distanceMeters: Double?
    let showNavigateButton: Bool
    var isFavorite: Bool = false
    var onFavorite: (() -> Void)? = nil
    var onTap: (() -> Void)? = nil

    @Environment(\.dynamicTypeSize) private var dynamicTypeSize

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
        // Convert distanceText back to meters (approximate)
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
        VStack(alignment: .leading, spacing: 10) {
            // Header row: Name, badges, favorite
            headerRow

            // Subtitle row: neighborhood, type, tier
            subtitleRow

            // Status row: open/closed, time warning
            statusRow

            // Notes
            Text(spot.criticalFieldNotes)
                .font(.footnote)
                .foregroundStyle(.primary)
                .lineLimit(dynamicTypeSize > .large ? 4 : 3)
                .fixedSize(horizontal: false, vertical: true)

            // Attributes
            attributeRow

            // Last visited
            if let lastVisited = spot.lastVisited {
                Label(
                    RelativeTimeFormatter.lastVisited(lastVisited) ?? "",
                    systemImage: "clock.arrow.circlepath"
                )
                .font(.caption)
                .foregroundStyle(.secondary)
            }

            // Friction warning
            frictionRow

            // Navigate button
            if showNavigateButton {
                HStack {
                    Spacer()
                    NavigateButton(spot: spot, travelMode: .driving)
                }
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(Color(uiColor: .secondarySystemBackground))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .stroke(tierBorderColor.opacity(0.3), lineWidth: 2)
        )
        .shadow(color: .black.opacity(0.05), radius: 4, x: 0, y: 2)
        .contentShape(Rectangle())
        .onTapGesture { onTap?() }
        .accessibilityElement(children: .combine)
        .accessibilityLabel(accessibilityDescription)
        .accessibilityHint("Double tap to mark as visited")
        .accessibilityAddTraits(.isButton)
    }

    // MARK: - Subviews

    private var headerRow: some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 4) {
                Text(spot.name)
                    .font(.headline)
                    .foregroundStyle(.primary)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Spacer()

            if let distanceMeters {
                DistanceDisplay(meters: distanceMeters, showWalkTime: distanceMeters < 2000)
            }

            if let onFavorite {
                Button(action: onFavorite) {
                    Image(systemName: isFavorite ? "heart.fill" : "heart")
                        .font(.title3)
                        .foregroundStyle(isFavorite ? .red : .secondary)
                }
                .buttonStyle(.plain)
                .accessibilityLabel(isFavorite ? "Remove from favorites" : "Add to favorites")
            }
        }
    }

    private var subtitleRow: some View {
        HStack(spacing: 8) {
            // Place type icon
            Label {
                Text(spot.neighborhood)
                    .font(.subheadline)
            } icon: {
                Image(systemName: placeTypeIcon)
                    .foregroundStyle(.secondary)
            }
            .foregroundStyle(.secondary)

            Text("•")
                .foregroundStyle(.tertiary)

            Text(spot.placeType.rawValue)
                .font(.subheadline)
                .foregroundStyle(.secondary)

            Spacer()

            TierBadge(tier: spot.tier)
        }
    }

    private var statusRow: some View {
        HStack(spacing: 12) {
            OpenClosedBadge(spot: spot)
            TimeSensitiveWarning(spot: spot)
            Spacer()
        }
    }

    private var attributeRow: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 6) {
                ForEach(spot.attributes.prefix(6)) { tag in
                    HStack(spacing: 4) {
                        Text(tag.emoji)
                        if dynamicTypeSize <= .large {
                            Text(tag.shortName)
                                .font(.caption)
                        }
                    }
                    .padding(.horizontal, 8)
                    .padding(.vertical, 6)
                    .background(
                        Capsule()
                            .fill(attributeBackgroundColor(for: tag))
                    )
                    .accessibilityLabel(tag.displayText)
                }
            }
        }
    }

    private var frictionRow: some View {
        Group {
            if let warning = FrictionBadge.evaluate(for: spot) {
                Label(warning.message, systemImage: warning.icon)
                    .font(.caption.weight(.medium))
                    .foregroundStyle(warning.severity == .high ? .red : .orange)
                    .padding(.vertical, 4)
            }
        }
    }

    // MARK: - Helpers

    private var placeTypeIcon: String {
        switch spot.placeType {
        case .coffeeShop: return "cup.and.saucer.fill"
        case .coworking: return "building.2.fill"
        case .library: return "books.vertical.fill"
        case .hotel: return "building.fill"
        case .cafe: return "fork.knife"
        case .other: return "mappin.circle.fill"
        }
    }

    private var tierBorderColor: Color {
        switch spot.tier {
        case .elite: return .purple
        case .solid: return .blue
        case .local: return .orange
        }
    }

    private func attributeBackgroundColor(for tag: AttributeTag) -> Color {
        switch tag {
        case .deepFocus, .powerHeavy:
            return .blue.opacity(0.12)
        case .luxury, .eliteCoffee:
            return .purple.opacity(0.12)
        case .bodyDoubling:
            return .green.opacity(0.12)
        case .nightOwl, .earlyBird:
            return .orange.opacity(0.12)
        default:
            return .gray.opacity(0.12)
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

// MARK: - Preview

#Preview {
    ScrollView {
        VStack(spacing: 16) {
            SpotCard(
                spot: LocationSpot.preview,
                distanceMeters: 1200,
                isFavorite: true,
                onFavorite: {},
                onTap: {}
            )

            SpotCard(
                spot: LocationSpot.preview,
                distanceMeters: 5000,
                isFavorite: false,
                onFavorite: {},
                onTap: {}
            )
        }
        .padding()
    }
}

// MARK: - Preview Helper

private extension LocationSpot {
    static var preview: LocationSpot {
        LocationSpot(
            id: "preview-1",
            name: "Blue Bottle Coffee - Venice",
            neighborhood: "Venice",
            latitude: 33.9925,
            longitude: -118.4695,
            placeType: .coffeeShop,
            tier: .elite,
            sentimentScore: 4.5,
            criticalFieldNotes: "Excellent pour-over, quiet back room perfect for focus work. Gets crowded after 10am.",
            safeToLeaveComputer: true,
            openLate: false,
            closeToHome: true,
            closeToWork: false,
            walkingFriendlyLocation: true,
            exerciseWellnessAvailable: false,
            chargedLaptopBrickOnly: false,
            attributes: [.eliteCoffee, .deepFocus, .powerHeavy]
        )
    }
}
