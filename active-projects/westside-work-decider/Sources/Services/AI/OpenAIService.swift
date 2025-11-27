import Foundation
import CoreLocation

// MARK: - OpenAIService

/// An AI recommendation service that uses OpenAI's API for intelligent spot recommendations.
/// Features caching, timeout handling, retry logic, and falls back to SimulatedAIService on failure.
struct OpenAIService: AIRecommendationService {

    // MARK: - Configuration

    struct Configuration {
        var model: String = "gpt-4o-mini"
        var maxCandidates: Int = 12
        var timeoutSeconds: TimeInterval = 30
        var maxRetries: Int = 2
        var cacheDurationSeconds: TimeInterval = 300  // 5 minutes
        var temperature: Double = 0.3  // Lower = more consistent

        static let `default` = Configuration()
    }

    // MARK: - Properties

    var apiKey: String
    var configuration: Configuration
    var urlSession: URLSession
    private let cache: ResponseCache
    private let fallbackService: SimulatedAIService

    // MARK: - Initialization

    init(apiKey: String, configuration: Configuration = .default) {
        self.apiKey = apiKey
        self.configuration = configuration
        self.cache = ResponseCache(ttl: configuration.cacheDurationSeconds)
        self.fallbackService = SimulatedAIService()

        // Configure URLSession with timeout
        let sessionConfig = URLSessionConfiguration.default
        sessionConfig.timeoutIntervalForRequest = configuration.timeoutSeconds
        sessionConfig.timeoutIntervalForResource = configuration.timeoutSeconds * 2
        self.urlSession = URLSession(configuration: sessionConfig)
    }

    /// Creates the default AI service - OpenAI if key available, otherwise Simulated
    static func makeDefault() -> AIRecommendationService {
        if let key = ProcessInfo.processInfo.environment["OPENAI_API_KEY"], !key.isEmpty {
            return OpenAIService(apiKey: key)
        }
        return SimulatedAIService()
    }

    // MARK: - AIRecommendationService

    func recommend(request: AIRecommendationRequest) async throws -> AIRecommendationResponse {
        guard !apiKey.isEmpty else {
            throw AIServiceError.missingAPIKey
        }

        // Check cache first
        let cacheKey = generateCacheKey(for: request)
        if let cached = cache.get(for: cacheKey) {
            return cached
        }

        // Prepare request
        let trimmedCandidates = Array(request.candidateSpots.prefix(configuration.maxCandidates))

        // Try with retries
        var lastError: Error?
        for attempt in 0..<configuration.maxRetries {
            do {
                let response = try await executeRequest(request, candidates: trimmedCandidates)

                // Cache successful response
                cache.set(response, for: cacheKey)

                return response

            } catch let error as AIServiceError where error.isRetryable {
                lastError = error
                // Exponential backoff
                if attempt < configuration.maxRetries - 1 {
                    let delay = UInt64(pow(2.0, Double(attempt))) * 1_000_000_000
                    try? await Task.sleep(nanoseconds: delay)
                }
            } catch {
                lastError = error
                break  // Non-retryable error
            }
        }

        // Fall back to simulated service on failure
        print("OpenAI request failed, falling back to simulated: \(lastError?.localizedDescription ?? "unknown")")
        return try await fallbackService.recommend(request: request)
    }

    // MARK: - Request Execution

