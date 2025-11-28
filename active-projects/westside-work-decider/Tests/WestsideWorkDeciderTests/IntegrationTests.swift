import XCTest
@testable import WestsideWorkDecider
import CoreLocation

// MARK: - Integration Tests

/// Integration tests for Priority 1-4 improvements
final class IntegrationTests: XCTestCase {

    // MARK: - Test Data

    static let testSpot = LocationSpot(
        name: "Test Coffee Shop",
        city: "Los Angeles",
        neighborhood: "Venice",
        placeType: .cafe,
        tier: .elite,
        sentimentScore: 4.5,
        costBasis: "$$",
        openLate: true,
        closeToHome: false,
        closeToWork: false,
        safeToLeaveComputer: true,
        walkingFriendlyLocation: true,
        exerciseWellnessAvailable: false,
        chargedLaptopBrickOnly: false,
        attributes: [.deepFocus, .powerHeavy, .eliteCoffee],
        criticalFieldNotes: "Great spot for focused work",
        status: "Verified Open",
        latitude: 33.9925,
        longitude: -118.4695,
        wifiQuality: .fast,
        noiseLevel: .quiet,
        operatingHours: OperatingHours(schedule: [
            1: DayHours(open: "06:00", close: "21:00"),
            2: DayHours(open: "06:00", close: "21:00"),
            3: DayHours(open: "06:00", close: "21:00"),
            4: DayHours(open: "06:00", close: "21:00"),
            5: DayHours(open: "06:00", close: "22:00"),
            6: DayHours(open: "07:00", close: "22:00"),
            7: DayHours(open: "07:00", close: "20:00")
        ])
    )

    static var testSpotNoHours = LocationSpot(
        name: "Test Spot Without Hours",
        city: "Los Angeles",
        neighborhood: "Santa Monica",
        placeType: .cafe,
        tier: .reliable,
        sentimentScore: 3.5,
        costBasis: "$$",
        openLate: false,
        closeToHome: true,
        closeToWork: false,
        safeToLeaveComputer: false,
        walkingFriendlyLocation: false,
        exerciseWellnessAvailable: false,
        chargedLaptopBrickOnly: true,
        attributes: [.bodyDoubling],
        criticalFieldNotes: "Basic cafe",
        status: "Verified Open",
        latitude: 34.0195,
        longitude: -118.4912
    )
}

// MARK: - DistanceFormatter Tests

final class DistanceFormatterIntegrationTests: XCTestCase {

    func testFormatShortDistance() {
        let formatted = DistanceFormatter.format(meters: 150)
        XCTAssertEqual(formatted, "< 0.1 mi")
    }

    func testFormatMediumDistance() {
        let formatted = DistanceFormatter.format(meters: 1609.34) // 1 mile
        XCTAssertEqual(formatted, "1.0 mi")
    }

    func testFormatLongDistance() {
        let formatted = DistanceFormatter.format(meters: 16093.4) // 10 miles
        XCTAssertEqual(formatted, "10 mi")
    }

    func testEstimatedTimeDriving() {
        let time = DistanceFormatter.estimatedTime(meters: 6700, mode: .driving) // ~10 min
        XCTAssertEqual(time, "10 min drive")
    }

    func testEstimatedTimeWalking() {
        let time = DistanceFormatter.estimatedTime(meters: 800, mode: .walking) // ~10 min
        XCTAssertEqual(time, "10 min walk")
    }

    func testEstimatedTimeTransit() {
        let time = DistanceFormatter.estimatedTime(meters: 4000, mode: .transit) // ~10 min
        XCTAssertEqual(time, "10 min transit")
    }

    func testEstimatedTimeLongDrive() {
        let time = DistanceFormatter.estimatedTime(meters: 67000, mode: .driving) // ~100 min
        XCTAssertEqual(time, "1 hr 40 min drive")
    }
}

// MARK: - FrictionBadge Tests

final class FrictionBadgeIntegrationTests: XCTestCase {

    func testEvaluateChargedLaptopOnly() {
        let spot = IntegrationTests.testSpotNoHours
        let warning = FrictionBadge.evaluate(for: spot)

        XCTAssertNotNil(warning)
        XCTAssertEqual(warning?.severity, .high)
        XCTAssertTrue(warning?.message.contains("Charge") ?? false)
    }

