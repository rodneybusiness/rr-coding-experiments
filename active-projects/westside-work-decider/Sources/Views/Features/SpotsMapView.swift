import SwiftUI
import MapKit

struct SpotsMapView: View {
    @ObservedObject var store: SpotStore
    @ObservedObject var filters: QueryModel
    @State private var mapCameraPosition = MapCameraPosition.region(
        MKCoordinateRegion(
            center: CLLocationCoordinate2D(latitude: 34.016, longitude: -118.45),
            span: MKCoordinateSpan(latitudeDelta: 0.12, longitudeDelta: 0.12)
        )
    )
    @State private var selectedSpotID: String?

    var body: some View {
        VStack(spacing: 0) {
            FiltersBar(query: $filters.query)
                .padding(.horizontal)
            ActiveFiltersSummary(query: filters.query, sort: filters.sort)
                .padding(.horizontal)

            let anchor = store.anchorLocation(for: filters.query)
            let mappedSpots = store.apply(query: filters.query, sort: .distance).compactMap { spot -> (LocationSpot, CLLocationCoordinate2D, CLLocationDistance?)? in
                guard let coordinate = coordinate(for: spot) else { return nil }
                return (spot, coordinate, spot.distance(from: anchor))
            }
            let mappedIDs = mappedSpots.map { $0.0.id }.joined(separator: ",")

            if mappedSpots.isEmpty {
                ContentUnavailableView(
                    "No map points yet",
                    systemImage: "mappin.slash",
                    description: Text("Add latitude/longitude to the dataset or run one-time geocoding to see pins.")
                )
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                let sortedSpots = mappedSpots.sorted { lhs, rhs in
                    switch (lhs.2, rhs.2) {
                    case let (l?, r?):
                        return l < r
                    case (.some, .none):
                        return true
                    case (.none, .some):
                        return false
                    default:
                        return lhs.0.name < rhs.0.name
                    }
                }

                Map(position: $mapCameraPosition, selection: $selectedSpotID) {
                    ForEach(sortedSpots, id: \.0.id) { entry in
                        Annotation(entry.0.name, coordinate: entry.1) {
                            ZStack {
                                Circle()
                                    .fill(selectedSpotID == entry.0.id ? Color.blue : Color.accentColor)
                                    .frame(width: 12, height: 12)
                                Circle()
                                    .stroke(Color.white, lineWidth: 2)
                                    .frame(width: 16, height: 16)
                            }
                        }
                        .tag(entry.0.id)
                    }
                }
                .mapStyle(.standard(elevation: .realistic))
                .onAppear { recenter(on: sortedSpots) }
                .onChange(of: mappedIDs) { _ in recenter(on: sortedSpots) }
                .safeAreaInset(edge: .bottom) {
                    bottomSheet(spots: sortedSpots)
                }
                .overlay(alignment: .topTrailing) {
                    if let selected = sortedSpots.first(where: { $0.0.id == selectedSpotID })?.0 {
                        callout(for: selected)
                            .padding()
                    }
                }
            }
        }
    }

    private func coordinate(for spot: LocationSpot) -> CLLocationCoordinate2D? {
        guard let lat = spot.latitude, let lon = spot.longitude else { return nil }
        return CLLocationCoordinate2D(latitude: lat, longitude: lon)
    }

    private func recenter(on mappedSpots: [(LocationSpot, CLLocationCoordinate2D, CLLocationDistance?)]) {
        guard let first = mappedSpots.first else { return }
        selectedSpotID = selectedSpotID ?? first.0.id
        mapCameraPosition = .region(
            MKCoordinateRegion(
                center: first.1,
                span: MKCoordinateSpan(latitudeDelta: 0.08, longitudeDelta: 0.08)
            )
        )
    }

    private func bottomSheet(spots: [(LocationSpot, CLLocationCoordinate2D, CLLocationDistance?)]) -> some View {
        VStack(spacing: 8) {
            Capsule().fill(Color.secondary.opacity(0.25)).frame(width: 40, height: 4)
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(spots, id: \.0.id) { entry in
                        SpotCard(
                            spot: entry.0,
                            distanceText: formattedDistance(entry.2),
                            frictionBadge: frictionBadge(for: entry.0),
                            isFavorite: entry.0.isFavorite,
                            onFavorite: { store.toggleFavorite(for: entry.0) },
                            onTap: { store.markVisited(entry.0); selectedSpotID = entry.0.id }
                        )
                        .frame(width: 280)
                    }
                }
                .padding(.horizontal)
            }
            .padding(.bottom, 8)
        }
        .background(.ultraThinMaterial)
    }

    private func callout(for spot: LocationSpot) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(spot.name)
                    .font(.headline)
                Spacer()
                Button(action: { store.toggleFavorite(for: spot) }) {
                    Image(systemName: spot.isFavorite ? "heart.fill" : "heart")
                        .foregroundStyle(spot.isFavorite ? .red : .primary)
                }
                .buttonStyle(.plain)
            }
            HStack(spacing: 6) {
                Text(spot.tier.rawValue).font(.caption).padding(6).background(Capsule().fill(Color.blue.opacity(0.15)))
                if spot.openLate { Text("Open late").font(.caption).padding(6).background(Capsule().fill(Color.green.opacity(0.18))) }
                if spot.attributes.contains(.realFood) { Text("Food").font(.caption).padding(6).background(Capsule().fill(Color.orange.opacity(0.15))) }
            }
            Text(spot.criticalFieldNotes)
                .font(.caption)
                .lineLimit(3)
        }
        .padding(12)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(uiColor: .secondarySystemBackground)))
        .shadow(radius: 3)
    }

    private func formattedDistance(_ distance: CLLocationDistance?) -> String? {
        guard let distance else { return nil }
        let miles = distance / 1609.34
        return String(format: "%.1f mi", miles)
    }

    private func frictionBadge(for spot: LocationSpot) -> String? {
        if spot.chargedLaptopBrickOnly { return "Charge before you go" }
        if !spot.attributes.contains(.easyParking) && !spot.walkingFriendlyLocation { return "Parking may be tricky" }
        return nil
    }
}
