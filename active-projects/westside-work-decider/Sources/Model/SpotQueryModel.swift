import SwiftUI

final class SpotQueryModel: ObservableObject {
    @Published var query: SpotQuery

    init(query: SpotQuery = SpotQuery()) {
        self.query = query
    }

    func applyPreset(_ preset: SessionPreset?) {
        query = SpotQuery.fromPreset(preset)
    }
}

extension SpotQuery {
    static func fromPreset(_ preset: SessionPreset?) -> SpotQuery {
        guard let preset else { return SpotQuery() }
        var query = SpotQuery()
        query.attributes = preset.tags
        if preset.requiresOpenLate { query.openLate = true }
        if preset.prefersElite { query.tiers.insert(.elite) }
        return query
    }
}
