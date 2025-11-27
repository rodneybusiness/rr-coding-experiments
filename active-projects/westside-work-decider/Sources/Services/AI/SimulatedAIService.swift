import Foundation
import CoreLocation

// MARK: - SimulatedAIService

/// An offline, rule-based AI service that provides intelligent recommendations
/// without requiring an API key. Uses keyword extraction, time-of-day heuristics,
/// and smart ranking to deliver contextual results.
struct SimulatedAIService: AIRecommendationService {

    // MARK: - Configuration

    struct Configuration {
        var maxRecommendations: Int = 5
        var noveltyBoost: Double = 0.5
        var distanceWeight: Double = 1.0
        var attributeMatchWeight: Double = 2.0
        var sentimentWeight: Double = 0.5
        var recentVisitPenaltyDays: Int = 3

        static let `default` = Configuration()
    }

    var configuration: Configuration

    init(configuration: Configuration = .default) {
        self.configuration = configuration
    }

    // MARK: - AIRecommendationService

    func recommend(request: AIRecommendationRequest) async throws -> AIRecommendationResponse {
        let analysis = analyzeMessage(request.userMessage, time: request.time)

        // Build query from analysis
        var query = request.activeFilters ?? SpotQuery()
        query.attributes.formUnion(analysis.attributes)

        // Apply boolean filters from analysis
        if analysis.wantsOpenLate { query.openLate = true }
        if analysis.wantsCloseToHome { query.closeToHome = true }
        if analysis.wantsCloseToWork { query.closeToWork = true }

        // Determine sort order
        let sort = determineSortOrder(from: analysis, request: request)

        // Score and rank candidates
        let rankedSpots = rankCandidates(
            request.candidateSpots,
            analysis: analysis,
            request: request
        )

        // Build recommendations with explanations
        let recommendations = rankedSpots.prefix(configuration.maxRecommendations).map { scored in
            AIRecommendationItem(
                id: scored.spot.id,
                reason: buildExplanation(for: scored, analysis: analysis)
            )
        }

        // Infer preset if applicable
        let preset = inferPreset(from: analysis)

        return AIRecommendationResponse(
            filters: query,
            sort: sort,
            preset: preset,
            recommendations: Array(recommendations)
        )
    }

    // MARK: - Message Analysis

    private struct MessageAnalysis {
        var attributes: Set<AttributeTag> = []
        var wantsOpenLate: Bool = false
        var wantsCloseToHome: Bool = false
        var wantsCloseToWork: Bool = false
        var wantsClosest: Bool = false
        var wantsQuiet: Bool = false
        var wantsSocial: Bool = false
        var wantsCheap: Bool = false
        var wantsLuxury: Bool = false
        var wantsNovelty: Bool = false
        var mentionedNeighborhoods: Set<String> = []
        var timeContext: TimeOfDayContext = .any
        var urgency: Urgency = .normal
        var sessionLength: SessionLength = .normal

        enum TimeOfDayContext {
            case earlyMorning, morning, afternoon, evening, lateNight, any
        }

        enum Urgency {
            case immediate, normal, flexible
        }

        enum SessionLength {
            case quick, normal, extended
        }
    }

    private func analyzeMessage(_ message: String, time: Date) -> MessageAnalysis {
        let lower = message.lowercased()
        var analysis = MessageAnalysis()

        // Extract attributes using comprehensive keyword matching
        analysis.attributes = extractAttributes(from: lower)

        // Location preferences
        if containsAny(lower, ["home", "house", "my place"]) {
            analysis.wantsCloseToHome = true
        }
        if containsAny(lower, ["office", "work", "job", "commute"]) {
            analysis.wantsCloseToWork = true
        }
        if containsAny(lower, ["closest", "nearest", "nearby", "close", "walking distance"]) {
            analysis.wantsClosest = true
        }

        // Time preferences
        let hour = Calendar.current.component(.hour, from: time)
        if containsAny(lower, ["late", "night", "evening", "tonight", "after hours", "midnight"]) || hour >= 20 {
            analysis.wantsOpenLate = true
            analysis.timeContext = .lateNight
            analysis.attributes.insert(.nightOwl)
        } else if containsAny(lower, ["morning", "early", "breakfast", "am", "dawn"]) || (hour >= 5 && hour < 9) {
            analysis.timeContext = .earlyMorning
            analysis.attributes.insert(.earlyBird)
        } else if hour >= 17 {
            analysis.timeContext = .evening
        } else if hour >= 12 {
            analysis.timeContext = .afternoon
        } else {
            analysis.timeContext = .morning
        }

        // Atmosphere preferences
        if containsAny(lower, ["quiet", "silent", "peaceful", "focus", "concentrate", "heads down", "study", "deep work"]) {
            analysis.wantsQuiet = true
            analysis.attributes.insert(.deepFocus)
        }
        if containsAny(lower, ["social", "people", "busy", "energy", "vibe", "lively", "bustling", "cowork"]) {
            analysis.wantsSocial = true
            analysis.attributes.insert(.bodyDoubling)
        }

        // Budget preferences
        if containsAny(lower, ["cheap", "free", "budget", "affordable", "inexpensive", "low cost"]) {
            analysis.wantsCheap = true
        }
        if containsAny(lower, ["nice", "fancy", "upscale", "premium", "best", "top", "luxur", "high end"]) {
            analysis.wantsLuxury = true
            analysis.attributes.insert(.luxury)
        }

        // Novelty preferences
        if containsAny(lower, ["new", "different", "haven't been", "try something", "surprise", "change", "explore"]) {
            analysis.wantsNovelty = true
        }

        // Session length
        if containsAny(lower, ["quick", "short", "30 min", "hour", "sprint", "brief", "90 min"]) {
            analysis.sessionLength = .quick
            analysis.attributes.insert(.easyParking)
        } else if containsAny(lower, ["all day", "long", "extended", "full day", "camp out", "marathon"]) {
            analysis.sessionLength = .extended
            analysis.attributes.insert(.powerHeavy)
            analysis.attributes.insert(.realFood)
        }

        // Urgency
        if containsAny(lower, ["now", "asap", "urgent", "immediately", "right now", "quick"]) {
            analysis.urgency = .immediate
            analysis.wantsClosest = true
        }

        return analysis
    }

