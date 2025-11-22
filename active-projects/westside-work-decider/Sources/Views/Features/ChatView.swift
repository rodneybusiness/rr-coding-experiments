import SwiftUI

struct ChatView: View {
    @ObservedObject var store: SpotStore
    @ObservedObject var filters: QueryModel
    var ai: AIRecommendationService
    var onJumpToResults: () -> Void = {}
    @State private var messages: [Message] = []
    @State private var input: String = ""

    var body: some View {
        VStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    ForEach(messages) { message in
                        HStack {
                            if message.isUser {
                                Spacer()
                                bubble(text: message.text, isUser: true)
                            } else {
                                bubble(text: message.text, isUser: false)
                                Spacer()
                            }
                        }
                    }
                }
                .padding()
            }

            HStack {
                TextField("Ask for a spot…", text: $input)
                    .textFieldStyle(.roundedBorder)
                Button("Send") { send() }
                    .buttonStyle(.borderedProminent)
            }
            .padding()
        }
    }

    private func send() {
        let text = input.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        messages.append(.init(text: text, isUser: true))
        input = ""

        Task {
            let anchor = store.anchorLocation(for: filters.query)
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
            let request = AIRecommendationRequest(
                userMessage: text,
                time: Date(),
                coordinate: anchor?.coordinate,
                activeFilters: filters.query,
                candidateSpots: Array(summaries.prefix(20))
            )
            do {
                let response = try await ai.recommend(request: request)
                await MainActor.run { filters.apply(aiResponse: response) }
                let decorated = store.apply(query: filters.query, sort: response.sort ?? filters.sort)
                let reasonLookup = Dictionary(uniqueKeysWithValues: response.recommendations.map { ($0.id, $0.reason) })
                let prioritized: [LocationSpot]
                if response.recommendations.isEmpty {
                    prioritized = Array(decorated.prefix(3))
                } else {
                    let matches = response.recommendations.compactMap { rec in decorated.first(where: { $0.id == rec.id }) }
                    prioritized = matches.isEmpty ? Array(decorated.prefix(3)) : matches
                }

                let summary = prioritized.map { spot in
                    "• \(spot.name) — \(reasonLookup[spot.id] ?? spot.criticalFieldNotes)"
                }.joined(separator: "\n")
                let filterCopy = response.filters?.attributes.map { $0.rawValue }.joined(separator: ", ") ?? "none"
                let explanation = "Recommended (filters: \(filterCopy)):\n\(summary)"
                await MainActor.run {
                    messages.append(.init(text: explanation, isUser: false))
                }
                onJumpToResults()
            } catch {
                await MainActor.run {
                    messages.append(.init(text: "Sorry, something went wrong.", isUser: false))
                }
            }
        }
    }

    private func bubble(text: String, isUser: Bool) -> some View {
        Text(text)
            .padding(12)
            .background(RoundedRectangle(cornerRadius: 12).fill(isUser ? Color.blue.opacity(0.15) : Color.gray.opacity(0.12)))
    }
}

private struct Message: Identifiable {
    let id = UUID()
    let text: String
    let isUser: Bool
}
