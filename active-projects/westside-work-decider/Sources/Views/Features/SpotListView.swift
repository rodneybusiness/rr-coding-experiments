import SwiftUI

struct SpotListView: View {
    @ObservedObject var store: SpotStore
    @ObservedObject var filters: QueryModel

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Filters bar
            FiltersBar(query: $filters.query)
                .padding(.horizontal)
                .padding(.top, 8)

            // Active filters summary
            ActiveFiltersSummary(query: filters.query, sort: filters.sort)
                .padding(.horizontal)
                .padding(.vertical, 4)

            // Sort picker
            Picker("Sort", selection: $filters.sort) {
                Text("Distance").tag(SpotSort.distance)
                Text("Sentiment").tag(SpotSort.sentiment)
                Text("Tier").tag(SpotSort.tier)
                Text("Time of day").tag(SpotSort.timeOfDay)
            }
            .pickerStyle(.segmented)
            .padding(.horizontal)
            .padding(.bottom, 8)
            .accessibilityLabel("Sort options")

            // Results count
            let results = store.apply(query: filters.query, sort: filters.sort)
            Text("\(results.count) spots")
                .font(.caption)
                .foregroundStyle(.secondary)
                .padding(.horizontal)
                .accessibilityLabel("\(results.count) spots found")

            // List
            List(results, id: \.id) { spot in
                let anchor = store.anchorLocation(for: filters.query)
                SpotCard(
                    spot: spot,
                    distanceMeters: spot.distance(from: anchor),
                    showNavigateButton: true,
                    isFavorite: spot.isFavorite,
                    onFavorite: { store.toggleFavorite(for: spot) },
                    onTap: { store.markVisited(spot) }
                )
                .listRowSeparator(.hidden)
                .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16))
            }
            .listStyle(.plain)
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Spot list view")
    }
}

// MARK: - Preview

#Preview {
    SpotListView(
        store: SpotStore(spots: []),
        filters: QueryModel()
    )
}