    private func extractAttributes(from message: String) -> Set<AttributeTag> {
        var result: Set<AttributeTag> = []

        // Comprehensive keyword mapping
        let keywordMap: [(keywords: [String], tag: AttributeTag)] = [
            // Power & outlets
            (["power", "outlet", "charge", "plug", "electric", "battery"], .powerHeavy),

            // Parking & access
            (["parking", "park", "car", "drive", "lot", "garage", "valet"], .easyParking),

            // Comfort
            (["ergonomic", "comfortable", "chair", "desk", "seating"], .ergonomic),

            // Social & coworking
            (["social", "body doubling", "people", "company", "community", "cowork", "networking"], .bodyDoubling),

            // Focus & quiet
            (["focus", "quiet", "deep", "concentrate", "study", "silent", "peaceful"], .deepFocus),

            // Food & dining
            (["food", "lunch", "meal", "eat", "hungry", "breakfast", "dinner", "snack", "kitchen"], .realFood),

            // Calls & meetings
            (["call", "phone", "meeting", "zoom", "video", "conference", "teams"], .callFriendly),

            // Outdoor
            (["outdoor", "patio", "outside", "fresh air", "sun", "garden", "terrace"], .patioPower),

            // Day pass
            (["day pass", "drop-in", "single day", "visitor", "guest"], .dayPass),

            // Early hours
            (["early", "morning", "am", "breakfast", "dawn", "sunrise"], .earlyBird),

            // Late hours
            (["late", "night", "evening", "pm", "after hours", "midnight"], .nightOwl),

            // Luxury
            (["luxury", "premium", "upscale", "fancy", "nice", "bougie", "high-end"], .luxury),

            // Coffee
            (["coffee", "espresso", "latte", "cafe", "cappuccino", "brew"], .eliteCoffee)
        ]

        for (keywords, tag) in keywordMap {
            for keyword in keywords {
                if message.contains(keyword) {
                    result.insert(tag)
                    break
                }
            }
        }

        return result
    }

    private func containsAny(_ text: String, _ keywords: [String]) -> Bool {
        keywords.contains { text.contains($0) }
    }

    // MARK: - Scoring & Ranking

    private struct ScoredSpot {
        let spot: SpotSummary
        var score: Double
        var matchedAttributes: Set<AttributeTag>
        var distanceScore: Double
        var noveltyScore: Double
        var timeScore: Double
    }

    private func rankCandidates(
        _ candidates: [SpotSummary],
        analysis: MessageAnalysis,
        request: AIRecommendationRequest
    ) -> [ScoredSpot] {

        var scored = candidates.map { spot -> ScoredSpot in
            var result = ScoredSpot(
                spot: spot,
                score: 0,
                matchedAttributes: [],
                distanceScore: 0,
                noveltyScore: 0,
                timeScore: 0
            )

            // Attribute matching (highest weight)
            let spotAttrs = Set(spot.attributes)
            result.matchedAttributes = analysis.attributes.intersection(spotAttrs)
            let attrScore = Double(result.matchedAttributes.count) * configuration.attributeMatchWeight
            result.score += attrScore

            // Distance scoring
            if let distance = spot.distanceMeters {
                // Normalize: closer = higher score, max ~10 miles consideration
                let normalizedDistance = min(distance, 16000) / 16000
                result.distanceScore = (1.0 - normalizedDistance) * configuration.distanceWeight

                // Boost if user explicitly wants closest
                if analysis.wantsClosest {
                    result.distanceScore *= 2.0
                }
                result.score += result.distanceScore
            }

            // Sentiment score contribution
            result.score += spot.sentimentFallback * configuration.sentimentWeight * 0.1

            // Time-of-day scoring
            result.timeScore = calculateTimeScore(spot: spot, analysis: analysis, time: request.time)
            result.score += result.timeScore

            // Novelty boost
            if analysis.wantsNovelty {
                result.noveltyScore = configuration.noveltyBoost
                result.score += result.noveltyScore
            }

            // Tier bonus
            if spot.tier == .elite {
                result.score += analysis.wantsLuxury ? 2.0 : 0.5
            } else if spot.tier == .reliable {
                result.score += 0.2
            }

            // Quick session bonus for easy parking spots
            if analysis.sessionLength == .quick {
                if spotAttrs.contains(.easyParking) {
                    result.score += 1.0
                }
            }

            // Extended session bonus for power and food
            if analysis.sessionLength == .extended {
                if spotAttrs.contains(.powerHeavy) { result.score += 0.5 }
                if spotAttrs.contains(.realFood) { result.score += 0.5 }
            }

            // Budget preference
            if analysis.wantsCheap && !spotAttrs.contains(.luxury) {
                result.score += 0.3
            }

            return result
        }

        // Sort by score descending
        scored.sort { $0.score > $1.score }

        return scored
    }

