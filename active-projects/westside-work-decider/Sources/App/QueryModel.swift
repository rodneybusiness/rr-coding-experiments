import Foundation

@MainActor
final class QueryModel: ObservableObject {
    @Published var query: SpotQuery = SpotQuery()
    @Published var sort: SpotSort = .distance
    @Published var lastAppliedPreset: SessionPreset? = nil

    func apply(preset: SessionPreset?) {
        lastAppliedPreset = preset
        guard let preset else { return }
        var newQuery = SpotQuery()
        newQuery.attributes = preset.tags
        if preset.requiresOpenLate { newQuery.openLate = true }
        if preset.prefersElite { newQuery.tiers.insert(.elite) }
        query = newQuery
        sort = .timeOfDay
    }

    func apply(aiResponse: AIRecommendationResponse) {
        if let preset = aiResponse.preset {
            apply(preset: preset)
        }
        if let filters = aiResponse.filters {
            query = filters
        }
        if let sort = aiResponse.sort {
            self.sort = sort
        }
    }
}
