import XCTest
@testable import WestsideWorkDecider

// MARK: - SpotQuery Tests

final class SpotQueryTests: XCTestCase {

    func testEmptyQueryHasNoFilters() {
        let query = SpotQuery()
        XCTAssertFalse(query.hasFilters)
        XCTAssertEqual(query.filterCount, 0)
        XCTAssertNil(query.summaryDescription())
    }

    func testQueryWithTierHasFilters() {
        var query = SpotQuery()
        query.tiers.insert(.elite)
        XCTAssertTrue(query.hasFilters)
        XCTAssertEqual(query.filterCount, 1)
    }

    func testQueryWithMultipleFilters() {
        var query = SpotQuery()
        query.tiers = [.elite, .reliable]
        query.attributes = [.deepFocus, .easyParking]
        query.openLate = true
        query.closeToHome = true

        XCTAssertTrue(query.hasFilters)
        XCTAssertEqual(query.filterCount, 6)  // 2 tiers + 2 attrs + 2 booleans
    }

    func testQuerySummaryDescription() {
        var query = SpotQuery()
        query.tiers.insert(.elite)
        query.attributes.insert(.deepFocus)
        query.openLate = true

        let summary = query.summaryDescription()
        XCTAssertNotNil(summary)
        XCTAssertTrue(summary!.contains("Elite"))
        XCTAssertTrue(summary!.contains("Focus"))
        XCTAssertTrue(summary!.contains("Open late"))
    }

    func testQueryClear() {
        var query = SpotQuery()
        query.tiers.insert(.elite)
        query.attributes.insert(.deepFocus)
        query.openLate = true

        query.clear()

        XCTAssertFalse(query.hasFilters)
        XCTAssertTrue(query.tiers.isEmpty)
        XCTAssertTrue(query.attributes.isEmpty)
        XCTAssertNil(query.openLate)
    }

    func testQueryToggleTier() {
        var query = SpotQuery()

        query.toggle(tier: .elite)
        XCTAssertTrue(query.tiers.contains(.elite))

        query.toggle(tier: .elite)
        XCTAssertFalse(query.tiers.contains(.elite))
    }

    func testQueryToggleAttribute() {
        var query = SpotQuery()

        query.toggle(attribute: .deepFocus)
        XCTAssertTrue(query.attributes.contains(.deepFocus))

        query.toggle(attribute: .deepFocus)
        XCTAssertFalse(query.attributes.contains(.deepFocus))
    }

    func testQueryWithSearchText() {
        var query = SpotQuery()
        query.searchText = "coffee"

        XCTAssertTrue(query.hasFilters)
        XCTAssertEqual(query.filterCount, 1)
    }

    func testQueryWithFavoriteOnly() {
        var query = SpotQuery()
        query.favoriteOnly = true

        XCTAssertTrue(query.hasFilters)
    }
}

// MARK: - LocationSpot Tests

final class LocationSpotTests: XCTestCase {

    func testSpotIDGeneration() {
        let id = LocationSpot.makeID(name: "Test Cafe", neighborhood: "Westchester")
        XCTAssertEqual(id, "test-cafe-westchester")
    }

    func testSpotIDWithSpecialCharacters() {
        let id = LocationSpot.makeID(name: "John's Coffee", neighborhood: "Santa Monica, CA")
        XCTAssertEqual(id, "johns-coffee-santa-monica-ca")
    }

    func testSpotMatchesAllTags() {
        let spot = createTestSpot(attributes: [.deepFocus, .powerHeavy, .easyParking])

        XCTAssertTrue(spot.matches(tagFilters: [.deepFocus]))
        XCTAssertTrue(spot.matches(tagFilters: [.deepFocus, .powerHeavy]))
        XCTAssertFalse(spot.matches(tagFilters: [.bodyDoubling]))
    }

    func testSpotMatchesEmptyTags() {
        let spot = createTestSpot(attributes: [.deepFocus])
        XCTAssertTrue(spot.matches(tagFilters: []))
    }