    private func calculateTimeScore(spot: SpotSummary, analysis: MessageAnalysis, time: Date) -> Double {
        let spotAttrs = Set(spot.attributes)
        var score: Double = 0

        let hour = Calendar.current.component(.hour, from: time)

        switch analysis.timeContext {
        case .earlyMorning:
            if spotAttrs.contains(.earlyBird) { score += 1.5 }
            if spotAttrs.contains(.eliteCoffee) { score += 0.5 }
        case .lateNight:
            if spotAttrs.contains(.nightOwl) { score += 1.5 }
        case .evening:
            if spotAttrs.contains(.nightOwl) { score += 0.5 }
        case .afternoon, .morning:
            // Most places good during these times
            break
        case .any:
            break
        }

        // Lunch time boost for food places
        if hour >= 11 && hour < 14 {
            if spotAttrs.contains(.realFood) { score += 0.5 }
        }

        return score
    }

    // MARK: - Sort Order

    private func determineSortOrder(from analysis: MessageAnalysis, request: AIRecommendationRequest) -> SpotSort {
        if analysis.wantsClosest || analysis.urgency == .immediate {
            return .distance
        }

        if analysis.wantsLuxury {
            return .tier
        }

        if analysis.wantsQuiet || analysis.wantsSocial {
            return .sentiment
        }

        // Default to time-of-day for contextual recommendations
        return .timeOfDay
    }

    // MARK: - Preset Inference

    private func inferPreset(from analysis: MessageAnalysis) -> SessionPreset? {
        // Deep Focus
        if analysis.wantsQuiet || analysis.attributes.contains(.deepFocus) {
            return SessionPreset.deepFocus
        }

        // Body Doubling
        if analysis.wantsSocial || analysis.attributes.contains(.bodyDoubling) {
            return SessionPreset.bodyDoubling
        }

        // Quick Sprint
        if analysis.sessionLength == .quick {
            return SessionPreset.quickSprint
        }

        // Late Night
        if analysis.wantsOpenLate || analysis.timeContext == .lateNight {
            return SessionPreset.lateNight
        }

        return nil
    }

    // MARK: - Explanation Building

    private func buildExplanation(for scored: ScoredSpot, analysis: MessageAnalysis) -> String {
        var parts: [String] = []

        // Distance
        if let distance = scored.spot.distanceMeters {
            let miles = distance / 1609.34
            if miles < 0.3 {
                parts.append("Very close")
            } else if miles < 1.0 {
                parts.append(String(format: "%.1f mi", miles))
            } else {
                parts.append(String(format: "%.1f mi away", miles))
            }
        }

        // Matched attributes
        if !scored.matchedAttributes.isEmpty {
            let matched = scored.matchedAttributes
                .filter { $0 != .unknown }
                .map { $0.shortName }
                .sorted()

            if matched.count == 1 {
                parts.append("has \(matched[0])")
            } else if matched.count == 2 {
                parts.append("\(matched[0]) + \(matched[1])")
            } else if matched.count <= 4 {
                parts.append("matches \(matched.joined(separator: ", "))")
            } else {
                parts.append("matches \(matched.count) criteria")
            }
        }

        // Tier mention for luxury seekers
        if scored.spot.tier == .elite && analysis.wantsLuxury {
            parts.append("Elite tier")
        }

        // Time context
        if analysis.timeContext == .lateNight && scored.spot.attributes.contains(.nightOwl) {
            parts.append("Open late")
        }
        if analysis.timeContext == .earlyMorning && scored.spot.attributes.contains(.earlyBird) {
            parts.append("Opens early")
        }

        // Critical notes (abbreviated)
        let notes = scored.spot.criticalFieldNotes
        if !notes.isEmpty {
            if notes.count < 50 {
                parts.append(notes)
            } else {
                let abbreviated = String(notes.prefix(45)) + "..."
                parts.append(abbreviated)
            }
        }

        // Novelty mention
        if analysis.wantsNovelty && scored.noveltyScore > 0 {
            parts.append("Try something new")
        }

        return parts.isEmpty ? "Good option for your needs" : parts.joined(separator: " • ")
    }
}
