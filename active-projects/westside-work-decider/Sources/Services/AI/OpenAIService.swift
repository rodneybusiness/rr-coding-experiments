import Foundation
import CoreLocation

struct OpenAIService: AIRecommendationService {
    enum ServiceError: Error {
        case missingAPIKey
        case invalidResponse
    }

    var apiKey: String
    var model: String
    var urlSession: URLSession = .shared
    var maxCandidates: Int = 12

    init(apiKey: String, model: String = "gpt-4o-mini") {
        self.apiKey = apiKey
        self.model = model
    }

    static func makeDefault() -> AIRecommendationService {
        if let key = ProcessInfo.processInfo.environment["OPENAI_API_KEY"], !key.isEmpty {
            return OpenAIService(apiKey: key)
        }
        return SimulatedAIService()
    }

    func recommend(request: AIRecommendationRequest) async throws -> AIRecommendationResponse {
        guard !apiKey.isEmpty else { throw ServiceError.missingAPIKey }

        let trimmedCandidates = Array(request.candidateSpots.prefix(maxCandidates))
        let payload = OpenAIChatPayload(
            model: model,
            messages: buildMessages(from: request, candidates: trimmedCandidates)
        )

        let data = try JSONEncoder().encode(payload)
        var urlRequest = URLRequest(url: URL(string: "https://api.openai.com/v1/chat/completions")!)
        urlRequest.httpMethod = "POST"
        urlRequest.addValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        urlRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = data

        let (responseData, response) = try await urlSession.data(for: urlRequest)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else { throw ServiceError.invalidResponse }
        let decoded = try JSONDecoder().decode(OpenAIChatResponse.self, from: responseData)
        guard let message = decoded.choices.first?.message.content else { throw ServiceError.invalidResponse }

        let ai = try JSONDecoder().decode(AIRecommendationResponse.self, from: Data(message.utf8))
        return ai
    }

    private func buildMessages(from request: AIRecommendationRequest, candidates: [SpotSummary]) -> [OpenAIMessage] {
        let systemPrompt = "You are an assistant that returns JSON matching AIRecommendationResponse. Only recommend from provided spots."
        let context = AIChatContext(
            userMessage: request.userMessage,
            time: request.time,
            coordinate: request.coordinate,
            activeFilters: request.activeFilters,
            candidateSpots: candidates
        )
        let contextJSON = (try? String(data: JSONEncoder().encode(context), encoding: .utf8)) ?? "{}"
        return [
            OpenAIMessage(role: "system", content: systemPrompt),
            OpenAIMessage(role: "user", content: contextJSON)
        ]
    }
}

private struct AIChatContext: Codable {
    let userMessage: String
    let time: Date
    let coordinate: CLLocationCoordinate2D?
    let activeFilters: SpotQuery?
    let candidateSpots: [SpotSummary]
}

private struct OpenAIChatPayload: Codable {
    let model: String
    let messages: [OpenAIMessage]
}

private struct OpenAIMessage: Codable {
    let role: String
    let content: String
}

private struct OpenAIChatResponse: Codable {
    let choices: [Choice]

    struct Choice: Codable {
        let message: OpenAIMessage
    }
}
