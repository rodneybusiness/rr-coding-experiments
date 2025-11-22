import SwiftUI

struct ChatView: View {
    @ObservedObject var store: SpotStore
    var ai: AIRecommendationService
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
            let summaries = store.spots.map { spot in
                SpotSummary(
                    id: spot.id,
                    name: spot.name,
                    neighborhood: spot.neighborhood,
                    tier: spot.tier,
                    placeType: spot.placeType,
                    attributes: spot.attributes,
                    criticalFieldNotes: spot.criticalFieldNotes,
                    distanceMeters: spot.distance(from: store.location)
                )
            }
            let request = AIRecommendationRequest(
                userMessage: text,
                time: Date(),
                coordinate: store.location?.coordinate,
                activeFilters: nil,
                candidateSpots: summaries
            )
            do {
                let response = try await ai.recommend(request: request)
                let names = response.recommendations.compactMap { id in
                    summaries.first(where: { $0.id == id.id })?.name ?? ""
                }
                let reasoned = names.isEmpty ? "No match" : names.joined(separator: ", ")
                let explanation = "Suggested: \(reasoned). Filters: \(response.filters?.attributes.map { $0.rawValue }.joined(separator: ", ") ?? "none")"
                await MainActor.run {
                    messages.append(.init(text: explanation, isUser: false))
                }
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
