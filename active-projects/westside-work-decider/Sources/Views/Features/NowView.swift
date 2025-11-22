import SwiftUI
import CoreLocation
import UIKit

struct NowView: View {
    @ObservedObject var store: SpotStore
    @ObservedObject var queryModel: SpotQueryModel
    var quickPresets: [SessionPreset] = [
        SessionPreset(title: "Deep Focus", description: "Quiet, power + focus heavy", tags: [.deepFocus, .powerHeavy], requiresOpenLate: false, prefersElite: false),
        SessionPreset(title: "Body Doubling", description: "Social energy, good wifi", tags: [.bodyDoubling], requiresOpenLate: false, prefersElite: false),
        SessionPreset(title: "Quick Sprint", description: "≤90m, low friction", tags: [.easyParking], requiresOpenLate: false, prefersElite: false),
        SessionPreset(title: "Late Night", description: "Open late + safe", tags: [.nightOwl], requiresOpenLate: true, prefersElite: false)
    ]

    @State private var selectedPreset: SessionPreset?
    @State private var sort: SpotSort = .timeOfDay
    @State private var showFullList = false
    @State private var activeSpotID: LocationSpot.ID?

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    Text("Where should I go right now?")
                        .font(.largeTitle.bold())

                    QuickActionsView(presets: quickPresets, selected: $selectedPreset) { preset in
                        queryModel.applyPreset(preset)
                    }

                    let results = store.apply(query: queryModel.query, sort: sort)
                    if let topThree = results.prefix(3).nilIfEmpty() {
                        TabView(selection: $activeSpotID) {
                            ForEach(topThree, id: \.id) { spot in
                                SpotCard(
                                    spot: spot,
                                    distanceText: formattedDistance(for: spot),
                                    frictionBadge: frictionBadge(for: spot)
                                )
                                .tag(spot.id)
                            }
                        }
                        .tabViewStyle(.page(indexDisplayMode: .always))
                        .frame(height: 260)
                        .animation(.easeInOut, value: selectedPreset?.id)
                        .animation(.spring(response: 0.35, dampingFraction: 0.85), value: activeSpotID)
                        .onAppear { activeSpotID = activeSpotID ?? topThree.first?.id }
                        .onChange(of: topThree.map(\.id)) { ids in
                            activeSpotID = ids.first
                        }
                        .onChange(of: activeSpotID) { _ in
                            UIImpactFeedbackGenerator(style: .light).impactOccurred()
                        }
                    }

                    Button {
                        if let preset = selectedPreset {
                            queryModel.applyPreset(preset)
                        }
                        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
                        showFullList = true
                    } label: {
                        Label("Show map & full list", systemImage: "map")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(RoundedRectangle(cornerRadius: 14).fill(Color.blue.opacity(0.15)))
                    }
                }
                .padding()
            }
            .navigationDestination(isPresented: $showFullList) {
                SpotListView(store: store, queryModel: queryModel)
            }
        }
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
    var onSelect: (SessionPreset) -> Void

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(presets) { preset in
                    Button {
                        withAnimation(.spring(response: 0.35, dampingFraction: 0.78)) {
                            selected = preset
                        }
                        UISelectionFeedbackGenerator().selectionChanged()
                        onSelect(preset)
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
