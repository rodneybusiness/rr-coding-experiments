import SwiftUI
import CoreLocation

struct NowView: View {
    @ObservedObject var store: SpotStore
    var quickPresets: [SessionPreset] = [
        SessionPreset(title: "Deep Focus", description: "Quiet, power + focus heavy", tags: [.deepFocus, .powerHeavy], requiresOpenLate: false, prefersElite: false),
        SessionPreset(title: "Body Doubling", description: "Social energy, good wifi", tags: [.bodyDoubling], requiresOpenLate: false, prefersElite: false),
        SessionPreset(title: "Quick Sprint", description: "≤90m, low friction", tags: [.easyParking], requiresOpenLate: false, prefersElite: false),
        SessionPreset(title: "Late Night", description: "Open late + safe", tags: [.nightOwl], requiresOpenLate: true, prefersElite: false)
    ]

    @State private var selectedPreset: SessionPreset?
    @State private var sort: SpotSort = .timeOfDay

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Where should I go right now?")
                    .font(.largeTitle.bold())

                QuickActionsView(presets: quickPresets, selected: $selectedPreset)

                let query = queryFromPreset(selectedPreset)
                let results = store.apply(query: query, sort: sort)
                if let topThree = results.prefix(3).nilIfEmpty() {
                    TabView {
                        ForEach(topThree, id: \.id) { spot in
                            SpotCard(
                                spot: spot,
                                distanceText: formattedDistance(for: spot),
                                frictionBadge: frictionBadge(for: spot)
                            )
                        }
                    }
                    .tabViewStyle(.page(indexDisplayMode: .always))
                    .frame(height: 260)
                }

                Button {
                    // navigate to map/list in real app
                } label: {
                    Label("Show map & full list", systemImage: "map")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(RoundedRectangle(cornerRadius: 14).fill(Color.blue.opacity(0.15)))
                }
            }
            .padding()
        }
    }

    private func queryFromPreset(_ preset: SessionPreset?) -> SpotQuery {
        guard let preset else { return SpotQuery() }
        var query = SpotQuery()
        query.attributes = preset.tags
        if preset.requiresOpenLate { query.openLate = true }
        if preset.prefersElite { query.tiers.insert(.elite) }
        return query
    }

    private func formattedDistance(for spot: LocationSpot) -> String? {
        guard let distance = spot.distance(from: store.location) else { return nil }
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