    func testEvaluateNoParkingNonRushHour() {
        var spot = IntegrationTests.testSpotNoHours
        spot.chargedLaptopBrickOnly = false

        let warning = FrictionBadge.evaluate(for: spot, hour: 14) // 2 PM

        XCTAssertNotNil(warning)
        XCTAssertTrue(warning?.message.contains("Parking") ?? false)
    }

    func testEvaluateRushHour() {
        var spot = IntegrationTests.testSpotNoHours
        spot.chargedLaptopBrickOnly = false

        let warning = FrictionBadge.evaluate(for: spot, hour: 8) // 8 AM rush hour

        XCTAssertNotNil(warning)
        XCTAssertTrue(warning?.message.contains("Rush hour") ?? false)
    }

    func testEvaluateNightSafety() {
        var spot = IntegrationTests.testSpotNoHours
        spot.chargedLaptopBrickOnly = false
        spot.walkingFriendlyLocation = true

        let warning = FrictionBadge.evaluate(for: spot, hour: 21) // 9 PM

        XCTAssertNotNil(warning)
        XCTAssertTrue(warning?.message.contains("night") ?? false)
    }

    func testEvaluateNoWarning() {
        let spot = IntegrationTests.testSpot
        let warning = FrictionBadge.evaluate(for: spot, hour: 14)

        // Elite spot with parking friendly and safe should have no friction
        XCTAssertNil(warning)
    }

    func testAllWarningsMultiple() {
        let spot = IntegrationTests.testSpotNoHours
        let warnings = FrictionBadge.allWarnings(for: spot, hour: 8)

        XCTAssertGreaterThan(warnings.count, 1)
    }
}

// MARK: - OperatingHours Tests

final class OperatingHoursIntegrationTests: XCTestCase {

    func testIsOpenDuringBusinessHours() {
        let spot = IntegrationTests.testSpot
        guard let hours = spot.operatingHours else {
            XCTFail("Test spot should have operating hours")
            return
        }

        // Create a Wednesday at 2 PM
        var components = DateComponents()
        components.year = 2024
        components.month = 3
        components.day = 13 // Wednesday
        components.hour = 14
        components.minute = 0

        let calendar = Calendar.current
        guard let date = calendar.date(from: components) else {
            XCTFail("Could not create test date")
            return
        }

        XCTAssertTrue(hours.isOpen(at: date, calendar: calendar))
    }

    func testIsClosedBeforeOpen() {
        let spot = IntegrationTests.testSpot
        guard let hours = spot.operatingHours else {
            XCTFail("Test spot should have operating hours")
            return
        }

        // Create a Wednesday at 5 AM (before 6 AM open)
        var components = DateComponents()
        components.year = 2024
        components.month = 3
        components.day = 13
        components.hour = 5
        components.minute = 0

        let calendar = Calendar.current
        guard let date = calendar.date(from: components) else {
            XCTFail("Could not create test date")
            return
        }

        XCTAssertFalse(hours.isOpen(at: date, calendar: calendar))
    }

    func testIsClosedAfterClose() {
        let spot = IntegrationTests.testSpot
        guard let hours = spot.operatingHours else {
            XCTFail("Test spot should have operating hours")
            return
        }

        // Create a Wednesday at 10 PM (after 9 PM close)
        var components = DateComponents()
        components.year = 2024
        components.month = 3
        components.day = 13
        components.hour = 22
        components.minute = 0

        let calendar = Calendar.current
        guard let date = calendar.date(from: components) else {
            XCTFail("Could not create test date")
            return
        }

        XCTAssertFalse(hours.isOpen(at: date, calendar: calendar))
    }
}

// MARK: - LoadingState Tests

final class LoadingStateIntegrationTests: XCTestCase {

    func testIdleState() {
        let state: LoadingState<[String]> = .idle

        XCTAssertFalse(state.isLoading)
        XCTAssertFalse(state.hasLoaded)
        XCTAssertNil(state.value)
        XCTAssertNil(state.error)
    }

    func testLoadingState() {
        let state: LoadingState<[String]> = .loading

        XCTAssertTrue(state.isLoading)
        XCTAssertFalse(state.hasLoaded)
        XCTAssertNil(state.value)
        XCTAssertNil(state.error)
    }

