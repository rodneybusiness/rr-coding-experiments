import SwiftUI
import CoreLocation

struct AppExperienceView: View {
    @StateObject private var appModel = AppModel(loader: CompositeSpotLoader())
    @StateObject private var filters = QueryModel()
    @State private var selectedTab: Tab = .now
    @State private var currentError: DisplayableError?
    @State private var showNeighborhoodPicker = false
    @State private var selectedNeighborhood: String?

    // Momentum preservation: restore tab selection on relaunch
    @SceneStorage("selectedTab") private var storedTab: String = "now"
    @SceneStorage("lastQueryJSON") private var lastQueryJSON: String = ""

    private let aiService: AIRecommendationService = OpenAIService.makeDefault()

    var body: some View {
        NavigationStack {
            ZStack {
                mainContent
                    .opacity(showsMainContent ? 1 : 0)

                // Loading overlay
                if appModel.store.loadingState.isLoading {
                    LoadingIndicator()
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                        .background(.ultraThinMaterial)
                }

                // Error state
                if let error = appModel.store.loadingState.error {
                    ErrorStateView(error: error) {
                        Task { await appModel.store.reload() }
                    }
                }

                // Location permission view
                if shouldShowLocationPermission {
                    LocationPermissionView(
                        status: appModel.locationProvider.authorizationStatus,
                        onRequestPermission: { appModel.requestLocation() },
                        onSelectNeighborhood: { showNeighborhoodPicker = true }
                    )
                }
            }
            .navigationTitle(navigationTitle(for: selectedTab))
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    if appModel.store.isUsingCachedData {
                        OfflineIndicator(isUsingCachedData: true)
                    }
                }
            }
        }
        .onAppear {
            appModel.requestLocation()
            restoreState()
        }
        .onChange(of: selectedTab) { _, newValue in
            storedTab = newValue.rawValue
        }
        .onChange(of: filters.query) { _, newValue in
            saveQueryState(newValue)
        }
        .errorToast($currentError)
        .sheet(isPresented: $showNeighborhoodPicker) {
            NeighborhoodPicker(
                neighborhoods: appModel.store.allNeighborhoods,
                selected: $selectedNeighborhood,
                onDismiss: { showNeighborhoodPicker = false }
            )
        }
        .onChange(of: selectedNeighborhood) { _, newValue in
            if let neighborhood = newValue {
                filters.query.neighborhoods = [neighborhood]
            }
        }
    }

    // MARK: - Main Content

    private var mainContent: some View {
        TabView(selection: $selectedTab) {
            NowView(
                store: appModel.store,
                filters: filters,
                onShowMap: { selectedTab = .map },
                onShowList: { selectedTab = .list }
            )
            .tabItem {
                Label("Now", systemImage: "sparkles")
            }
            .tag(Tab.now)

            SpotsMapView(store: appModel.store, filters: filters)
                .tabItem {
                    Label("Map", systemImage: "map")
                }
                .tag(Tab.map)

            SpotListView(store: appModel.store, filters: filters)
                .tabItem {
                    Label("List", systemImage: "list.bullet")
                }
                .tag(Tab.list)

            ChatView(
                store: appModel.store,
                filters: filters,
                ai: aiService,
                onJumpToResults: { selectedTab = .list },
                onJumpToMap: { selectedTab = .map }
            )
            .tabItem {
                Label("Chat", systemImage: "bubble.left.and.bubble.right")
            }
            .tag(Tab.chat)
        }
    }

    // MARK: - State Management

    private var showsMainContent: Bool {
        appModel.store.loadingState.hasLoaded && !shouldShowLocationPermission
    }

    private var shouldShowLocationPermission: Bool {
        let status = appModel.locationProvider.authorizationStatus
        return status == .denied || status == .restricted
    }

    private func restoreState() {
        // Restore tab selection
        if let tab = Tab(rawValue: storedTab) {
            selectedTab = tab
        }

        // Restore query filters
        if !lastQueryJSON.isEmpty,
           let data = lastQueryJSON.data(using: .utf8),
           let query = try? JSONDecoder().decode(SpotQuery.self, from: data) {
            filters.query = query
        }
    }

    private func saveQueryState(_ query: SpotQuery) {
        if let data = try? JSONEncoder().encode(query),
           let json = String(data: data, encoding: .utf8) {
            lastQueryJSON = json
        }
    }

    // MARK: - Helpers

    private func navigationTitle(for tab: Tab) -> String {
        switch tab {
        case .now: return "Now"
        case .map: return "Map"
        case .list: return "All Spots"
        case .chat: return "Chat"
        }
    }

    // MARK: - Tab Enum

    enum Tab: String, Hashable {
        case now
        case map
        case list
        case chat
    }
}

// MARK: - Preview

#Preview {
    AppExperienceView()
}
