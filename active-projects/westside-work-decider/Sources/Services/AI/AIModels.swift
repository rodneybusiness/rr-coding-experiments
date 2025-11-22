import Foundation
import CoreLocation

struct AIRecommendationRequest: Codable {
    let userMessage: String
    let time: Date
    let coordinate: CLLocationCoordinate2D?
    let activeFilters: SpotQuery?
    let candidateSpots: [SpotSummary]
}

struct SpotSummary: Codable, Identifiable {
    let id: UUID
    let name: String
    let neighborhood: String
    let tier: Tier
    let placeType: PlaceType
    let attributes: [AttributeTag]
    let criticalFieldNotes: String
    let distanceMeters: Double?
}

struct AIRecommendationResponse: Codable {
    let filters: SpotQuery?
    let sort: SpotSort?
    let preset: SessionPreset?
    let recommendations: [AIRecommendationItem]
}

struct AIRecommendationItem: Codable, Identifiable {
    let id: UUID
    let reason: String
}

protocol AIRecommendationService {
    func recommend(request: AIRecommendationRequest) async throws -> AIRecommendationResponse
}
