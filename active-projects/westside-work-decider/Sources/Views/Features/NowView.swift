import SwiftUI
import CoreLocation

// MARK: - Premium NowView 2025

struct NowView: View {
    @ObservedObject var store: SpotStore
    @ObservedObject var filters: QueryModel
    var onShowMap: () -> Void
    var onShowList: () -> Void

    @State private var selectedPreset: SessionPreset?
    @State private var hasAppeared = false
    @State private var headerScale: CGFloat = 0.9
    @State private var headerOpacity: CGFloat = 0

    @Environment(\.dynamicTypeSize) private var dynamicTypeSize

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: DS.Spacing.lg) {
                // Hero header with dramatic animation
                heroHeaderSection
                    .padding(.top, DS.Spacing.md)

                // Active filters summary (glass style)
                ActiveFiltersSummary(query: filters.query, sort: filters.sort)

                // Quick presets with premium design
                PremiumQuickActionsView(
                    presets: SessionPreset.defaults,
                    selected: $selectedPreset
                )
                .onChange(of: selectedPreset) { _, newValue in
                    HapticFeedback.selection()
                    filters.apply(preset: newValue)
                }

                // Results section with staggered animations
                resultsSection

                // Premium action buttons
                premiumActionButtons
            }
            .padding(.horizontal, DS.Spacing.md)
            .padding(.bottom, DS.Spacing.xxl)
        }
        .background(backgroundGradient)
        .onAppear {
            withAnimation(DS.Animation.springy.delay(0.1)) {
                hasAppeared = true
                headerScale = 1
                headerOpacity = 1
            }
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Now view - Find your perfect work spot")
    }

    // MARK: - Background

    private var backgroundGradient: some View {
        ZStack {
            // Base color
            Color(uiColor: .systemBackground)

            // Subtle gradient overlay - warm luxury tones
            LinearGradient(
                colors: [
                    DS.Colors.accentGold.opacity(0.025),
                    Color.clear,
                    DS.Colors.accentSlate.opacity(0.02)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        }
        .ignoresSafeArea()
    }

    // MARK: - Hero Header

    private var heroHeaderSection: some View {
        VStack(alignment: .leading, spacing: DS.Spacing.sm) {
            // Time-based greeting with subtle animation
            if let hour = Calendar.current.dateComponents([.hour], from: Date()).hour {
                HStack(spacing: DS.Spacing.xs) {
                    Image(systemName: greetingIcon(for: hour))
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundStyle(greetingColor(for: hour))
                        .symbolEffect(.pulse)
                    Text(greetingForHour(hour))
                        .font(.system(size: 15, weight: .medium, design: .rounded))
                        .foregroundStyle(.secondary)
                }
                .opacity(headerOpacity)
            }

            // Hero title with dramatic typography
            Text("Where should I\ngo right now?")
                .font(.system(size: 36, weight: .bold, design: .default))
                .tracking(-0.5)
                .lineSpacing(-4)
                .foregroundStyle(
                    LinearGradient(
                        colors: [.primary, .primary.opacity(0.8)],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
                .scaleEffect(headerScale, anchor: .leading)
                .opacity(headerOpacity)
                .accessibilityAddTraits(.isHeader)

            // Subtle context line
            Text("\(store.openSpots(for: filters.query).count) spots open now")
                .font(.system(size: 14, weight: .medium, design: .rounded))
                .foregroundStyle(DS.Colors.accentGold)
                .opacity(headerOpacity)
        }
    }

    // MARK: - Results Section

    private var resultsSection: some View {
        let query = presetAdjustedQuery(selectedPreset)
        let results = store.apply(query: query, sort: filters.sort)
        let anchor = store.anchorLocation(for: query)

        return Group {
            if results.isEmpty {
                premiumEmptyStateView
            } else {
                VStack(spacing: DS.Spacing.md) {
                    // Section header
                    HStack {
                        Text("Recommended")
                            .font(.system(size: 13, weight: .bold, design: .rounded))
                            .textCase(.uppercase)
                            .tracking(1)
                            .foregroundStyle(.secondary)
                        Spacer()
                        Text("\(results.count) spots")
                            .font(.system(size: 12, weight: .medium, design: .rounded))
                            .foregroundStyle(.tertiary)
                    }
                    .opacity(hasAppeared ? 1 : 0)

                    // Staggered card list
                    ForEach(Array(results.enumerated()), id: \.element.id) { index, spot in
                        SpotCard(
                            spot: spot,
                            distanceMeters: spot.distance(from: anchor),
                            showNavigateButton: true,
                            isFavorite: spot.isFavorite,
                            onFavorite: { store.toggleFavorite(for: spot) },
                            onTap: { store.markVisited(spot) }
                        )
                        .opacity(hasAppeared ? 1 : 0)
                        .offset(y: hasAppeared ? 0 : 30)
                        .animation(
                            DS.Animation.springy.delay(Double(index) * 0.08),
                            value: hasAppeared
                        )
                    }
                }
            }
        }
    }

    // MARK: - Empty State

    private var premiumEmptyStateView: some View {
        VStack(spacing: DS.Spacing.lg) {
            // Animated icon
            ZStack {
                Circle()
                    .fill(DS.Colors.accentGold.opacity(0.1))
                    .frame(width: 100, height: 100)

                Image(systemName: "magnifyingglass")
                    .font(.system(size: 40, weight: .medium))
                    .foregroundStyle(DS.Colors.accentGold.opacity(0.6))
                    .symbolEffect(.pulse)
            }

            VStack(spacing: DS.Spacing.xs) {
                Text("No spots match")
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundStyle(.primary)

                Text("Try adjusting your filters or selecting a different preset")
                    .font(.system(size: 14, weight: .regular, design: .rounded))
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, DS.Spacing.xl)
            }

            Button {
                HapticFeedback.light()
                filters.clear()
                selectedPreset = nil
            } label: {
                Text("Clear Filters")
                    .font(.system(size: 14, weight: .semibold, design: .rounded))
                    .foregroundStyle(DS.Colors.accentGold)
                    .padding(.horizontal, DS.Spacing.lg)
                    .padding(.vertical, DS.Spacing.sm)
                    .background(
                        Capsule()
                            .fill(DS.Colors.accentGold.opacity(0.12))
                    )
            }
            .buttonStyle(.plain)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, DS.Spacing.xxxl)
        .glassCard()
        .accessibilityElement(children: .combine)
        .accessibilityLabel("No spots found. Try adjusting your filters.")
    }

    // MARK: - Action Buttons

    private var premiumActionButtons: some View {
        HStack(spacing: DS.Spacing.sm) {
            PremiumActionButton(
                title: "Map",
                icon: "map.fill",
                gradient: [DS.Colors.accentGold, DS.Colors.accentAmber],
                action: {
                    HapticFeedback.light()
                    onShowMap()
                }
            )

            PremiumActionButton(
                title: "Full List",
                icon: "list.bullet",
                gradient: [.gray.opacity(0.3), .gray.opacity(0.2)],
                isSecondary: true,
                action: {
                    HapticFeedback.light()
                    onShowList()
                }
            )
        }
        .opacity(hasAppeared ? 1 : 0)
        .offset(y: hasAppeared ? 0 : 20)
        .animation(DS.Animation.springy.delay(0.3), value: hasAppeared)
    }

    // MARK: - Helpers

    private func presetAdjustedQuery(_ preset: SessionPreset?) -> SpotQuery {
        guard let preset else { return filters.query }
        var query = filters.query
        query.attributes.formUnion(preset.tags)
        if preset.requiresOpenLate { query.openLate = true }
        if preset.prefersElite { query.tiers.insert(.elite) }
        return query
    }

    private func greetingForHour(_ hour: Int) -> String {
        switch hour {
        case 0..<6:
            return "Late night session? Here are spots open now."
        case 6..<12:
            return "Good morning! Great time for focused work."
        case 12..<14:
            return "Lunchtime - spots with real food recommended."
        case 14..<17:
            return "Afternoon productivity boost incoming."
        case 17..<21:
            return "Evening session - showing spots still open."
        default:
            return "Night owl mode - late-night friendly spots."
        }
    }

    private func greetingIcon(for hour: Int) -> String {
        switch hour {
        case 0..<6: return "moon.stars.fill"
        case 6..<12: return "sunrise.fill"
        case 12..<14: return "sun.max.fill"
        case 14..<17: return "sun.haze.fill"
        case 17..<21: return "sunset.fill"
        default: return "moon.fill"
        }
    }

    private func greetingColor(for hour: Int) -> Color {
        switch hour {
        case 0..<6: return DS.Colors.accentSlate
        case 6..<12: return DS.Colors.accentGold
        case 12..<14: return DS.Colors.accentAmber
        case 14..<17: return DS.Colors.accentGold
        case 17..<21: return DS.Colors.accentAmber
        default: return DS.Colors.accentSlate
        }
    }
}

// MARK: - Premium Quick Actions View

private struct PremiumQuickActionsView: View {
    let presets: [SessionPreset]
    @Binding var selected: SessionPreset?
    @State private var hasAppeared = false

    var body: some View {
        VStack(alignment: .leading, spacing: DS.Spacing.sm) {
            Text("Quick Start")
                .font(.system(size: 13, weight: .bold, design: .rounded))
                .textCase(.uppercase)
                .tracking(1)
                .foregroundStyle(.secondary)
                .opacity(hasAppeared ? 1 : 0)

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: DS.Spacing.sm) {
                    ForEach(Array(presets.enumerated()), id: \.element.id) { index, preset in
                        PremiumPresetButton(
                            preset: preset,
                            isSelected: selected?.id == preset.id,
                            onTap: { selected = preset }
                        )
                        .opacity(hasAppeared ? 1 : 0)
                        .offset(x: hasAppeared ? 0 : 20)
                        .animation(
                            DS.Animation.springy.delay(Double(index) * 0.05),
                            value: hasAppeared
                        )
                    }
                }
                .padding(.vertical, DS.Spacing.xxs)
            }
        }
        .onAppear {
            withAnimation(DS.Animation.springy.delay(0.2)) {
                hasAppeared = true
            }
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Quick presets")
    }
}

// MARK: - Premium Preset Button

private struct PremiumPresetButton: View {
    let preset: SessionPreset
    let isSelected: Bool
    let onTap: () -> Void
    @State private var isPressed = false

    var body: some View {
        Button(action: onTap) {
            VStack(alignment: .leading, spacing: DS.Spacing.xs) {
                // Icon + Title row
                HStack(spacing: DS.Spacing.xs) {
                    Image(systemName: presetIcon)
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundStyle(isSelected ? Color(hex: "1A1A1F") : DS.Colors.accentGold)

                    Text(preset.title)
                        .font(.system(size: 15, weight: .semibold, design: .rounded))
                        .foregroundStyle(isSelected ? Color(hex: "1A1A1F") : .primary)
                }

                Text(preset.description)
                    .font(.system(size: 12, weight: .regular, design: .rounded))
                    .foregroundStyle(isSelected ? Color(hex: "1A1A1F").opacity(0.7) : .secondary)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(DS.Spacing.sm)
            .frame(width: 150, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: DS.Radius.md, style: .continuous)
                    .fill(isSelected ? DS.Gradients.heroGradient : LinearGradient(colors: [Color.clear], startPoint: .top, endPoint: .bottom))
            )
            .background(
                RoundedRectangle(cornerRadius: DS.Radius.md, style: .continuous)
                    .fill(.ultraThinMaterial)
            )
            .overlay(
                RoundedRectangle(cornerRadius: DS.Radius.md, style: .continuous)
                    .stroke(
                        isSelected
                            ? Color.white.opacity(0.3)
                            : Color.gray.opacity(0.2),
                        lineWidth: isSelected ? 1 : 0.5
                    )
            )
            .shadow(
                color: isSelected ? DS.Colors.accentGold.opacity(0.35) : .clear,
                radius: 12,
                x: 0,
                y: 6
            )
        }
        .buttonStyle(.plain)
        .scaleEffect(isPressed ? 0.96 : 1)
        .animation(DS.Animation.quick, value: isPressed)
        .onLongPressGesture(minimumDuration: 0.1, pressing: { pressing in
            isPressed = pressing
        }, perform: {})
        .accessibilityLabel("\(preset.title): \(preset.description)")
        .accessibilityAddTraits(isSelected ? [.isSelected] : [])
    }

    private var presetIcon: String {
        switch preset.title.lowercased() {
        case let t where t.contains("focus"): return "brain.head.profile"
        case let t where t.contains("body"): return "person.2.fill"
        case let t where t.contains("sprint"): return "bolt.fill"
        case let t where t.contains("night"): return "moon.fill"
        default: return "sparkles"
        }
    }
}

// MARK: - Premium Action Button

private struct PremiumActionButton: View {
    let title: String
    let icon: String
    let gradient: [Color]
    var isSecondary: Bool = false
    let action: () -> Void

    @State private var isPressed = false

    var body: some View {
        Button(action: action) {
            HStack(spacing: DS.Spacing.xs) {
                Image(systemName: icon)
                    .font(.system(size: 16, weight: .semibold))
                    .symbolEffect(.bounce, value: isPressed)
                Text(title)
                    .font(.system(size: 15, weight: .semibold, design: .rounded))
            }
            .foregroundStyle(isSecondary ? .primary : .white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, DS.Spacing.md)
            .background(
                RoundedRectangle(cornerRadius: DS.Radius.md, style: .continuous)
                    .fill(
                        isSecondary
                            ? AnyShapeStyle(.ultraThinMaterial)
                            : AnyShapeStyle(LinearGradient(colors: gradient, startPoint: .leading, endPoint: .trailing))
                    )
            )
            .overlay(
                RoundedRectangle(cornerRadius: DS.Radius.md, style: .continuous)
                    .stroke(Color.white.opacity(isSecondary ? 0.1 : 0.2), lineWidth: 0.5)
            )
            .shadow(
                color: isSecondary ? .clear : gradient.first?.opacity(0.3) ?? .clear,
                radius: 12,
                x: 0,
                y: 6
            )
        }
        .buttonStyle(.plain)
        .scaleEffect(isPressed ? 0.97 : 1)
        .animation(DS.Animation.quick, value: isPressed)
        .onLongPressGesture(minimumDuration: 0.1, pressing: { pressing in
            isPressed = pressing
        }, perform: {})
    }
}

// MARK: - SpotStore Extension

extension SpotStore {
    func openSpots(for query: SpotQuery) -> [LocationSpot] {
        let now = Date()
        return apply(query: query, sort: .distance).filter { spot in
            spot.operatingHours?.isOpen(at: now, calendar: .current) ?? true
        }
    }
}

// MARK: - Preview

#Preview {
    NowView(
        store: SpotStore(spots: []),
        filters: QueryModel(),
        onShowMap: {},
        onShowList: {}
    )
    .preferredColorScheme(.dark)
}
