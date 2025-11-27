import Foundation
import Combine
import CoreLocation

// MARK: - SpotStore

final class SpotStore: ObservableObject {
    // MARK: - Published State

    @Published private(set) var spots: [LocationSpot] = []
    @Published private(set) var loadingState: LoadingState<[LocationSpot]> = .idle
    @Published var favorites: Set<String> = []
    @Published var recentVisits: [String: Date] = [:]
    @Published var location: CLLocation? = nil
    @Published private(set) var lastError: DisplayableError? = nil
    @Published private(set) var stateLoaded = false

    // MARK: - Computed Properties

    var isLoading: Bool { loadingState.isLoading }
    var hasLoaded: Bool { loadingState.hasLoaded }
    var spotCount: Int { spots.count }

    /// Indicates if the store is operating with cached/fallback data
    @Published private(set) var isUsingCachedData: Bool = false

    /// All unique neighborhoods in the dataset
    var neighborhoods: [String] {
        Array(Set(spots.map { $0.neighborhood })).sorted()
    }

    /// Alias for neighborhoods (for clearer API)
    var allNeighborhoods: [String] { neighborhoods }

    /// All unique place types in the dataset
    var placeTypes: [PlaceType] {
        Array(Set(spots.map { $0.placeType })).sorted { $0.rawValue < $1.rawValue }
    }

    // MARK: - Private State

    private var cancellables: Set<AnyCancellable> = []
    private var spotIndex: [String: LocationSpot] = [:]
    private var queryCache: QueryCache = QueryCache()
    private var currentLoader: SpotLoader = BundleSpotLoader()

    private let stateURL: URL = {
        let directory = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first
            ?? URL(fileURLWithPath: NSTemporaryDirectory())
        return directory.appendingPathComponent("spotstore_state.json")
    }()

    // MARK: - Location Anchors

    private let homeAnchor = CLLocation(latitude: 33.958, longitude: -118.396)
    private let workAnchor = CLLocation(latitude: 34.040, longitude: -118.429)
    private let defaultAnchor = CLLocation(latitude: 34.015, longitude: -118.45)

    // MARK: - Constants

    private enum Constants {
        static let maxRecentVisits = 15
        static let cacheExpirationSeconds: TimeInterval = 300
    }

    // MARK: - Initialization

    init(loader: SpotLoader = BundleSpotLoader()) {
        self.currentLoader = loader
        setupStateObservers()

        Task {
            await loadState()
            await load(loader: loader)
        }
    }

    /// Initialize with pre-loaded spots (useful for testing and previews)
    init(spots: [LocationSpot]) {
        self.spots = spots
        self.loadingState = .loaded(spots)
        self.stateLoaded = true
        buildIndex()
        setupStateObservers()
    }

    private func setupStateObservers() {
        $favorites
            .dropFirst()
            .debounce(for: .milliseconds(500), scheduler: RunLoop.main)
            .sink { [weak self] _ in
                self?.queryCache.invalidate()
                self?.persistState()
            }
            .store(in: &cancellables)

        $recentVisits
            .dropFirst()
            .debounce(for: .milliseconds(500), scheduler: RunLoop.main)
            .sink { [weak self] _ in
                self?.queryCache.invalidate()
                self?.persistState()
            }
            .store(in: &cancellables)

        $location
            .dropFirst()
            .sink { [weak self] _ in self?.queryCache.invalidate() }
            .store(in: &cancellables)
    }

    // MARK: - Loading

    @MainActor
    func load(loader: SpotLoader) async {
        guard !loadingState.isLoading else { return }

        loadingState = .loading
        lastError = nil

        do {
            let decoded = try await loader.loadSpots()

            guard !decoded.isEmpty else {
                throw SpotDataError.emptyDataset
            }

            spots = decoded
            loadingState = .loaded(decoded)
            buildIndex()
            applyUserState()

        } catch {
            loadingState = .failed(error)
            lastError = DisplayableError(from: error) { [weak self] in
                guard let self else { return }
                Task { await self.load(loader: loader) }
            }
            print("Failed to load spots: \(error)")
        }
    }

    @MainActor
    func reload() async {
        await reload(loader: currentLoader)
    }

    @MainActor
    func reload(loader: SpotLoader) async {
        currentLoader = loader
        queryCache.invalidate()
        loadingState = .idle
        await load(loader: loader)
    }

    private func buildIndex() {
        spotIndex = Dictionary(uniqueKeysWithValues: spots.map { ($0.id, $0) })
    }

    // MARK: - Querying

