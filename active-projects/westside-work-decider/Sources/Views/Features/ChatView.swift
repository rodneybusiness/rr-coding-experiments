import SwiftUI

struct ChatView: View {
    @ObservedObject var store: SpotStore
    @ObservedObject var filters: QueryModel
    var ai: AIRecommendationService
    var onJumpToResults: () -> Void = {}
    var onJumpToMap: () -> Void = {}

    @State private var messages: [ChatEntry] = []
    @State private var input: String = ""
    @State private var isProcessing: Bool = false
    @State private var currentError: DisplayableError?

    var body: some View {
        VStack(spacing: 0) {
            // Active filters summary
            ActiveFiltersSummary(query: filters.query, sort: filters.sort)
                .padding(.horizontal)

            Divider()

            // Chat messages
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 12) {
                        // Welcome message if empty
                        if messages.isEmpty {
                            welcomeMessage
                        }

                        ForEach(messages) { message in
                            messageView(for: message)
                        }

                        // Typing indicator
                        if isProcessing {
                            typingIndicator
                        }
                    }
                    .padding()
                    .onChange(of: messages.count) { _, _ in
                        if let last = messages.last {
                            withAnimation {
                                proxy.scrollTo(last.id, anchor: .bottom)
                            }
                        }
                    }
                }
            }

            Divider()

            // Input field
            inputBar
        }
        .errorToast($currentError)
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Chat with AI assistant")
    }

    // MARK: - Subviews

    private var welcomeMessage: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Hi! I can help you find the perfect work spot.")
                .font(.headline)

            Text("Try asking things like:")
                .font(.subheadline)
                .foregroundStyle(.secondary)

            VStack(alignment: .leading, spacing: 8) {
                suggestionButton("I need a quiet place with good wifi")
                suggestionButton("Where can I work late tonight?")
                suggestionButton("Find a coffee shop with outlets nearby")
                suggestionButton("I want somewhere with good food for lunch")
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.blue.opacity(0.08))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Welcome message with suggestions")
    }

    private func suggestionButton(_ text: String) -> some View {
        Button {
            input = text
            send()
        } label: {
            HStack {
                Image(systemName: "sparkles")
                    .foregroundStyle(.blue)
                Text(text)
                    .font(.subheadline)
                    .foregroundStyle(.primary)
                    .multilineTextAlignment(.leading)
            }
            .padding(.vertical, 6)
        }
        .buttonStyle(.plain)
        .accessibilityLabel("Suggestion: \(text)")
    }

    @ViewBuilder
    private func messageView(for entry: ChatEntry) -> some View {
        switch entry.role {
        case .user:
            HStack {
                Spacer()
                bubble(text: entry.text, isUser: true)
            }
            .accessibilityLabel("You said: \(entry.text)")

        case .assistant:
            assistantView(for: entry)
        }
    }

    @ViewBuilder
    private func assistantView(for entry: ChatEntry) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            bubble(text: entry.text, isUser: false)

            // Applied filters
            if let appliedFilters = entry.appliedFilters,
               let summary = appliedFilters.summaryDescription() {
                Label(summary, systemImage: "checkmark.circle")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            // Sort info
            if let sort = entry.appliedSort {
                Text("Sorted by: \(sort.displayName)")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
            }

            // Recommendations
            if !entry.recommendations.isEmpty {
                VStack(alignment: .leading, spacing: 12) {
                    ForEach(entry.recommendations, id: \.id) { spot in
                        let anchor = store.anchorLocation(for: filters.query)
                        SpotCard(
                            spot: spot,
                            distanceMeters: spot.distance(from: anchor),
                            showNavigateButton: true,
                            isFavorite: spot.isFavorite,
                            onFavorite: { store.toggleFavorite(for: spot) },
                            onTap: { store.markVisited(spot) }
                        )

                        if let reason = entry.reasons[spot.id] {
                            Text(reason)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                                .padding(.leading, 8)
                        }
                    }

                    // Action buttons
                    HStack {
                        Button {
                            onJumpToResults()
                        } label: {
                            Label("Open in List", systemImage: "list.bullet")
                        }
                        .buttonStyle(.bordered)

                        Button {
                            onJumpToMap()
                        } label: {
                            Label("Show on Map", systemImage: "map")
                        }
                        .buttonStyle(.bordered)
                    }

                    // Feedback
                    FeedbackView(
                        spotName: entry.recommendations.first?.name ?? "recommendation"
                    ) { feedbackType in
                        handleFeedback(feedbackType, for: entry)
                    }
                }
            }
        }
        .id(entry.id)
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Assistant response")
    }

    private var typingIndicator: some View {
        HStack(spacing: 4) {
            ForEach(0..<3) { index in
                Circle()
                    .fill(Color.gray)
                    .frame(width: 8, height: 8)
                    .opacity(0.6)
            }
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.gray.opacity(0.12))
        )
        .accessibilityLabel("Assistant is typing")
    }

    private func bubble(text: String, isUser: Bool) -> some View {
        Text(text)
            .padding(12)
            .frame(maxWidth: isUser ? nil : .infinity, alignment: isUser ? .trailing : .leading)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(isUser ? Color.blue.opacity(0.15) : Color.gray.opacity(0.12))
            )
    }

    private var inputBar: some View {
        HStack(spacing: 12) {
            TextField("Ask for a spot...", text: $input)
                .textFieldStyle(.roundedBorder)
                .disabled(isProcessing)
                .onSubmit { send() }
                .accessibilityLabel("Message input")

            Button(action: send) {
                Image(systemName: "arrow.up.circle.fill")
                    .font(.title2)
                    .foregroundStyle(canSend ? .blue : .gray)
            }
            .disabled(!canSend)
            .accessibilityLabel("Send message")
        }
        .padding()
    }

    // MARK: - Actions

    private var canSend: Bool {
        !input.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && !isProcessing
    }

    private func send() {
        let text = input.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }

        let userEntry = ChatEntry(role: .user, text: text)
        messages.append(userEntry)
        input = ""
        isProcessing = true

        Task {
            await processMessage(text)
        }
    }

    private func processMessage(_ text: String) async {
        let anchor = store.anchorLocation(for: filters.query)
        let prioritized = store.apply(query: filters.query, sort: .distance)

        let summaries = prioritized.prefix(40).map { spot in
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

        let request = AIRecommendationRequest(
            userMessage: text,
            time: Date(),
            coordinate: anchor?.coordinate,
            activeFilters: filters.query,
            candidateSpots: Array(summaries.prefix(20))
        )

        do {
            let response = try await ai.recommend(request: request)

            await MainActor.run {
                filters.apply(aiResponse: response)
            }

            let appliedQuery = await MainActor.run { filters.query }
            let appliedSort = await MainActor.run { response.sort ?? filters.sort }
            let decorated = store.apply(query: appliedQuery, sort: appliedSort)

            let reasonLookup = Dictionary(
                uniqueKeysWithValues: response.recommendations.map { ($0.id, $0.reason) }
            )

            let prioritizedResults: [LocationSpot]
            if response.recommendations.isEmpty {
                prioritizedResults = Array(decorated.prefix(5))
            } else {
                let matches = response.recommendations.compactMap { rec in
                    decorated.first(where: { $0.id == rec.id })
                }
                prioritizedResults = matches.isEmpty ? Array(decorated.prefix(5)) : matches
            }

            let summary = prioritizedResults.map { spot in
                "• \(spot.name) — \(reasonLookup[spot.id] ?? spot.criticalFieldNotes)"
            }.joined(separator: "\n")

            let explanation = summary.isEmpty ? "Showing updated matches." : summary

            let entry = ChatEntry(
                role: .assistant,
                text: explanation,
                recommendations: prioritizedResults,
                reasons: reasonLookup,
                appliedFilters: appliedQuery,
                appliedSort: appliedSort
            )

            await MainActor.run {
                messages.append(entry)
                isProcessing = false
            }

        } catch {
            await MainActor.run {
                let errorMessage: String
                if let aiError = error as? AIServiceError {
                    errorMessage = aiError.errorDescription ?? "Something went wrong."
                } else {
                    errorMessage = "Sorry, I couldn't process your request. Please try again."
                }

                messages.append(ChatEntry(role: .assistant, text: errorMessage))
                isProcessing = false

                currentError = DisplayableError(from: error)
            }
        }
    }

    private func handleFeedback(_ type: FeedbackView.FeedbackType, for entry: ChatEntry) {
        // Log feedback for analytics/improvement
        let feedbackData: [String: Any] = [
            "type": type == .helpful ? "positive" : "negative",
            "messageId": entry.id.uuidString,
            "recommendations": entry.recommendations.map { $0.id },
            "timestamp": Date()
        ]

        // In a real app, send to analytics service
        print("Feedback received: \(feedbackData)")

        // If not helpful, could adjust future recommendations
        if type == .notHelpful {
            // Track spots marked as not helpful for this query type
            // This could inform future AI prompts
        }
    }
}

// MARK: - Chat Entry Model

private struct ChatEntry: Identifiable {
    let id = UUID()
    let role: Role
    let text: String
    var recommendations: [LocationSpot] = []
    var reasons: [String: String] = [:]
    var appliedFilters: SpotQuery? = nil
    var appliedSort: SpotSort? = nil

    enum Role {
        case user
        case assistant
    }
}

// MARK: - Preview

#Preview {
    ChatView(
        store: SpotStore(spots: []),
        filters: QueryModel(),
        ai: SimulatedAIService()
    )
}