    func testSpotMatchesAnyTags() {
        let spot = createTestSpot(attributes: [.deepFocus, .powerHeavy])

        XCTAssertTrue(spot.matchesAny(tagFilters: [.deepFocus, .bodyDoubling]))
        XCTAssertFalse(spot.matchesAny(tagFilters: [.bodyDoubling, .luxury]))
    }

    func testSpotPrimaryFriction() {
        let spotWithBrick = createTestSpot(chargedLaptopBrickOnly: true)
        XCTAssertEqual(spotWithBrick.primaryFriction, "Charge before you go")

        let spotWithParkingIssue = createTestSpot(
            attributes: [],
            walkingFriendlyLocation: false
        )
        XCTAssertEqual(spotWithParkingIssue.primaryFriction, "Parking may be tricky")

        let goodSpot = createTestSpot(attributes: [.easyParking])
        XCTAssertNil(goodSpot.primaryFriction)
    }

    func testSpotHasCoordinates() {
        let spotWithCoords = createTestSpot(latitude: 34.0, longitude: -118.4)
        XCTAssertTrue(spotWithCoords.hasCoordinates)

        let spotWithoutCoords = createTestSpot()
        XCTAssertFalse(spotWithoutCoords.hasCoordinates)
    }

    func testSpotEquality() {
        let spot1 = createTestSpot(name: "Test", neighborhood: "Area")
        let spot2 = createTestSpot(name: "Test", neighborhood: "Area")
        let spot3 = createTestSpot(name: "Different", neighborhood: "Area")

        XCTAssertEqual(spot1, spot2)
        XCTAssertNotEqual(spot1, spot3)
    }

    // MARK: - Helpers

    private func createTestSpot(
        name: String = "Test Spot",
        neighborhood: String = "Test Area",
        attributes: [AttributeTag] = [],
        walkingFriendlyLocation: Bool = true,
        chargedLaptopBrickOnly: Bool = false,
        latitude: Double? = nil,
        longitude: Double? = nil
    ) -> LocationSpot {
        LocationSpot(
            name: name,
            city: "Los Angeles",
            neighborhood: neighborhood,
            placeType: .cafe,
            tier: .reliable,
            sentimentScore: 8.0,
            costBasis: "$$",
            openLate: false,
            closeToHome: false,
            closeToWork: false,
            safeToLeaveComputer: true,
            walkingFriendlyLocation: walkingFriendlyLocation,
            exerciseWellnessAvailable: false,
            chargedLaptopBrickOnly: chargedLaptopBrickOnly,
            attributes: attributes,
            criticalFieldNotes: "Test notes",
            status: "Active",
            latitude: latitude,
            longitude: longitude
        )
    }
}

// MARK: - Tier Tests

final class TierTests: XCTestCase {

    func testTierDisplayColor() {
        XCTAssertEqual(Tier.elite.displayColor, "gold")
        XCTAssertEqual(Tier.reliable.displayColor, "blue")
        XCTAssertEqual(Tier.unknown.displayColor, "gray")
    }

    func testTierDescription() {
        XCTAssertFalse(Tier.elite.description.isEmpty)
        XCTAssertFalse(Tier.reliable.description.isEmpty)
    }
}

// MARK: - AttributeTag Tests

final class AttributeTagTests: XCTestCase {

    func testAttributeShortName() {
        XCTAssertEqual(AttributeTag.deepFocus.shortName, "Focus")
        XCTAssertEqual(AttributeTag.easyParking.shortName, "Parking")
        XCTAssertEqual(AttributeTag.bodyDoubling.shortName, "Social")
    }

    func testAttributeKeywords() {
        XCTAssertTrue(AttributeTag.deepFocus.keywords.contains("focus"))
        XCTAssertTrue(AttributeTag.deepFocus.keywords.contains("quiet"))
        XCTAssertTrue(AttributeTag.easyParking.keywords.contains("parking"))
    }

