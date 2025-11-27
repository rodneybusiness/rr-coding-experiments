import XCTest
@testable import WestsideWorkDecider
import CoreLocation

// MARK: - Error Simulation Tests

/// Tests for error handling, edge cases, and error recovery
final class ErrorSimulationTests: XCTestCase {

    // MARK: - SpotDataError Tests

    func testMissingBundleResourceError() {
        let error = SpotDataError.missingBundleResource(name: "missing_file")

        XCTAssertNotNil(error.errorDescription)
        XCTAssertTrue(error.errorDescription!.contains("missing_file"))
        XCTAssertNotNil(error.recoverySuggestion)
    }

    func testDecodingFailedError() {
        let underlying = NSError(domain: "Test", code: 1, userInfo: nil)
        let error = SpotDataError.decodingFailed(underlying: underlying)

        XCTAssertNotNil(error.errorDescription)
        XCTAssertTrue(error.errorDescription!.contains("parse"))
        XCTAssertNotNil(error.recoverySuggestion)
    }

    func testFileNotFoundError() {
        let error = SpotDataError.fileNotFound(path: "/nonexistent/path")

        XCTAssertNotNil(error.errorDescription)
        XCTAssertTrue(error.errorDescription!.contains("/nonexistent/path"))
    }

    func testEmptyDatasetError() {
        let error = SpotDataError.emptyDataset

        XCTAssertNotNil(error.errorDescription)
        XCTAssertTrue(error.errorDescription!.contains("No spots"))
    }

    func testCorruptedUserStateError() {
        let underlying = NSError(domain: "JSON", code: 1, userInfo: nil)
        let error = SpotDataError.corruptedUserState(underlying: underlying)

        XCTAssertNotNil(error.errorDescription)
        XCTAssertTrue(error.errorDescription!.contains("corrupted"))
        XCTAssertNotNil(error.recoverySuggestion)
        XCTAssertTrue(error.recoverySuggestion!.contains("reset"))
    }

    // MARK: - AIServiceError Tests

    func testMissingAPIKeyError() {
        let error = AIServiceError.missingAPIKey

        XCTAssertNotNil(error.errorDescription)
        XCTAssertTrue(error.errorDescription!.contains("API key"))
        XCTAssertFalse(error.isRetryable)
    }

    func testInvalidResponseError() {
        let error = AIServiceError.invalidResponse(details: "Missing content")

        XCTAssertNotNil(error.errorDescription)
        XCTAssertTrue(error.errorDescription!.contains("Missing content"))
        XCTAssertFalse(error.isRetryable)
    }

    func testNetworkErrorIsRetryable() {
        let urlError = URLError(.notConnectedToInternet)
        let error = AIServiceError.networkError(underlying: urlError)

        XCTAssertTrue(error.isRetryable)
        XCTAssertNotNil(error.errorDescription)
    }

    func testTimeoutErrorIsRetryable() {
        let error = AIServiceError.timeout

        XCTAssertTrue(error.isRetryable)
        XCTAssertTrue(error.errorDescription!.contains("timed out"))
    }

    func testRateLimitedWithRetryAfter() {
        let error = AIServiceError.rateLimited(retryAfter: 30)

        XCTAssertNotNil(error.errorDescription)
        XCTAssertTrue(error.errorDescription!.contains("30"))
        XCTAssertTrue(error.isRetryable)
    }

    func testRateLimitedWithoutRetryAfter() {
        let error = AIServiceError.rateLimited(retryAfter: nil)

        XCTAssertNotNil(error.errorDescription)
        XCTAssertFalse(error.isRetryable)
    }

    func testServerErrorIsRetryable() {
        let error = AIServiceError.serverError(statusCode: 503)

        XCTAssertTrue(error.isRetryable)
        XCTAssertTrue(error.errorDescription!.contains("503"))
    }

    func testParsingFailedNotRetryable() {
        let underlying = NSError(domain: "JSON", code: 1, userInfo: nil)
        let error = AIServiceError.parsingFailed(underlying: underlying)

        XCTAssertFalse(error.isRetryable)
    }

    // MARK: - LocationError Tests

    func testPermissionDeniedError() {
        let error = LocationError.permissionDenied

        XCTAssertNotNil(error.errorDescription)
        XCTAssertTrue(error.errorDescription!.contains("denied"))
        XCTAssertNotNil(error.recoverySuggestion)
        XCTAssertTrue(error.recoverySuggestion!.contains("Settings"))
    }

    func testPermissionRestrictedError() {
        let error = LocationError.permissionRestricted

        XCTAssertNotNil(error.errorDescription)
        XCTAssertTrue(error.errorDescription!.contains("restricted"))
    }

    func testServiceDisabledError() {
        let error = LocationError.serviceDisabled

        XCTAssertNotNil(error.errorDescription)
        XCTAssertNotNil(error.recoverySuggestion)
    }

    func testLocationUnknownError() {
        let error = LocationError.locationUnknown

        XCTAssertNotNil(error.errorDescription)
        XCTAssertTrue(error.errorDescription!.contains("Unable to determine"))
    }

    func testGeocodingFailedError() {
        let underlying = NSError(domain: "Geocoding", code: 1, userInfo: nil)
        let error = LocationError.geocodingFailed(underlying: underlying)

        XCTAssertNotNil(error.errorDescription)
        XCTAssertNotNil(error.recoverySuggestion)
    }

    // MARK: - ErrorRecovery Tests