    private func executeRequest(
        _ request: AIRecommendationRequest,
        candidates: [SpotSummary]
    ) async throws -> AIRecommendationResponse {

        let payload = buildPayload(from: request, candidates: candidates)

        guard let payloadData = try? JSONEncoder().encode(payload) else {
            throw AIServiceError.invalidResponse(details: "Failed to encode request")
        }

        var urlRequest = URLRequest(url: URL(string: "https://api.openai.com/v1/chat/completions")!)
        urlRequest.httpMethod = "POST"
        urlRequest.addValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        urlRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = payloadData

        let (responseData, response): (Data, URLResponse)
        do {
            (responseData, response) = try await urlSession.data(for: urlRequest)
        } catch let urlError as URLError {
            switch urlError.code {
            case .timedOut:
                throw AIServiceError.timeout
            case .notConnectedToInternet, .networkConnectionLost:
                throw AIServiceError.networkError(underlying: urlError)
            default:
                throw AIServiceError.networkError(underlying: urlError)
            }
        }

        guard let http = response as? HTTPURLResponse else {
            throw AIServiceError.invalidResponse(details: "Non-HTTP response")
        }

        // Handle HTTP errors
        switch http.statusCode {
        case 200:
            break  // Success
        case 401:
            throw AIServiceError.missingAPIKey
        case 429:
            let retryAfter = http.value(forHTTPHeaderField: "Retry-After").flatMap { TimeInterval($0) }
            throw AIServiceError.rateLimited(retryAfter: retryAfter)
        case 500..<600:
            throw AIServiceError.serverError(statusCode: http.statusCode)
        default:
            throw AIServiceError.invalidResponse(details: "HTTP \(http.statusCode)")
        }

        // Parse response
        let decoded: OpenAIChatResponse
        do {
            decoded = try JSONDecoder().decode(OpenAIChatResponse.self, from: responseData)
        } catch {
            throw AIServiceError.parsingFailed(underlying: error)
        }

        guard let messageContent = decoded.choices.first?.message.content else {
            throw AIServiceError.invalidResponse(details: "No message content")
        }

        // Extract JSON from response (handle markdown code blocks)
        let jsonString = extractJSON(from: messageContent)

        guard let jsonData = jsonString.data(using: .utf8) else {
            throw AIServiceError.invalidResponse(details: "Invalid JSON encoding")
        }

        do {
            return try JSONDecoder().decode(AIRecommendationResponse.self, from: jsonData)
        } catch {
            throw AIServiceError.parsingFailed(underlying: error)
        }
    }

    // MARK: - Payload Building

    private func buildPayload(from request: AIRecommendationRequest, candidates: [SpotSummary]) -> OpenAIChatPayload {
        let systemPrompt = buildSystemPrompt()
        let userPrompt = buildUserPrompt(from: request, candidates: candidates)

        return OpenAIChatPayload(
            model: configuration.model,
            messages: [
                OpenAIMessage(role: "system", content: systemPrompt),
                OpenAIMessage(role: "user", content: userPrompt)
            ],
            temperature: configuration.temperature,
            responseFormat: ResponseFormat(type: "json_object")
        )
    }

    private func buildSystemPrompt() -> String {
        """
        You are an AI assistant for a remote work spot finder app. Your job is to recommend work spots from a curated list based on user queries.

        CRITICAL RULES:
        1. ONLY recommend spots from the provided candidateSpots list - never invent locations
        2. Return VALID JSON matching the AIRecommendationResponse schema exactly
        3. Include 1-5 recommendations, prioritized by relevance to the user's needs
        4. Provide brief, helpful reasons for each recommendation

        Response Schema:
        {
          "filters": { "tiers": [], "neighborhoods": [], "placeTypes": [], "attributes": [], "openLate": null, ... },
          "sort": "distance" | "sentiment" | "tier" | "timeOfDay",
          "preset": null | { "title": "...", "description": "...", "tags": [...], "requiresOpenLate": false, "prefersElite": false },
          "recommendations": [
            { "id": "spot-id", "reason": "Brief explanation why this spot fits" }
          ]
        }

        Attributes to recognize: powerHeavy, easyParking, ergonomic, bodyDoubling, deepFocus, realFood, callFriendly, patioPower, dayPass, earlyBird, nightOwl, luxury, eliteCoffee

        Sort options:
        - "distance": User wants closest spots
        - "sentiment": User wants highest-rated spots
        - "tier": User wants premium/elite spots
        - "timeOfDay": Default contextual recommendation

        Be concise in reasons. Focus on what makes each spot good for this specific request.
        """
    }

