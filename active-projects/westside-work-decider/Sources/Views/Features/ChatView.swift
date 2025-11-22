import SwiftUI

struct ChatView: View {
    @ObservedObject var store: SpotStore
    @ObservedObject var filters: QueryModel
    var ai: AIRecommendationService
    var onJumpToResults: () -> Void = {}
    var onJumpToMap: () -> Void = {}
    @State private var messages: [ChatEntry] = []
    @State private var input: String = ""

    var body: some View {
        VStack(spacing: 0) {
            ActiveFiltersSummary(query: filters.query, sort: filters.sort)
                .padding(.horizontal)
            Divider()
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 12) {
                        ForEach(messages) { message in
                            switch message.role {
                            case .user:
                                HStack {
                                    Spacer()
                                    bubble(text: message.text, isUser: true)
                                }
                            case .assistant:
                                assistantView(for: message)
                            }
                        }
                    }
                    .padding()
                    .onChange(of: messages.count) { _ in
                        if let last = messages.last { proxy.scrollTo(last.id, anchor: .bottom) }
                    }
                }
            }

            Divider()
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
        let userEntry = ChatEntry(role: .user, text: text)
        messages.append(userEntry)
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
                let appliedQuery = await MainActor.run { filters.query }
                let appliedSort = await MainActor.run { response.sort ?? filters.sort }
                let decorated = store.apply(query: appliedQuery, sort: appliedSort)
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
                let explanation = summary.isEmpty ? "Showing updated matches." : summary

                let entry = ChatEntry(
                    role: .assistant,
                    text: explanation,
                    recommendations: prioritized,
                    reasons: reasonLookup,
                    appliedFilters: appliedQuery,
                    appliedSort: appliedSort
                )
                await MainActor.run {
                    messages.append(entry)
                }
            } catch {
                await MainActor.run {
                    messages.append(ChatEntry(role: .assistant, text: "Sorry, something went wrong."))
                }
            }
        }
    }

    @ViewBuilder
    private func assistantView(for entry: ChatEntry) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            bubble(text: entry.text, isUser: false)
            if let filters = entry.appliedFilters {
                Label(filters.summaryDescription() ?? "No filters applied", systemImage: "checkmark.circle")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            if let sort = entry.appliedSort {
                Text("Sort: \(sort.displayName)")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
            }
            if !entry.recommendations.isEmpty {
                VStack(alignment: .leading, spacing: 12) {
                    ForEach(entry.recommendations, id: \.id) { spot in
                        SpotCard(
                            spot: spot,
                            distanceText: formattedDistance(for: spot),
                            frictionBadge: frictionBadge(for: spot),
                            isFavorite: spot.isFavorite,
                            onFavorite: { store.toggleFavorite(for: spot) },
                            onTap: { store.markVisited(spot) }
                        )
                        if let reason = entry.reasons[spot.id] {
                            Text(reason)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                    HStack {
                        Button {
                            onJumpToResults()
                        } label: {
                            Label("Open in list", systemImage: "list.bullet")
                        }
                        .buttonStyle(.bordered)

                        Button {
                            onJumpToMap()
                        } label: {
                            Label("Show on map", systemImage: "map")
                        }
                        .buttonStyle(.bordered)
                    }
                }
            }
        }
        .id(entry.id)
    }

    private func bubble(text: String, isUser: Bool) -> some View {
        Text(text)
            .padding(12)
            .frame(maxWidth: .infinity, alignment: isUser ? .trailing : .leading)
            .background(RoundedRectangle(cornerRadius: 12).fill(isUser ? Color.blue.opacity(0.15) : Color.gray.opacity(0.12)))
    }

    private func formattedDistance(for spot: LocationSpot) -> String? {
        guard let distance = spot.distance(from: store.anchorLocation(for: filters.query)) else { return nil }
        let miles = distance / 1609.34
        return String(format: "%.1f mi", miles)
    }

    private func frictionBadge(for spot: LocationSpot) -> String? {
        if spot.chargedLaptopBrickOnly { return "Charge before you go" }
        if !spot.attributes.contains(.easyParking) && !spot.walkingFriendlyLocation { return "Parking may be tricky" }
        return nil
    }
}

private struct ChatEntry: Identifiable {
    let id = UUID()
    let role: Role
    let text: String
    var recommendations: [LocationSpot] = []
    var reasons: [String: String] = [:]
    var appliedFilters: SpotQuery? = nil
    var appliedSort: SpotSort? = nil

    enum Role { case user, assistant }
}