    func apply(query: SpotQuery, sort: SpotSort, timeContext: TimeContext = .now()) -> [LocationSpot] {
        let cacheKey = QueryCacheKey(query: query, sort: sort, hour: timeContext.hour)

        if let cached = queryCache.get(for: cacheKey) {
            return cached.map { decorate(spot: $0) }
        }

        let anchor = anchorLocation(for: query)

        let filtered = spots.filter { spot in
            matches(spot: spot, query: query)
        }

        let sorted: [LocationSpot]
        switch sort {
        case .distance:
            sorted = filtered.sorted { lhs, rhs in
                compareByDistance(lhs, rhs, anchor: anchor)
            }
        case .sentiment:
            sorted = filtered.sorted { $0.sentimentScore > $1.sentimentScore }
        case .tier:
            sorted = filtered.sorted { $0.tier.sortOrder < $1.tier.sortOrder }
        case .timeOfDay:
            sorted = filtered.sorted { lhs, rhs in
                let lScore = TimeOfDayScoring.score(for: lhs, context: timeContext)
                let rScore = TimeOfDayScoring.score(for: rhs, context: timeContext)
                return lScore > rScore
            }
        }

        queryCache.set(sorted, for: cacheKey)

        return sorted.map { decorate(spot: $0) }
    }

    /// Quick lookup by ID with O(1) performance
    func spot(byID id: String) -> LocationSpot? {
        if let spot = spotIndex[id] {
            return decorate(spot: spot)
        }
        return nil
    }

    /// Get spots by IDs, preserving order
    func spots(byIDs ids: [String]) -> [LocationSpot] {
        ids.compactMap { spot(byID: $0) }
    }

    /// Get favorite spots
    func favoriteSpots(sort: SpotSort = .distance) -> [LocationSpot] {
        var query = SpotQuery()
        query.favoriteOnly = true
        return apply(query: query, sort: sort).filter { favorites.contains($0.id) }
    }

    /// Get recently visited spots
    func recentSpots(limit: Int = 10) -> [LocationSpot] {
        let sortedRecents = recentVisits.sorted { $0.value > $1.value }
        return sortedRecents.prefix(limit).compactMap { spot(byID: $0.key) }
    }

    // MARK: - Filtering Logic

    private func matches(spot: LocationSpot, query: SpotQuery) -> Bool {
        // Favorite filter
        if query.favoriteOnly == true && !favorites.contains(spot.id) { return false }

        // Boolean filters
        if let openLate = query.openLate, spot.openLate != openLate { return false }
        if let closeToHome = query.closeToHome, spot.closeToHome != closeToHome { return false }
        if let closeToWork = query.closeToWork, spot.closeToWork != closeToWork { return false }
        if let safe = query.safeToLeaveComputer, spot.safeToLeaveComputer != safe { return false }
        if let walking = query.walkingFriendlyLocation, spot.walkingFriendlyLocation != walking { return false }
        if let wellness = query.exerciseWellnessAvailable, spot.exerciseWellnessAvailable != wellness { return false }
        if let brickOnly = query.chargedLaptopBrickOnly, spot.chargedLaptopBrickOnly != brickOnly { return false }

        // Set filters
        if !query.tiers.isEmpty && !query.tiers.contains(spot.tier) { return false }
        if !query.neighborhoods.isEmpty && !query.neighborhoods.contains(spot.neighborhood) { return false }
        if !query.placeTypes.isEmpty && !query.placeTypes.contains(spot.placeType) { return false }
        if !spot.matches(tagFilters: query.attributes) { return false }

        // Text search
        if let searchText = query.searchText, !searchText.isEmpty {
            let lowercased = searchText.lowercased()
            let matchesName = spot.name.lowercased().contains(lowercased)
            let matchesNeighborhood = spot.neighborhood.lowercased().contains(lowercased)
            let matchesNotes = spot.criticalFieldNotes.lowercased().contains(lowercased)
            if !matchesName && !matchesNeighborhood && !matchesNotes { return false }
        }

        return true
    }

