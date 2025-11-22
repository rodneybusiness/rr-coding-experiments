#if canImport(WestsideWorkDecider)
import XCTest
@testable import WestsideWorkDecider

final class SpotStoreRoundTripTests: XCTestCase {
    func testQuerySummaryDescribesActiveFilters() {
        var query = SpotQuery()
        query.tier = .elite
        query.attributes = [.deepFocus, .easyParking]
        query.openLate = true
        XCTAssertEqual(query.summaryDescription(), "Elite • Deep Focus, Easy Parking • Open late")
    }

    func testSimulatedAIRespectsDistanceCap() async throws {
        let loader = CompositeSpotLoader()
        let store = SpotStore(loader: loader)
        try await Task.sleep(nanoseconds: 500_000_000)
        let anchor = store.anchorLocation(for: .init())
        let summaries = store.spots.map { spot in
            SpotSummary(
                id: spot.id,
                name: spot.name,
                neighborhood: spot.neighborhood,
                tier: spot.tier,
                placeType: spot.placeType,
                attributes: spot.attributes,
                criticalFieldNotes: spot.criticalFieldNotes,
                distanceMeters: spot.distance(from: anchor)
            )
        }
        let ai = SimulatedAIService()
        let response = try await ai.recommend(
            request: AIRecommendationRequest(
                userMessage: "closest deep focus",
                time: Date(),
                coordinate: anchor?.coordinate,
                activeFilters: nil,
                candidateSpots: Array(summaries.prefix(10))
            )
        )
        XCTAssertLessThanOrEqual(response.recommendations.count, 5)
    }
}
#endif