    func testLoadedState() {
        let state: LoadingState<[String]> = .loaded(["a", "b", "c"])

        XCTAssertFalse(state.isLoading)
        XCTAssertTrue(state.hasLoaded)
        XCTAssertEqual(state.value, ["a", "b", "c"])
        XCTAssertNil(state.error)
    }

    func testFailedState() {
        let error = SpotDataError.emptyDataset
        let state: LoadingState<[String]> = .failed(error)

        XCTAssertFalse(state.isLoading)
        XCTAssertFalse(state.hasLoaded)
        XCTAssertNil(state.value)
        XCTAssertNotNil(state.error)
    }
}

// MARK: - DisplayableError Tests

final class DisplayableErrorIntegrationTests: XCTestCase {

    func testFromSpotDataError() {
        let error = SpotDataError.emptyDataset
        let displayable = DisplayableError(from: error)

        XCTAssertEqual(displayable.title, "Something went wrong")
        XCTAssertTrue(displayable.message.contains("No spots"))
        XCTAssertNotNil(displayable.suggestion)
    }

    func testFromAIServiceError() {
        let error = AIServiceError.timeout
        let displayable = DisplayableError(from: error)

        XCTAssertTrue(displayable.message.contains("timed out"))
        XCTAssertTrue(displayable.isRetryable)
    }

    func testNonRetryableAIError() {
        let error = AIServiceError.missingAPIKey
        let displayable = DisplayableError(from: error)

        XCTAssertFalse(displayable.isRetryable)
    }

    func testRetryableAIError() {
        let error = AIServiceError.networkError(underlying: URLError(.notConnectedToInternet))
        let displayable = DisplayableError(from: error)

        XCTAssertTrue(displayable.isRetryable)
    }

    func testCustomError() {
        let displayable = DisplayableError(
            title: "Custom Error",
            message: "Something bad happened",
            suggestion: "Try again",
            isRetryable: true
        )

        XCTAssertEqual(displayable.title, "Custom Error")
        XCTAssertEqual(displayable.message, "Something bad happened")
        XCTAssertEqual(displayable.suggestion, "Try again")
        XCTAssertTrue(displayable.isRetryable)
    }
}

// MARK: - WiFiQuality Tests

final class WiFiQualityIntegrationTests: XCTestCase {

    func testWiFiQualityValues() {
        XCTAssertEqual(WiFiQuality.fast.rawValue, "Fast")
        XCTAssertEqual(WiFiQuality.moderate.rawValue, "Moderate")
        XCTAssertEqual(WiFiQuality.slow.rawValue, "Slow")
        XCTAssertEqual(WiFiQuality.none.rawValue, "None")
    }

    func testWiFiQualityFromSpot() {
        let spot = IntegrationTests.testSpot
        XCTAssertEqual(spot.wifiQuality, .fast)
    }
}

// MARK: - NoiseLevel Tests

final class NoiseLevelIntegrationTests: XCTestCase {

    func testNoiseLevelValues() {
        XCTAssertEqual(NoiseLevel.silent.rawValue, "Silent")
        XCTAssertEqual(NoiseLevel.quiet.rawValue, "Quiet")
        XCTAssertEqual(NoiseLevel.moderate.rawValue, "Moderate")
        XCTAssertEqual(NoiseLevel.loud.rawValue, "Loud")
    }

    func testNoiseLevelFromSpot() {
        let spot = IntegrationTests.testSpot
        XCTAssertEqual(spot.noiseLevel, .quiet)
    }
}

// MARK: - TravelMode Tests

final class TravelModeIntegrationTests: XCTestCase {

    func testTravelModeMetersPerMinute() {
        XCTAssertEqual(TravelMode.driving.metersPerMinute, 670)
        XCTAssertEqual(TravelMode.walking.metersPerMinute, 80)
        XCTAssertEqual(TravelMode.transit.metersPerMinute, 400)
    }

    func testTravelModeSuffix() {
        XCTAssertEqual(TravelMode.driving.suffix, "drive")
        XCTAssertEqual(TravelMode.walking.suffix, "walk")
        XCTAssertEqual(TravelMode.transit.suffix, "transit")
    }
}

// MARK: - RelativeTimeFormatter Tests

final class RelativeTimeFormatterIntegrationTests: XCTestCase {

