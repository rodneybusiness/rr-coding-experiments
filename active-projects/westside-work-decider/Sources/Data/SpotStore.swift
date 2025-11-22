import Foundation
import Combine
import CoreLocation

final class SpotStore: ObservableObject {
    @Published private(set) var spots: [LocationSpot] = []
    @Published var favorites: Set<String> = []
    @Published var recentVisits: [String: Date] = [:]
    @Published var location: CLLocation? = nil
    @Published private(set) var stateLoaded = false

    private var cancellables: Set<AnyCancellable> = []
    private let stateURL: URL = {
        let directory = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first
            ?? URL(fileURLWithPath: NSTemporaryDirectory())
        return directory.appendingPathComponent("spotstore_state.json")
    }()

    private let homeAnchor = CLLocation(latitude: 33.958, longitude: -118.396)
    private let workAnchor = CLLocation(latitude: 34.040, longitude: -118.429)
    private let defaultAnchor = CLLocation(latitude: 34.015, longitude: -118.45)

    init(loader: SpotLoader = BundleSpotLoader()) {
        Task {
            await loadState()
            await load(loader: loader)
        }

        $favorites
            .dropFirst()
            .sink { [weak self] _ in self?.persistState() }
            .store(in: &cancellables)

        $recentVisits
            .dropFirst()
            .sink { [weak self] _ in self?.persistState() }
            .store(in: &cancellables)
    }

    @MainActor
    func load(loader: SpotLoader) async {
        do {
            let decoded = try await loader.loadSpots()
            spots = decoded
            applyUserState()
        } catch {
            print("Failed to load spots: \(error)")
        }
    }

    func apply(query: SpotQuery, sort: SpotSort, timeContext: TimeContext = .now()) -> [LocationSpot] {
        let anchor = anchorLocation(for: query)
        let filtered = spots.filter { spot in
            matches(spot: spot, query: query)
        }
        .map { decorate(spot: $0) }

        switch sort {
        case .distance:
            return filtered.sorted { lhs, rhs in
                switch (lhs.distance(from: anchor), rhs.distance(from: anchor)) {
                case let (l?, r?):
                    return l < r
                case (.some, .none):
                    return true
                case (.none, .some):
                    return false
                default:
                    return lhs.name < rhs.name
                }
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

    func toggleFavorite(for spot: LocationSpot) {
        if favorites.contains(spot.id) {
            favorites.remove(spot.id)
        } else {
            favorites.insert(spot.id)
        }
        applyUserState()
    }

    func markVisited(_ spot: LocationSpot) {
        var updated = recentVisits
        updated[spot.id] = Date()
        if updated.count > 15 {
            let sorted = updated.sorted { $0.value > $1.value }
            let trimmed = Dictionary(uniqueKeysWithValues: sorted.prefix(15))
            recentVisits = trimmed
        } else {
            recentVisits = updated
        }
        applyUserState()
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

    func anchorLocation(for query: SpotQuery) -> CLLocation? {
        if let location { return location }
        if query.closeToHome == true { return homeAnchor }
        if query.closeToWork == true { return workAnchor }
        return defaultAnchor
    }

    private func decorate(spot: LocationSpot) -> LocationSpot {
        var updated = spot
        updated.isFavorite = favorites.contains(spot.id)
        updated.lastVisited = recentVisits[spot.id]
        return updated
    }

    @MainActor
    private func loadState() async {
        guard let data = try? Data(contentsOf: stateURL) else { stateLoaded = true; return }
        do {
            let decoded = try JSONDecoder().decode(UserState.self, from: data)
            favorites = Set(decoded.favorites)
            var recents: [String: Date] = [:]
            decoded.recents.forEach { recents[$0.id] = $0.lastVisited }
            recentVisits = recents
        } catch {
            // Attempt legacy decode (favorites + recent IDs only)
            if let legacy = try? JSONDecoder().decode(LegacyUserState.self, from: data) {
                favorites = Set(legacy.favorites)
                var recents: [String: Date] = [:]
                legacy.recentIDs.forEach { recents[$0] = Date.distantPast }
                recentVisits = recents
            } else {
                print("Failed to decode user state: \(error)")
            }
        }
        stateLoaded = true
        applyUserState()
    }

    private func persistState() {
        let recents = recentVisits
            .sorted { $0.value > $1.value }
            .prefix(15)
            .map { RecentEntry(id: $0.key, lastVisited: $0.value) }
        let state = UserState(favorites: Array(favorites), recents: Array(recents))
        do {
            let data = try JSONEncoder().encode(state)
            try data.write(to: stateURL, options: [.atomic])
        } catch {
            print("Failed to persist user state: \(error)")
        }
    }

    private func applyUserState() {
        guard stateLoaded else { return }
        spots = spots.map { decorate(spot: $0) }
        let existing = Set(spots.map { $0.id })
        recentVisits = recentVisits.filter { existing.contains($0.key) }
    }
}

private struct UserState: Codable {
    let favorites: [String]
    let recents: [RecentEntry]
}

private struct LegacyUserState: Codable {
    let favorites: [String]
    let recentIDs: [String]
}

private struct RecentEntry: Codable {
    let id: String
    let lastVisited: Date
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