    func testErrorRecoverySuccess() async throws {
        var callCount = 0

        let recovery = ErrorRecovery<Int> {
            callCount += 1
            return 42
        }

        let result = try await recovery.execute()
        XCTAssertEqual(result, 42)
        XCTAssertEqual(callCount, 1)
    }

    func testErrorRecoveryFallback() async throws {
        var primaryCalled = false
        var fallbackCalled = false

        let recovery = ErrorRecovery<Int> {
            primaryCalled = true
            throw SpotDataError.emptyDataset
        }.fallback {
            fallbackCalled = true
            return 99
        }

        let result = try await recovery.execute()
        XCTAssertEqual(result, 99)
        XCTAssertTrue(primaryCalled)
        XCTAssertTrue(fallbackCalled)
    }

    func testErrorRecoveryMultipleFallbacks() async throws {
        var callOrder: [String] = []

        let recovery = ErrorRecovery<String> {
            callOrder.append("primary")
            throw SpotDataError.emptyDataset
        }.fallback {
            callOrder.append("fallback1")
            throw SpotDataError.emptyDataset
        }.fallback {
            callOrder.append("fallback2")
            return "success"
        }

        let result = try await recovery.execute()
        XCTAssertEqual(result, "success")
        XCTAssertEqual(callOrder, ["primary", "fallback1", "fallback2"])
    }

    func testErrorRecoveryAllFail() async {
        let recovery = ErrorRecovery<Int> {
            throw SpotDataError.emptyDataset
        }.fallback {
            throw SpotDataError.emptyDataset
        }

        do {
            _ = try await recovery.execute()
            XCTFail("Should have thrown")
        } catch {
            XCTAssertTrue(error is SpotDataError)
        }
    }

    // MARK: - Edge Case Tests

    func testOperatingHoursNoSchedule() {
        let hours = OperatingHours(schedule: [:])

        // Should return false for any date when no schedule
        let date = Date()
        XCTAssertFalse(hours.isOpen(at: date, calendar: .current))
    }

    func testSpotQueryToggleTierAddsAndRemoves() {
        var query = SpotQuery()

        query.toggle(tier: .elite)
        XCTAssertTrue(query.tiers.contains(.elite))

        query.toggle(tier: .elite)
        XCTAssertFalse(query.tiers.contains(.elite))
    }

    func testSpotQueryToggleAttributeAddsAndRemoves() {
        var query = SpotQuery()

        query.toggle(attribute: .deepFocus)
        XCTAssertTrue(query.attributes.contains(.deepFocus))

        query.toggle(attribute: .deepFocus)
        XCTAssertFalse(query.attributes.contains(.deepFocus))
    }

    func testDistanceFormatterVeryShortDistance() {
        // Test < 160 meters (< 0.1 miles)
        let formatted = DistanceFormatter.format(meters: 50)
        XCTAssertEqual(formatted, "< 0.1 mi")
    }

    func testDistanceFormatterExactlyOneMile() {
        let formatted = DistanceFormatter.format(meters: 1609.34)
        XCTAssertEqual(formatted, "1.0 mi")
    }

    func testEstimatedTimeLessThanOneMinute() {
        let time = DistanceFormatter.estimatedTime(meters: 10, mode: .driving)
        XCTAssertEqual(time, "< 1 min drive")
    }

    func testEstimatedTimeExactlyOneMinute() {
        let time = DistanceFormatter.estimatedTime(meters: 80, mode: .walking) // 80m / 80m per min = 1 min
        XCTAssertEqual(time, "1 min walk")
    }

    func testFrictionWarningEquality() {
        let warning1 = FrictionWarning(
            message: "Test",
            detail: "Detail",
            severity: .high,
            icon: "icon"
        )
        let warning2 = FrictionWarning(
            message: "Test",
            detail: "Different detail",
            severity: .high,
            icon: "different-icon"
        )

        // Equality based on message and severity only
        XCTAssertEqual(warning1, warning2)
    }

    func testFrictionWarningSeverityComparison() {
        XCTAssertTrue(FrictionWarning.Severity.low < .medium)
        XCTAssertTrue(FrictionWarning.Severity.medium < .high)
        XCTAssertFalse(FrictionWarning.Severity.high < .low)
    }

    // MARK: - Mock Loader Tests

    func testFailingSpotLoader() async {
        let loader = FailingSpotLoader(error: SpotDataError.emptyDataset)

        do {
            _ = try await loader.loadSpots()
            XCTFail("Should have thrown")
        } catch {
            XCTAssertTrue(error is SpotDataError)
        }
    }

    func testDelayedSpotLoader() async {
        let spots = [IntegrationTests.testSpot]
        let loader = DelayedSpotLoader(spots: spots, delay: 0.1)

        let start = Date()
        let result = try? await loader.loadSpots()
        let elapsed = Date().timeIntervalSince(start)

        XCTAssertNotNil(result)
        XCTAssertEqual(result?.count, 1)
        XCTAssertGreaterThanOrEqual(elapsed, 0.1)
    }
}

// MARK: - Mock Loaders

struct FailingSpotLoader: SpotLoader {
    let error: Error

    func loadSpots() async throws -> [LocationSpot] {
        throw error
    }
}

struct DelayedSpotLoader: SpotLoader {
    let spots: [LocationSpot]
    let delay: TimeInterval

    func loadSpots() async throws -> [LocationSpot] {
        try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
        return spots
    }
}

// MARK: - Reference to IntegrationTests for Test Spot

extension IntegrationTests {
    // Already defined in IntegrationTests.swift
}