    private func buildUserPrompt(from request: AIRecommendationRequest, candidates: [SpotSummary]) -> String {
        let hour = Calendar.current.component(.hour, from: request.time)
        let timeOfDay = hour < 12 ? "morning" : (hour < 17 ? "afternoon" : (hour < 21 ? "evening" : "night"))

        let spotsJSON = candidates.map { spot in
            """
            {"id":"\(spot.id)","name":"\(spot.name)","neighborhood":"\(spot.neighborhood)","tier":"\(spot.tier.rawValue)","type":"\(spot.placeType.rawValue)","attrs":[\(spot.attributes.map { "\"\($0.shortName)\"" }.joined(separator: ","))],\(spot.distanceMeters.map { "\"dist\":\(Int($0))" } ?? "\"dist\":null"),"notes":"\(spot.criticalFieldNotes.prefix(50))"}
            """
        }.joined(separator: ",\n")

        return """
        User query: "\(request.userMessage)"
        Time: \(timeOfDay) (\(hour):00)
        Active filters: \(request.activeFilters?.summaryDescription() ?? "none")

        Available spots:
        [\(spotsJSON)]

        Respond with JSON only.
        """
    }

    // MARK: - Helpers

    private func extractJSON(from content: String) -> String {
        // Handle markdown code blocks
        if content.contains("```json") {
            let start = content.range(of: "```json")?.upperBound ?? content.startIndex
            let end = content.range(of: "```", range: start..<content.endIndex)?.lowerBound ?? content.endIndex
            return String(content[start..<end]).trimmingCharacters(in: .whitespacesAndNewlines)
        }
        if content.contains("```") {
            let start = content.range(of: "```")?.upperBound ?? content.startIndex
            let end = content.range(of: "```", range: start..<content.endIndex)?.lowerBound ?? content.endIndex
            return String(content[start..<end]).trimmingCharacters(in: .whitespacesAndNewlines)
        }
        return content.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private func generateCacheKey(for request: AIRecommendationRequest) -> String {
        let hour = Calendar.current.component(.hour, from: request.time)
        let spotIDs = request.candidateSpots.prefix(5).map { $0.id }.joined(separator: ",")
        return "\(request.userMessage.lowercased().prefix(50))|\(hour)|\(spotIDs)"
    }
}

// MARK: - Response Cache

private class ResponseCache {
    private var cache: [String: (response: AIRecommendationResponse, timestamp: Date)] = [:]
    private let ttl: TimeInterval
    private let lock = NSLock()

    init(ttl: TimeInterval) {
        self.ttl = ttl
    }

    func get(for key: String) -> AIRecommendationResponse? {
        lock.lock()
        defer { lock.unlock() }

        guard let entry = cache[key] else { return nil }
        guard Date().timeIntervalSince(entry.timestamp) < ttl else {
            cache.removeValue(forKey: key)
            return nil
        }
        return entry.response
    }

    func set(_ response: AIRecommendationResponse, for key: String) {
        lock.lock()
        defer { lock.unlock() }

        cache[key] = (response, Date())

        // Limit cache size
        if cache.count > 50 {
            let sortedKeys = cache.sorted { $0.value.timestamp < $1.value.timestamp }
            for (key, _) in sortedKeys.prefix(25) {
                cache.removeValue(forKey: key)
            }
        }
    }

    func clear() {
        lock.lock()
        defer { lock.unlock() }
        cache.removeAll()
    }
}

// MARK: - API Models

private struct OpenAIChatPayload: Codable {
    let model: String
    let messages: [OpenAIMessage]
    let temperature: Double?
    let responseFormat: ResponseFormat?

    enum CodingKeys: String, CodingKey {
        case model, messages, temperature
        case responseFormat = "response_format"
    }
}

private struct ResponseFormat: Codable {
    let type: String
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