    func testAllAttributesHaveKeywords() {
        for tag in AttributeTag.allCases where tag != .unknown {
            XCTAssertFalse(tag.keywords.isEmpty, "\(tag) should have keywords")
        }
    }
}

// MARK: - SessionPreset Tests

final class SessionPresetTests: XCTestCase {

    func testBuiltInPresets() {
        XCTAssertEqual(SessionPreset.allPresets.count, 4)
        XCTAssertTrue(SessionPreset.allPresets.contains { $0.title == "Deep Focus" })
        XCTAssertTrue(SessionPreset.allPresets.contains { $0.title == "Body Doubling" })
        XCTAssertTrue(SessionPreset.allPresets.contains { $0.title == "Quick Sprint" })
        XCTAssertTrue(SessionPreset.allPresets.contains { $0.title == "Late Night" })
    }

    func testPresetApplyToQuery() {
        var query = SpotQuery()
        SessionPreset.deepFocus.apply(to: &query)

        XCTAssertTrue(query.attributes.contains(.deepFocus))
        XCTAssertTrue(query.attributes.contains(.powerHeavy))
    }

    func testPresetToQuery() {
        let query = SessionPreset.lateNight.toQuery()

        XCTAssertTrue(query.openLate == true)
        XCTAssertTrue(query.attributes.contains(.nightOwl))
    }
}

// MARK: - OperatingHours Tests

final class OperatingHoursTests: XCTestCase {

    func testDayHoursIsOpen() {
        let hours = DayHours(open: "09:00", close: "17:00")
        let calendar = Calendar.current

        // Create date at 10:00
        var components = calendar.dateComponents([.year, .month, .day], from: Date())
        components.hour = 10
        components.minute = 0
        let openTime = calendar.date(from: components)!

        // Create date at 20:00
        components.hour = 20
        let closedTime = calendar.date(from: components)!

        XCTAssertTrue(hours.isOpen(at: openTime, calendar: calendar))
        XCTAssertFalse(hours.isOpen(at: closedTime, calendar: calendar))
    }

    func testDayHoursCrossingMidnight() {
        let hours = DayHours(open: "20:00", close: "02:00")
        let calendar = Calendar.current

        var components = calendar.dateComponents([.year, .month, .day], from: Date())

        // At 21:00 - should be open
        components.hour = 21
        let nightTime = calendar.date(from: components)!
        XCTAssertTrue(hours.isOpen(at: nightTime, calendar: calendar))

        // At 01:00 - should be open
        components.hour = 1
        let lateNight = calendar.date(from: components)!
        XCTAssertTrue(hours.isOpen(at: lateNight, calendar: calendar))

        // At 10:00 - should be closed
        components.hour = 10
        let morning = calendar.date(from: components)!
        XCTAssertFalse(hours.isOpen(at: morning, calendar: calendar))
    }
}

// MARK: - TimeContext Tests

final class TimeContextTests: XCTestCase {

    func testTimeOfDayClassification() {
        let calendar = Calendar.current
        var components = DateComponents()
        components.year = 2024
        components.month = 6
        components.day = 15

        // Early morning (6:00)
        components.hour = 6
        let earlyMorning = calendar.date(from: components)!
        let earlyContext = TimeContext(date: earlyMorning, calendar: calendar)
        XCTAssertEqual(earlyContext.timeOfDay, .earlyMorning)

        // Morning (10:00)
        components.hour = 10
        let morning = calendar.date(from: components)!
        let morningContext = TimeContext(date: morning, calendar: calendar)
        XCTAssertEqual(morningContext.timeOfDay, .morning)

        // Evening (19:00)
        components.hour = 19
        let evening = calendar.date(from: components)!
        let eveningContext = TimeContext(date: evening, calendar: calendar)
        XCTAssertEqual(eveningContext.timeOfDay, .evening)

        // Night (23:00)
        components.hour = 23
        let night = calendar.date(from: components)!
        let nightContext = TimeContext(date: night, calendar: calendar)
        XCTAssertEqual(nightContext.timeOfDay, .night)
    }