    private func compareByDistance(_ lhs: LocationSpot, _ rhs: LocationSpot, anchor: CLLocation?) -> Bool {
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

    // MARK: - Anchor Location

    func anchorLocation(for query: SpotQuery) -> CLLocation? {
        if let location { return location }
        if query.closeToHome == true { return homeAnchor }
        if query.closeToWork == true { return workAnchor }
        return defaultAnchor
    }

    // MARK: - User Actions

    func toggleFavorite(for spot: LocationSpot) {
        if favorites.contains(spot.id) {
            favorites.remove(spot.id)
        } else {
            favorites.insert(spot.id)
        }
    }

    func markVisited(_ spot: LocationSpot) {
        var updated = recentVisits
        updated[spot.id] = Date()

        if updated.count > Constants.maxRecentVisits {
            let sorted = updated.sorted { $0.value > $1.value }
            let trimmed = Dictionary(uniqueKeysWithValues: sorted.prefix(Constants.maxRecentVisits))
            recentVisits = trimmed
        } else {
            recentVisits = updated
        }
    }

    func setFavorite(_ isFavorite: Bool, for spotID: String) {
        if isFavorite {
            favorites.insert(spotID)
        } else {
            favorites.remove(spotID)
        }
    }

    func clearFavorites() {
        favorites.removeAll()
    }

    func clearHistory() {
        recentVisits.removeAll()
    }

    func dismissError() {
        lastError = nil
    }

    // MARK: - Decoration (User State)

    private func decorate(spot: LocationSpot) -> LocationSpot {
        var updated = spot
        updated.isFavorite = favorites.contains(spot.id)
        updated.lastVisited = recentVisits[spot.id]
        return updated
    }

    // MARK: - State Persistence

    @MainActor
    private func loadState() async {
        guard let data = try? Data(contentsOf: stateURL) else {
            stateLoaded = true
            return
        }

        do {
            let decoded = try JSONDecoder().decode(UserState.self, from: data)
            favorites = Set(decoded.favorites)

            var recents: [String: Date] = [:]
            decoded.recents.forEach { recents[$0.id] = $0.lastVisited }
            recentVisits = recents

        } catch {
            // Attempt legacy decode
            if let legacy = try? JSONDecoder().decode(LegacyUserState.self, from: data) {
                favorites = Set(legacy.favorites)
                var recents: [String: Date] = [:]
                legacy.recentIDs.forEach { recents[$0] = Date.distantPast }
                recentVisits = recents
            } else {
                lastError = DisplayableError(
                    from: SpotDataError.corruptedUserState(underlying: error)
                )
                print("Failed to decode user state: \(error)")
            }
        }

        stateLoaded = true
    }

    private func persistState() {
        let recents = recentVisits
            .sorted { $0.value > $1.value }
            .prefix(Constants.maxRecentVisits)
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
        let existing = Set(spots.map { $0.id })
        recentVisits = recentVisits.filter { existing.contains($0.key) }
        favorites = favorites.filter { existing.contains($0) }
    }
}

// MARK: - Tier Sort Order Extension

private extension Tier {
    var sortOrder: Int {
        switch self {
        case .elite: return 0
        case .reliable: return 1
        case .unknown: return 2
        }
    }
}

// MARK: - Query Cache

private struct QueryCacheKey: Hashable {
    let query: SpotQuery
    let sort: SpotSort
    let hour: Int
}

private class QueryCache {
    private var cache: [QueryCacheKey: (spots: [LocationSpot], timestamp: Date)] = [:]
    private let expirationInterval: TimeInterval = 300

    func get(for key: QueryCacheKey) -> [LocationSpot]? {
        guard let entry = cache[key] else { return nil }
        guard Date().timeIntervalSince(entry.timestamp) < expirationInterval else {
            cache.removeValue(forKey: key)
            return nil
        }
        return entry.spots
    }

    func set(_ spots: [LocationSpot], for key: QueryCacheKey) {
        cache[key] = (spots, Date())

        if cache.count > 20 {
            let sortedKeys = cache.sorted { $0.value.timestamp < $1.value.timestamp }
            for (key, _) in sortedKeys.prefix(10) {
                cache.removeValue(forKey: key)
            }
        }
    }

    func invalidate() {
        cache.removeAll()
    }
}

// MARK: - User State Models

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

// MARK: - Spot Loader Protocol & Implementations

protocol SpotLoader {
    func loadSpots() async throws -> [LocationSpot]
}

struct BundleSpotLoader: SpotLoader {
    var resourceName: String = "westside_remote_work_master_verified"

    func loadSpots() async throws -> [LocationSpot] {
        guard let url = Bundle.main.url(forResource: resourceName, withExtension: "json") else {
            throw SpotDataError.missingBundleResource(name: resourceName)
        }

        do {
            let data = try Data(contentsOf: url)
            let decoder = JSONDecoder()
            return try decoder.decode([LocationSpot].self, from: data)
        } catch let decodingError as DecodingError {
            throw SpotDataError.decodingFailed(underlying: decodingError)
        }
    }
}

// MARK: - Time Context

struct TimeContext: Equatable {
    let date: Date
    let calendar: Calendar

    static func now(calendar: Calendar = .current) -> TimeContext {
        TimeContext(date: Date(), calendar: calendar)
    }

    var hour: Int { calendar.component(.hour, from: date) }
    var minute: Int { calendar.component(.minute, from: date) }
    var dayOfWeek: Int { calendar.component(.weekday, from: date) }
    var isWeekend: Bool { dayOfWeek == 1 || dayOfWeek == 7 }

    var timeOfDay: TimeOfDay {
        switch hour {
        case 5..<9: return .earlyMorning
        case 9..<12: return .morning
        case 12..<14: return .lunch
        case 14..<17: return .afternoon
        case 17..<21: return .evening
        default: return .night
        }
    }

    enum TimeOfDay: String, CaseIterable {
        case earlyMorning = "Early Morning"
        case morning = "Morning"
        case lunch = "Lunch"
        case afternoon = "Afternoon"
        case evening = "Evening"
        case night = "Night"
    }

    static func == (lhs: TimeContext, rhs: TimeContext) -> Bool {
        lhs.hour == rhs.hour && lhs.dayOfWeek == rhs.dayOfWeek
    }
}
