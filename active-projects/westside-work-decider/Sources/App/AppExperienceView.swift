import SwiftUI
import CoreLocation

struct AppExperienceView: View {
    @StateObject private var appModel: AppModel
    @StateObject private var filters = QueryModel()
    @State private var selectedTab: Tab = .now
    @State private var currentError: DisplayableError?
    @State private var showNeighborhoodPicker = false
    @State private var selectedNeighborhood: String?
    @State private var showCityPicker = false

    // Momentum preservation: restore selections on relaunch
    @SceneStorage("selectedTab") private var storedTab: String = "now"
    @SceneStorage("lastQueryJSON") private var lastQueryJSON: String = ""
    @SceneStorage("selectedCityID") private var storedCityID: String = City.default.id

    private let aiService: AIRecommendationService = OpenAIService.makeDefault()

    init() {
        // Restore city from storage or use default
        let cityID = UserDefaults.standard.string(forKey: "selectedCityID") ?? City.default.id
        let city = City.find(byID: cityID) ?? .default
        _appModel = StateObject(wrappedValue: AppModel(city: city))
    }

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
                // City picker in leading position
                ToolbarItem(placement: .topBarLeading) {
                    cityPickerMenu
                }

                // Offline indicator in trailing position
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
        .onChange(of: appModel.currentCity) { _, newCity in
            storedCityID = newCity.id
            UserDefaults.standard.set(newCity.id, forKey: "selectedCityID")
            // Clear neighborhood filter when city changes
            selectedNeighborhood = nil
            filters.query.neighborhoods = []
        }
        .errorToast($currentError)
        .sheet(isPresented: $showNeighborhoodPicker) {
            NeighborhoodPicker(
                neighborhoods: appModel.store.allNeighborhoods,
                selected: $selectedNeighborhood,
                onDismiss: { showNeighborhoodPicker = false }
            )
        }
        .sheet(isPresented: $showCityPicker) {
            CityPickerSheet(
                currentCity: appModel.currentCity,
                onSelect: { city in
                    Task { await appModel.switchCity(city) }
                    showCityPicker = false
                },
                onDismiss: { showCityPicker = false }
            )
        }
        .onChange(of: selectedNeighborhood) { _, newValue in
            if let neighborhood = newValue {
                filters.query.neighborhoods = [neighborhood]
            }
        }
    }

    // MARK: - City Picker Menu

    private var cityPickerMenu: some View {
        Menu {
            // Current city section
            Section {
                Label(appModel.currentCity.name, systemImage: "checkmark")
                    .labelStyle(.titleAndIcon)
            } header: {
                Text("Current City")
            }

            Divider()

            // Quick switch to cities with data
            Section {
                ForEach(City.citiesWithData.filter { $0.id != appModel.currentCity.id }) { city in
                    Button {
                        Task { await appModel.switchCity(city) }
                    } label: {
                        Label(city.name, systemImage: "building.2")
                    }
                }
            } header: {
                Text("Switch City")
            }

            Divider()

            // Full city picker
            Button {
                showCityPicker = true
            } label: {
                Label("All Cities...", systemImage: "globe")
            }
        } label: {
            HStack(spacing: 4) {
                Image(systemName: "building.2")
                Text(appModel.currentCity.name)
                    .font(.subheadline)
                    .fontWeight(.medium)
                Image(systemName: "chevron.down")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(
                Capsule()
                    .fill(Color.blue.opacity(0.1))
            )
        }
        .accessibilityLabel("Select city, currently \(appModel.currentCity.name)")
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

// MARK: - City Picker Sheet

struct CityPickerSheet: View {
    let currentCity: City
    let onSelect: (City) -> Void
    let onDismiss: () -> Void

    var body: some View {
        NavigationStack {
            List {
                ForEach(CityGroup.all) { group in
                    Section(group.name) {
                        ForEach(group.cities) { city in
                            CityRow(
                                city: city,
                                isSelected: city.id == currentCity.id,
                                onSelect: {
                                    if city.hasData {
                                        onSelect(city)
                                    }
                                }
                            )
                        }
                    }
                }
            }
            .navigationTitle("Select City")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") {
                        onDismiss()
                    }
                }
            }
        }
    }
}

// MARK: - City Row

struct CityRow: View {
    let city: City
    let isSelected: Bool
    let onSelect: () -> Void

    var body: some View {
        Button(action: onSelect) {
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text(city.name)
                        .font(.body)
                        .foregroundStyle(city.hasData ? .primary : .secondary)

                    Text(city.spotCountLabel)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                Spacer()

                if isSelected {
                    Image(systemName: "checkmark")
                        .foregroundStyle(.blue)
                        .fontWeight(.semibold)
                } else if !city.hasData {
                    Text("Coming Soon")
                        .font(.caption)
                        .foregroundStyle(.tertiary)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(
                            Capsule()
                                .fill(Color.gray.opacity(0.1))
                        )
                }
            }
        }
        .disabled(!city.hasData && !isSelected)
        .accessibilityLabel("\(city.name), \(city.spotCountLabel)")
        .accessibilityHint(city.hasData ? "Tap to select" : "Coming soon")
    }
}

// MARK: - Preview

#Preview {
    AppExperienceView()
}
