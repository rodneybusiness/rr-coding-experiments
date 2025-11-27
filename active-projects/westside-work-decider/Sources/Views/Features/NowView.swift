import SwiftUI
import CoreLocation

struct NowView: View {
    @ObservedObject var store: SpotStore
    @ObservedObject var filters: QueryModel
    var onShowMap: () -> Void
    var onShowList: () -> Void

    @State private var selectedPreset: SessionPreset?

    @Environment(\.dynamicTypeSize) private var dynamicTypeSize

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Header
                headerSection

                // Active filters summary
                ActiveFiltersSummary(query: filters.query, sort: filters.sort)

                // Quick presets
                QuickActionsView(
                    presets: SessionPreset.defaults,
                    selected: $selectedPreset
                )
                .onChange(of: selectedPreset) { _, newValue in
                    filters.apply(preset: newValue)
                }

                // Results
                resultsSection

                // Actions
                actionButtons
            }
            .padding()
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Now view - Find your perfect work spot")
    }

    // MARK: - Subviews

    private var headerSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Where should I go right now?")
                .font(.largeTitle.bold())
                .accessibilityAddTraits(.isHeader)

            if let hour = Calendar.current.dateComponents([.hour], from: Date()).hour {
                Text(greetingForHour(hour))
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
        }
    }

    private var resultsSection: some View {
        let query = presetAdjustedQuery(selectedPreset)
        let results = store.apply(query: query, sort: filters.sort)
        let anchor = store.anchorLocation(for: query)

        return Group {
            if results.isEmpty {
                emptyStateView
            } else {
                // Show all matching spots in a vertical list
                VStack(spacing: 16) {
                    ForEach(results, id: \.id) { spot in
                        SpotCard(
                            spot: spot,
                            distanceMeters: spot.distance(from: anchor),
                            showNavigateButton: true,
                            isFavorite: spot.isFavorite,
                            onFavorite: { store.toggleFavorite(for: spot) },
                            onTap: { store.markVisited(spot) }
                        )
                    }
                }
            }
        }
    }

    private var emptyStateView: some View {
        VStack(spacing: 12) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 48))
                .foregroundStyle(.secondary)

            Text("No spots match your criteria")
                .font(.headline)

            Text("Try adjusting your filters or selecting a different preset")
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)

            Button("Clear Filters") {
                filters.clear()
                selectedPreset = nil
            }
            .buttonStyle(.bordered)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 40)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("No spots found. Try adjusting your filters.")
    }

    private var actionButtons: some View {
        HStack(spacing: 12) {
            Button {
                onShowMap()
            } label: {
                Label("Show Map", systemImage: "map")
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 14)
                            .fill(Color.blue.opacity(0.15))
                    )
            }
            .buttonStyle(.plain)
            .accessibilityLabel("Show all spots on map")

            Button {
                onShowList()
            } label: {
                Label("Full List", systemImage: "list.bullet")
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 14)
                            .fill(Color.gray.opacity(0.15))
                    )
            }
            .buttonStyle(.plain)
            .accessibilityLabel("Show full list of spots")
        }
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
}

// MARK: - Quick Actions View

private struct QuickActionsView: View {
    let presets: [SessionPreset]
    @Binding var selected: SessionPreset?

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(presets) { preset in
                    PresetButton(
                        preset: preset,
                        isSelected: selected?.id == preset.id,
                        onTap: { selected = preset }
                    )
                }
            }
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Quick presets")
    }
}

private struct PresetButton: View {
    let preset: SessionPreset
    let isSelected: Bool
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            VStack(alignment: .leading, spacing: 4) {
                Text(preset.title)
                    .font(.headline)
                    .foregroundStyle(.primary)

                Text(preset.description)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }
            .padding()
            .frame(width: 160, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 14)
                    .fill(isSelected ? Color.blue.opacity(0.2) : Color.gray.opacity(0.12))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 14)
                    .stroke(isSelected ? Color.blue : Color.clear, lineWidth: 2)
            )
        }
        .buttonStyle(.plain)
        .accessibilityLabel("\(preset.title): \(preset.description)")
        .accessibilityAddTraits(isSelected ? [.isSelected] : [])
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
}
