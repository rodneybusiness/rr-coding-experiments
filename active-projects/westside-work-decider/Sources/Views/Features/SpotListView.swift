import SwiftUI

struct SpotListView: View {
    @ObservedObject var store: SpotStore
    @ObservedObject var filters: QueryModel

    var body: some View {
        VStack(alignment: .leading) {
            FiltersBar(query: $filters.query)
                .padding(.horizontal)
            Picker("Sort", selection: $filters.sort) {
                Text("Distance").tag(SpotSort.distance)
                Text("Sentiment").tag(SpotSort.sentiment)
                Text("Tier").tag(SpotSort.tier)
                Text("Time of day").tag(SpotSort.timeOfDay)
            }
            .pickerStyle(.segmented)
            .padding(.horizontal)

            List(store.apply(query: filters.query, sort: filters.sort), id: \.id) { spot in
                SpotCard(
                    spot: spot,
                    distanceText: formattedDistance(for: spot),
                    frictionBadge: frictionBadge(for: spot),
                    isFavorite: spot.isFavorite,
                    onFavorite: { store.toggleFavorite(for: spot) },
                    onTap: { store.markVisited(spot) }
                )
                .listRowSeparator(.hidden)
            }
            .listStyle(.plain)
        }
    }

    private func formattedDistance(for spot: LocationSpot) -> String? {
        guard let distance = spot.distance(from: store.anchorLocation(for: filters.query)) else { return nil }
        let miles = distance / 1609.34
        return String(format: "%.1f mi", miles)
    }

    private func frictionBadge(for spot: LocationSpot) -> String? {
        if spot.chargedLaptopBrickOnly { return "Charge before you go" }
        if !spot.attributes.contains(.easyParking) && !spot.walkingFriendlyLocation { return "Parking may be tricky" }
        return nil
    }
}
