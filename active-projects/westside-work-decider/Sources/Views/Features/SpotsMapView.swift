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

    var body: some View {
        VStack(spacing: 0) {
            FiltersBar(query: $filters.query)
                .padding(.horizontal)
            let mappedSpots = store.apply(query: filters.query, sort: .distance).compactMap { spot -> (LocationSpot, CLLocationCoordinate2D)? in
                guard let coordinate = coordinate(for: spot) else { return nil }
                return (spot, coordinate)
            }

            if mappedSpots.isEmpty {
                ContentUnavailableView("No map points yet", systemImage: "mappin.slash", description: Text("Add latitude/longitude to the dataset or run one-time geocoding to see pins."))
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                Map(position: $mapCameraPosition) {
                    ForEach(mappedSpots, id: \.0.id) { pair in
                        Marker(pair.0.name, coordinate: pair.1)
                    }
                }
                .mapStyle(.standard(elevation: .realistic))
            }
        }
        .onAppear { mapCameraPosition = defaultCameraPosition() }
    }

    private func coordinate(for spot: LocationSpot) -> CLLocationCoordinate2D? {
        guard let lat = spot.latitude, let lon = spot.longitude else { return nil }
        return CLLocationCoordinate2D(latitude: lat, longitude: lon)
    }

    private func defaultCameraPosition() -> MapCameraPosition {
        if let user = store.anchorLocation(for: filters.query)?.coordinate {
            return .region(MKCoordinateRegion(center: user, span: MKCoordinateSpan(latitudeDelta: 0.08, longitudeDelta: 0.08)))
        }
        return mapCameraPosition
    }
}