    func testAbbreviatedFormat() {
        let oneHourAgo = Date().addingTimeInterval(-3600)
        let formatted = RelativeTimeFormatter.abbreviated(from: oneHourAgo)

        XCTAssertTrue(formatted.contains("hr") || formatted.contains("hour"))
    }

    func testLastVisited() {
        let yesterday = Date().addingTimeInterval(-86400)
        let formatted = RelativeTimeFormatter.lastVisited(yesterday)

        XCTAssertNotNil(formatted)
        XCTAssertTrue(formatted!.contains("Visited"))
    }

    func testLastVisitedNil() {
        let formatted = RelativeTimeFormatter.lastVisited(nil)
        XCTAssertNil(formatted)
    }
}

// MARK: - SpotStore Integration Tests

final class SpotStoreIntegrationTests: XCTestCase {

    func testSpotStoreInitWithSpots() {
        let spots = [IntegrationTests.testSpot, IntegrationTests.testSpotNoHours]
        let store = SpotStore(spots: spots)

        XCTAssertEqual(store.spotCount, 2)
        XCTAssertTrue(store.hasLoaded)
    }

    func testSpotByID() {
        let spots = [IntegrationTests.testSpot]
        let store = SpotStore(spots: spots)

        let found = store.spot(byID: "test-coffee-shop-venice")
        XCTAssertNotNil(found)
        XCTAssertEqual(found?.name, "Test Coffee Shop")
    }

    func testSpotByIDNotFound() {
        let spots = [IntegrationTests.testSpot]
        let store = SpotStore(spots: spots)

        let found = store.spot(byID: "nonexistent")
        XCTAssertNil(found)
    }

    func testAllNeighborhoods() {
        let spots = [IntegrationTests.testSpot, IntegrationTests.testSpotNoHours]
        let store = SpotStore(spots: spots)

        let neighborhoods = store.allNeighborhoods
        XCTAssertEqual(neighborhoods.count, 2)
        XCTAssertTrue(neighborhoods.contains("Venice"))
        XCTAssertTrue(neighborhoods.contains("Santa Monica"))
    }

    func testApplyQueryWithTier() {
        let spots = [IntegrationTests.testSpot, IntegrationTests.testSpotNoHours]
        let store = SpotStore(spots: spots)

        var query = SpotQuery()
        query.tiers.insert(.elite)

        let results = store.apply(query: query, sort: .distance)
        XCTAssertEqual(results.count, 1)
        XCTAssertEqual(results.first?.tier, .elite)
    }

    func testApplyQueryWithAttribute() {
        let spots = [IntegrationTests.testSpot, IntegrationTests.testSpotNoHours]
        let store = SpotStore(spots: spots)

        var query = SpotQuery()
        query.attributes.insert(.deepFocus)

        let results = store.apply(query: query, sort: .sentiment)
        XCTAssertEqual(results.count, 1)
        XCTAssertTrue(results.first?.attributes.contains(.deepFocus) ?? false)
    }

    func testToggleFavorite() {
        let spots = [IntegrationTests.testSpot]
        let store = SpotStore(spots: spots)
        let spotID = "test-coffee-shop-venice"

        XCTAssertFalse(store.favorites.contains(spotID))

        store.toggleFavorite(for: IntegrationTests.testSpot)
        XCTAssertTrue(store.favorites.contains(spotID))

        store.toggleFavorite(for: IntegrationTests.testSpot)
        XCTAssertFalse(store.favorites.contains(spotID))
    }
}

// MARK: - SimulatedAIService Tests

final class SimulatedAIServiceIntegrationTests: XCTestCase {

    func testRecommendWithKeywords() async throws {
        let service = SimulatedAIService()
        let spots = [
            SpotSummary(
                id: "test-1",
                name: "Quiet Coffee",
                neighborhood: "Venice",
                tier: .elite,
                placeType: .cafe,
                attributes: [.deepFocus, .powerHeavy],
                criticalFieldNotes: "Great for focus work",
                distanceMeters: 1000
            )
        ]

        let request = AIRecommendationRequest(
            userMessage: "I need a quiet place to focus",
            time: Date(),
            coordinate: CLLocationCoordinate2D(latitude: 34.0, longitude: -118.4),
            activeFilters: SpotQuery(),
            candidateSpots: spots
        )

        let response = try await service.recommend(request: request)

        XCTAssertFalse(response.recommendations.isEmpty)
        XCTAssertTrue(response.recommendations.contains { $0.id == "test-1" })
    }

