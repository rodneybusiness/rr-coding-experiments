import SwiftUI
import CoreLocation

struct NowView: View {
    @ObservedObject var store: SpotStore
    @ObservedObject var filters: QueryModel
    var onShowMap: () -> Void
    var onShowList: () -> Void
    var quickPresets: [SessionPreset] = [
        SessionPreset(title: "Deep Focus", description: "Quiet, power + focus heavy", tags: [.deepFocus, .powerHeavy], requiresOpenLate: false, prefersElite: false),
        SessionPreset(title: "Body Doubling", description: "Social energy, good wifi", tags: [.bodyDoubling], requiresOpenLate: false, prefersElite: false),
        SessionPreset(title: "Quick Sprint", description: "≤90m, low friction", tags: [.easyParking], requiresOpenLate: false, prefersElite: false),
        SessionPreset(title: "Late Night", description: "Open late + safe", tags: [.nightOwl], requiresOpenLate: true, prefersElite: false)
    ]

    @State private var selectedPreset: SessionPreset?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Where should I go right now?")
                    .font(.largeTitle.bold())

                QuickActionsView(presets: quickPresets, selected: $selectedPreset)
                    .onChange(of: selectedPreset) { _, newValue in
                        filters.apply(preset: newValue)
                    }

                let query = presetAdjustedQuery(selectedPreset)
                let results = store.apply(query: query, sort: filters.sort)
                if let topThree = results.prefix(3).nilIfEmpty() {
                    TabView {
                        ForEach(topThree, id: \.id) { spot in
                            SpotCard(
                                spot: spot,
                                distanceText: formattedDistance(for: spot, query: query),
                                frictionBadge: frictionBadge(for: spot),
                                isFavorite: spot.isFavorite,
                                onFavorite: { store.toggleFavorite(for: spot) },
                                onTap: { store.markVisited(spot) }
                            )
                        }
                    }
                    .tabViewStyle(.page(indexDisplayMode: .always))
                    .frame(height: 260)
                }

                Button {
                    onShowMap()
                } label: {
                    Label("Show map & full list", systemImage: "map")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(RoundedRectangle(cornerRadius: 14).fill(Color.blue.opacity(0.15)))
                }
                .buttonStyle(.plain)
            }
            .padding()
        }
    }

    private func presetAdjustedQuery(_ preset: SessionPreset?) -> SpotQuery {
        guard let preset else { return filters.query }
        var query = filters.query
        query.attributes.formUnion(preset.tags)
        if preset.requiresOpenLate { query.openLate = true }
        if preset.prefersElite { query.tiers.insert(.elite) }
        return query
    }

    private func formattedDistance(for spot: LocationSpot, query: SpotQuery) -> String? {
        guard let distance = spot.distance(from: store.anchorLocation(for: query)) else { return nil }
        let miles = distance / 1609.34
        return String(format: "%.1f mi", miles)
    }

    private func frictionBadge(for spot: LocationSpot) -> String? {
        if spot.chargedLaptopBrickOnly {
            return "Charge before you go"
        }
        if !spot.attributes.contains(.easyParking) && !spot.walkingFriendlyLocation {
            return "Parking may be tricky"
        }
        return nil
    }
}

private struct QuickActionsView: View {
    let presets: [SessionPreset]
    @Binding var selected: SessionPreset?

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(presets) { preset in
                    Button {
                        selected = preset
                    } label: {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(preset.title)
                                .font(.headline)
                            Text(preset.description)
                                .font(.footnote)
                                .foregroundStyle(.secondary)
                        }
                        .padding()
                        .frame(width: 180, alignment: .leading)
                        .background(RoundedRectangle(cornerRadius: 14).fill(selected?.id == preset.id ? Color.blue.opacity(0.2) : Color.gray.opacity(0.12)))
                    }
                }
            }
        }
    }
}

private extension Collection {
    func nilIfEmpty() -> Self? { isEmpty ? nil : self }
}
