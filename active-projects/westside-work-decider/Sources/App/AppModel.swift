import Foundation
import CoreLocation
import Combine

@MainActor
final class AppModel: ObservableObject {
    @Published var store: SpotStore
    @Published var locationProvider: LocationProvider
    private var cancellables: Set<AnyCancellable> = []

    init(loader: SpotLoader = CompositeSpotLoader()) {
        self.store = SpotStore(loader: loader)
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
}

/// Tries bundle first, then falls back to a known relative path so previews/tests work outside Xcode.
struct CompositeSpotLoader: SpotLoader {
    var resourceName: String = "westside_remote_work_master_verified"

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