    func testWeekendDetection() {
        let calendar = Calendar.current

        // Find a Saturday
        var components = DateComponents()
        components.year = 2024
        components.month = 6
        components.day = 15  // Saturday
        components.hour = 12
        let saturday = calendar.date(from: components)!
        let satContext = TimeContext(date: saturday, calendar: calendar)
        XCTAssertTrue(satContext.isWeekend)

        // Monday
        components.day = 17
        let monday = calendar.date(from: components)!
        let monContext = TimeContext(date: monday, calendar: calendar)
        XCTAssertFalse(monContext.isWeekend)
    }
}

// MARK: - SimulatedAIService Tests

final class SimulatedAIServiceTests: XCTestCase {

    let service = SimulatedAIService()

    func testExtractsDeepFocusKeywords() async throws {
        let response = try await service.recommend(request: createRequest("I need a quiet place to focus"))

        XCTAssertTrue(response.filters?.attributes.contains(.deepFocus) == true)
    }

    func testExtractsParkingKeywords() async throws {
        let response = try await service.recommend(request: createRequest("somewhere with easy parking"))

        XCTAssertTrue(response.filters?.attributes.contains(.easyParking) == true)
    }

    func testExtractsLateNightKeywords() async throws {
        let response = try await service.recommend(request: createRequest("open late tonight"))

        XCTAssertTrue(response.filters?.openLate == true)
    }

    func testInfersDeepFocusPreset() async throws {
        let response = try await service.recommend(request: createRequest("I need deep focus"))

        XCTAssertEqual(response.preset?.title, "Deep Focus")
    }

    func testInfersBodyDoublingPreset() async throws {
        let response = try await service.recommend(request: createRequest("social atmosphere with people around"))

        XCTAssertEqual(response.preset?.title, "Body Doubling")
    }

    func testRespectsMaxRecommendations() async throws {
        let response = try await service.recommend(request: createRequest("show me spots"))

        XCTAssertLessThanOrEqual(response.recommendations.count, 5)
    }

    func testClosestSortForDistanceQuery() async throws {
        let response = try await service.recommend(request: createRequest("closest spot to me"))

        XCTAssertEqual(response.sort, .distance)
    }

    func testRecommendationsHaveReasons() async throws {
        let response = try await service.recommend(request: createRequest("coffee shop"))

        for rec in response.recommendations {
            XCTAssertFalse(rec.reason.isEmpty, "Recommendation should have a reason")
        }
    }

    // MARK: - Helpers

    private func createRequest(_ message: String) -> AIRecommendationRequest {
        AIRecommendationRequest(
            userMessage: message,
            time: Date(),
            coordinate: nil,
            activeFilters: nil,
            candidateSpots: createTestCandidates()
        )
    }

    private func createTestCandidates() -> [SpotSummary] {
        [
            SpotSummary(
                id: "test-cafe-1",
                name: "Deep Focus Cafe",
                neighborhood: "Westchester",
                tier: .elite,
                placeType: .cafe,
                attributes: [.deepFocus, .powerHeavy, .eliteCoffee],
                criticalFieldNotes: "Quiet library vibe",
                distanceMeters: 1000
            ),
            SpotSummary(
                id: "test-cafe-2",
                name: "Social Hub",
                neighborhood: "Santa Monica",
                tier: .reliable,
                placeType: .coworking,
                attributes: [.bodyDoubling, .easyParking, .realFood],
                criticalFieldNotes: "Great for networking",
                distanceMeters: 2000
            ),
            SpotSummary(
                id: "test-cafe-3",
                name: "Night Owl Spot",
                neighborhood: "Culver City",
                tier: .reliable,
                placeType: .cafe,
                attributes: [.nightOwl, .powerHeavy],
                criticalFieldNotes: "Open until 2am",
                distanceMeters: 3000
            )
        ]
    }
}

