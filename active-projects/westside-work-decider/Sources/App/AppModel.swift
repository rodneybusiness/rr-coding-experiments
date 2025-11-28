import Foundation
import CoreLocation
import Combine

@MainActor
final class AppModel: ObservableObject {
    @Published var store: SpotStore
    @Published var locationProvider: LocationProvider
    @Published private(set) var currentCity: City
    private var cancellables: Set<AnyCancellable> = []

    init(city: City = .default) {
        self.currentCity = city
        let loader = CompositeSpotLoader(resourceName: city.dataFileName)
        self.store = SpotStore(loader: loader, city: city)
        self.locationProvider = LocationProvider()

        locationProvider.$location
            .receive(on: RunLoop.main)
            .sink { [weak store] newLocation in
                store?.location = newLocation
            }
            .store(in: &cancellables)
    }

    /// For testing/preview with custom loader
    init(loader: SpotLoader, city: City = .default) {
        self.currentCity = city
        self.store = SpotStore(loader: loader, city: city)
        self.locationProvider = LocationProvider()

        locationProvider.$location
            .receive(on: RunLoop.main)
            .sink { [weak store] newLocation in
                store?.location = newLocation
            }
            .store(in: &cancellables)
    }

    func requestLocation() {
        locationProvider.requestAuthorization()
    }

    /// Switch to a different city
    func switchCity(_ city: City) async {
        guard city.id != currentCity.id else { return }
        currentCity = city
        await store.switchCity(city)
    }
}

/// Tries bundle first, then falls back to a known relative path so previews/tests work outside Xcode.
struct CompositeSpotLoader: SpotLoader {
    let resourceName: String

    init(resourceName: String) {
        self.resourceName = resourceName
    }

    func loadSpots() async throws -> [LocationSpot] {
        do {
            return try await BundleSpotLoader(resourceName: resourceName).loadSpots()
        } catch {
            // Fallback for preview/CLI contexts
            let current = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
            let fallback = current.appendingPathComponent("active-projects/westside-work-decider/data/\(resourceName).json")
            let data = try Data(contentsOf: fallback)
            return try JSONDecoder().decode([LocationSpot].self, from: data)
        }
    }
}