    func testRecommendLateNight() async throws {
        let service = SimulatedAIService()
        let spots = [
            SpotSummary(
                id: "late-spot",
                name: "Night Owl Cafe",
                neighborhood: "Venice",
                tier: .reliable,
                placeType: .cafe,
                attributes: [.nightOwl],
                criticalFieldNotes: "Open until 2am",
                distanceMeters: 500
            )
        ]

        // Create a late night date
        var components = Calendar.current.dateComponents([.year, .month, .day], from: Date())
        components.hour = 22
        let lateNight = Calendar.current.date(from: components) ?? Date()

        let request = AIRecommendationRequest(
            userMessage: "Where can I work late tonight?",
            time: lateNight,
            coordinate: nil,
            activeFilters: SpotQuery(),
            candidateSpots: spots
        )

        let response = try await service.recommend(request: request)

        // Should recommend the night owl spot
        XCTAssertNotNil(response.filters?.openLate)
    }
}

// MARK: - City Tests

final class CityIntegrationTests: XCTestCase {

    func testDefaultCity() {
        XCTAssertEqual(City.default.id, "la-westside")
        XCTAssertEqual(City.default.name, "LA Westside")
    }

    func testCityFindByID() {
        let found = City.find(byID: "la-westside")
        XCTAssertNotNil(found)
        XCTAssertEqual(found?.name, "LA Westside")

        let notFound = City.find(byID: "nonexistent")
        XCTAssertNil(notFound)
    }

    func testCitiesWithData() {
        let citiesWithData = City.citiesWithData
        XCTAssertTrue(citiesWithData.contains { $0.id == "la-westside" })
        XCTAssertTrue(citiesWithData.contains { $0.id == "sf-bay" })
        XCTAssertTrue(citiesWithData.contains { $0.id == "london" })
    }

    func testCityAnchors() {
        let la = City.laWestside

        XCTAssertNotNil(la.defaultAnchor)
        XCTAssertNotNil(la.homeAnchor)
        XCTAssertNotNil(la.workAnchor)

        // SF doesn't have home anchor
        let sf = City.sanFrancisco
        XCTAssertNotNil(sf.defaultAnchor)
        XCTAssertNil(sf.homeAnchor)
        XCTAssertNotNil(sf.workAnchor)
    }

    func testCitySpotCount() {
        XCTAssertEqual(City.laWestside.spotCount, 44)
        XCTAssertEqual(City.sanFrancisco.spotCount, 2)
        XCTAssertEqual(City.london.spotCount, 1)
        XCTAssertEqual(City.newYork.spotCount, 0)
    }

    func testCityHasData() {
        XCTAssertTrue(City.laWestside.hasData)
        XCTAssertTrue(City.sanFrancisco.hasData)
        XCTAssertTrue(City.london.hasData)
        XCTAssertFalse(City.newYork.hasData)
        XCTAssertFalse(City.paris.hasData)
    }

    func testCitySpotCountLabel() {
        XCTAssertEqual(City.laWestside.spotCountLabel, "44 spots")
        XCTAssertEqual(City.london.spotCountLabel, "1 spot")
        XCTAssertEqual(City.newYork.spotCountLabel, "Coming soon")
    }

    func testAllCitiesAvailable() {
        let all = City.available
        XCTAssertGreaterThanOrEqual(all.count, 6)
        XCTAssertTrue(all.contains { $0.id == "la-westside" })
        XCTAssertTrue(all.contains { $0.id == "sf-bay" })
        XCTAssertTrue(all.contains { $0.id == "london" })
        XCTAssertTrue(all.contains { $0.id == "nyc" })
        XCTAssertTrue(all.contains { $0.id == "paris" })
        XCTAssertTrue(all.contains { $0.id == "detroit-aa" })
    }

    func testCityGroups() {
        let groups = CityGroup.all
        XCTAssertGreaterThanOrEqual(groups.count, 4)

        let westCoast = groups.first { $0.id == "usa-west" }
        XCTAssertNotNil(westCoast)
        XCTAssertTrue(westCoast?.cities.contains { $0.id == "la-westside" } ?? false)
        XCTAssertTrue(westCoast?.cities.contains { $0.id == "sf-bay" } ?? false)
    }
}