// MARK: - Error Types Tests

final class ErrorTypesTests: XCTestCase {

    func testSpotDataErrorDescriptions() {
        let errors: [SpotDataError] = [
            .missingBundleResource(name: "test"),
            .decodingFailed(underlying: NSError(domain: "test", code: 1)),
            .fileNotFound(path: "/test"),
            .emptyDataset,
            .corruptedUserState(underlying: NSError(domain: "test", code: 1))
        ]

        for error in errors {
            XCTAssertNotNil(error.errorDescription, "Error should have description: \(error)")
            XCTAssertNotNil(error.recoverySuggestion, "Error should have recovery suggestion: \(error)")
        }
    }

    func testAIServiceErrorDescriptions() {
        let errors: [AIServiceError] = [
            .missingAPIKey,
            .invalidResponse(details: "test"),
            .networkError(underlying: NSError(domain: "test", code: 1)),
            .timeout,
            .rateLimited(retryAfter: 60),
            .serverError(statusCode: 500),
            .parsingFailed(underlying: NSError(domain: "test", code: 1))
        ]

        for error in errors {
            XCTAssertNotNil(error.errorDescription, "Error should have description: \(error)")
        }
    }

    func testAIServiceErrorRetryable() {
        XCTAssertTrue(AIServiceError.timeout.isRetryable)
        XCTAssertTrue(AIServiceError.serverError(statusCode: 500).isRetryable)
        XCTAssertTrue(AIServiceError.rateLimited(retryAfter: 60).isRetryable)
        XCTAssertFalse(AIServiceError.missingAPIKey.isRetryable)
        XCTAssertFalse(AIServiceError.invalidResponse(details: "test").isRetryable)
    }

    func testDisplayableError() {
        let error = AIServiceError.timeout
        let displayable = DisplayableError(from: error)

        XCTAssertFalse(displayable.title.isEmpty)
        XCTAssertFalse(displayable.message.isEmpty)
        XCTAssertTrue(displayable.isRetryable)
    }
}

// MARK: - LoadingState Tests

final class LoadingStateTests: XCTestCase {

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
    }

    func testLoadedState() {
        let state: LoadingState<[String]> = .loaded(["test"])
        XCTAssertFalse(state.isLoading)
        XCTAssertTrue(state.hasLoaded)
        XCTAssertEqual(state.value, ["test"])
    }

    func testFailedState() {
        let error = NSError(domain: "test", code: 1)
        let state: LoadingState<[String]> = .failed(error)
        XCTAssertFalse(state.isLoading)
        XCTAssertFalse(state.hasLoaded)
        XCTAssertNotNil(state.error)
    }
}

// MARK: - SpotSort Tests

final class SpotSortTests: XCTestCase {

    func testSortDisplayNames() {
        XCTAssertEqual(SpotSort.distance.displayName, "Distance")
        XCTAssertEqual(SpotSort.sentiment.displayName, "Sentiment")
        XCTAssertEqual(SpotSort.tier.displayName, "Tier")
        XCTAssertEqual(SpotSort.timeOfDay.displayName, "Time of day")
    }

    func testSortIcons() {
        for sort in SpotSort.allCases {
            XCTAssertFalse(sort.icon.isEmpty, "\(sort) should have an icon")
        }
    }
}

// MARK: - PlaceType Tests

final class PlaceTypeTests: XCTestCase {

    func testPlaceTypeIcons() {
        for type in PlaceType.allCases {
            XCTAssertFalse(type.icon.isEmpty, "\(type) should have an icon")
        }
    }

    func testPlaceTypeShortNames() {
        XCTAssertEqual(PlaceType.coworking.shortName, "Coworking")
        XCTAssertEqual(PlaceType.hotelLobby.shortName, "Hotel")
        XCTAssertEqual(PlaceType.cafeRestaurant.shortName, "Restaurant")
    }
}
