import SwiftUI

struct AppExperienceView: View {
    @StateObject private var appModel = AppModel(loader: CompositeSpotLoader())
    @StateObject private var filters = QueryModel()
    @State private var selectedTab: Tab = .now
    private let aiService: AIRecommendationService = OpenAIService.makeDefault()

    var body: some View {
        NavigationStack {
            TabView(selection: $selectedTab) {
                NowView(store: appModel.store, filters: filters, onShowMap: { selectedTab = .map }, onShowList: { selectedTab = .list })
                    .tabItem { Label("Now", systemImage: "sparkles") }
                    .tag(Tab.now)

                SpotsMapView(store: appModel.store, filters: filters)
                    .tabItem { Label("Map", systemImage: "map") }
                    .tag(Tab.map)

                SpotListView(store: appModel.store, filters: filters)
                    .tabItem { Label("List", systemImage: "list.bullet") }
                    .tag(Tab.list)

                ChatView(
                    store: appModel.store,
                    filters: filters,
                    ai: aiService,
                    onJumpToResults: { selectedTab = .list },
                    onJumpToMap: { selectedTab = .map }
                )
                    .tabItem { Label("Chat", systemImage: "bubble.left.and.bubble.right") }
                    .tag(Tab.chat)
            }
            .navigationTitle(navigationTitle(for: selectedTab))
        }
        .onAppear { appModel.requestLocation() }
    }

    private func navigationTitle(for tab: Tab) -> String {
        switch tab {
        case .now: return "Now"
        case .map: return "Map"
        case .list: return "All spots"
        case .chat: return "Chat"
        }
    }

    private enum Tab: Hashable { case now, map, list, chat }
}

#Preview {
    AppExperienceView()
}
