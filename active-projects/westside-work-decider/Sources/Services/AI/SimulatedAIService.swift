import Foundation
import CoreLocation

struct SimulatedAIService: AIRecommendationService {
    func recommend(request: AIRecommendationRequest) async throws -> AIRecommendationResponse {
        let tags = inferredTags(from: request.userMessage)
        var query = request.activeFilters ?? SpotQuery()
        query.attributes.formUnion(tags)

        // Heuristic: if user asks for "late" or it's after 6pm, prefer OpenLate
        let hour = Calendar.current.component(.hour, from: request.time)
        if request.userMessage.lowercased().contains("late") || hour >= 18 {
            query.openLate = true
        }

        if request.userMessage.lowercased().contains("home") {
            query.closeToHome = true
        }
        if request.userMessage.lowercased().contains("office") || request.userMessage.lowercased().contains("work") {
            query.closeToWork = true
        }

        let sort: SpotSort = request.userMessage.lowercased().contains("closest") ? .distance : .timeOfDay

        let ranked = request.candidateSpots.sorted { lhs, rhs in
            switch (lhs.distanceMeters, rhs.distanceMeters) {
            case let (l?, r?): return l < r
            case (.some, .none): return true
            case (.none, .some): return false
            default: return lhs.sentimentFallback > rhs.sentimentFallback
            }
        }
        let items = ranked.prefix(5).map { spot in
            AIRecommendationItem(id: spot.id, reason: explanation(for: spot, tags: tags))
        }

        let preset = presetFrom(tags: tags, request: request)
        return AIRecommendationResponse(filters: query, sort: sort, preset: preset, recommendations: items)
    }

    private func inferredTags(from message: String) -> Set<AttributeTag> {
        let lower = message.lowercased()
        var result: Set<AttributeTag> = []
        if lower.contains("parking") { result.insert(.easyParking) }
        if lower.contains("deep") { result.insert(.deepFocus) }
        if lower.contains("focus") { result.insert(.deepFocus) }
        if lower.contains("social") || lower.contains("body") { result.insert(.bodyDoubling) }
        if lower.contains("call") { result.insert(.callFriendly) }
        if lower.contains("food") || lower.contains("lunch") { result.insert(.realFood) }
        if lower.contains("coffee") { result.insert(.eliteCoffee) }
        if lower.contains("outdoor") || lower.contains("patio") { result.insert(.patioPower) }
        return result
    }

    private func explanation(for spot: SpotSummary, tags: Set<AttributeTag>) -> String {
        var parts: [String] = []
        if let distance = spot.distanceMeters {
            let miles = distance / 1609.34
            parts.append(String(format: "%.1f mi away", miles))
        }
        if !tags.isEmpty {
            let matched = spot.attributes.filter { tags.contains($0) }
            if !matched.isEmpty {
                parts.append("matches " + matched.map { $0.rawValue }.joined(separator: ", "))
            }
        }
        parts.append(spot.criticalFieldNotes)
        return parts.joined(separator: " • ")
    }

    private func presetFrom(tags: Set<AttributeTag>, request: AIRecommendationRequest) -> SessionPreset? {
        if tags.contains(.deepFocus) {
            return SessionPreset(title: "Deep Focus", description: "Quiet, power-friendly spots for heads-down work", tags: [.deepFocus, .powerHeavy], requiresOpenLate: false, prefersElite: false)
        }
        if tags.contains(.bodyDoubling) {
            return SessionPreset(title: "Body Doubling", description: "Social energy with good wifi", tags: [.bodyDoubling], requiresOpenLate: false, prefersElite: false)
        }
        if request.userMessage.contains("90") {
            return SessionPreset(title: "90-minute sprint", description: "Low-friction, easy parking", tags: [.easyParking], requiresOpenLate: false, prefersElite: false)
        }
        return nil
    }
}
