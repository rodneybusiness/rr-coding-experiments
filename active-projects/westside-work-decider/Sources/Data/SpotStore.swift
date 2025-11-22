import Foundation
import Combine
import CoreLocation

final class SpotStore: ObservableObject {
    @Published private(set) var spots: [LocationSpot] = []
    @Published var favorites: Set<String> = []
    @Published var recentVisits: [LocationSpot] = []
    @Published var location: CLLocation? = nil

    private var cancellables: Set<AnyCancellable> = []

    init(loader: SpotLoader = BundleSpotLoader()) {
        Task { await load(loader: loader) }
    }

    @MainActor
    func load(loader: SpotLoader) async {
        do {
            let decoded = try await loader.loadSpots()
            spots = decoded
        } catch {
            print("Failed to load spots: \(error)")
        }
    }

    func apply(query: SpotQuery, sort: SpotSort, timeContext: TimeContext = .now()) -> [LocationSpot] {
        let filtered = spots.filter { spot in
            matches(spot: spot, query: query)
        }

        switch sort {
        case .distance:
            return filtered.sorted { lhs, rhs in
                guard let left = lhs.distance(from: location), let right = rhs.distance(from: location) else { return false }
                return left < right
            }
        case .sentiment:
            return filtered.sorted { $0.sentimentScore > $1.sentimentScore }
        case .tier:
            return filtered.sorted { $0.tier.rawValue < $1.tier.rawValue }
        case .timeOfDay:
            return filtered.sorted { lhs, rhs in
                let lScore = TimeOfDayScoring.score(for: lhs, context: timeContext)
                let rScore = TimeOfDayScoring.score(for: rhs, context: timeContext)
                return lScore > rScore
            }
        }
    }

    private func matches(spot: LocationSpot, query: SpotQuery) -> Bool {
        if let openLate = query.openLate, spot.openLate != openLate { return false }
        if let closeToHome = query.closeToHome, spot.closeToHome != closeToHome { return false }
        if let closeToWork = query.closeToWork, spot.closeToWork != closeToWork { return false }
        if let safe = query.safeToLeaveComputer, spot.safeToLeaveComputer != safe { return false }
        if let walking = query.walkingFriendlyLocation, spot.walkingFriendlyLocation != walking { return false }
        if let wellness = query.exerciseWellnessAvailable, spot.exerciseWellnessAvailable != wellness { return false }
        if let brickOnly = query.chargedLaptopBrickOnly, spot.chargedLaptopBrickOnly != brickOnly { return false }

        if !query.tiers.isEmpty && !query.tiers.contains(spot.tier) { return false }
        if !query.neighborhoods.isEmpty && !query.neighborhoods.contains(spot.neighborhood) { return false }
        if !query.placeTypes.isEmpty && !query.placeTypes.contains(spot.placeType) { return false }
        if !spot.matches(tagFilters: query.attributes) { return false }

        return true
    }
}

protocol SpotLoader {
    func loadSpots() async throws -> [LocationSpot]
}

struct BundleSpotLoader: SpotLoader {
    var resourceName: String = "westside_remote_work_master_verified"

    func loadSpots() async throws -> [LocationSpot] {
        guard let url = Bundle.main.url(forResource: resourceName, withExtension: "json") else {
            throw NSError(domain: "SpotLoader", code: 1, userInfo: [NSLocalizedDescriptionKey: "Missing bundled dataset"])
        }
        let data = try Data(contentsOf: url)
        let decoder = JSONDecoder()
        return try decoder.decode([LocationSpot].self, from: data)
    }
}

struct TimeContext {
    let date: Date
    let calendar: Calendar

    static func now(calendar: Calendar = .current) -> TimeContext {
        TimeContext(date: Date(), calendar: calendar)
    }

    var hour: Int { calendar.component(.hour, from: date) }
}
