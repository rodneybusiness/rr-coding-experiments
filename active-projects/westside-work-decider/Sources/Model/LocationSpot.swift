import Foundation
import CoreLocation

// MARK: - Tier

enum Tier: String, Codable, CaseIterable, Identifiable, Hashable {
    case elite = "Elite"
    case reliable = "Reliable"
    case unknown

    var id: String { rawValue }

    var displayColor: String {
        switch self {
        case .elite: return "gold"
        case .reliable: return "blue"
        case .unknown: return "gray"
        }
    }

    var description: String {
        switch self {
        case .elite: return "Top-tier, exceptional experience"
        case .reliable: return "Solid choice, consistently good"
        case .unknown: return "Not yet rated"
        }
    }
}

// MARK: - PlaceType

enum PlaceType: String, Codable, CaseIterable, Identifiable, Hashable {
    case club = "Club"
    case coworking = "Coworking Space"
    case hotelLobby = "Hotel Lobby"
    case cafe = "Cafe"
    case cafeRestaurant = "Cafe/Restaurant"
    case bookstoreCafe = "Bookstore Cafe"
    case bankCafe = "Bank Cafe"
    case library = "Library"
    case unknown

    var id: String { rawValue }

    var icon: String {
        switch self {
        case .club: return "building.columns.fill"
        case .coworking: return "desktopcomputer"
        case .hotelLobby: return "bed.double.fill"
        case .cafe: return "cup.and.saucer.fill"
        case .cafeRestaurant: return "fork.knife"
        case .bookstoreCafe: return "books.vertical.fill"
        case .bankCafe: return "building.2.fill"
        case .library: return "book.fill"
        case .unknown: return "mappin"
        }
    }

    var shortName: String {
        switch self {
        case .club: return "Club"
        case .coworking: return "Coworking"
        case .hotelLobby: return "Hotel"
        case .cafe: return "Cafe"
        case .cafeRestaurant: return "Restaurant"
        case .bookstoreCafe: return "Bookstore"
        case .bankCafe: return "Bank Cafe"
        case .library: return "Library"
        case .unknown: return "Other"
        }
    }
}

// MARK: - AttributeTag

enum AttributeTag: String, Codable, CaseIterable, Identifiable, Hashable {
    case powerHeavy = "⚡️ Power Heavy"
    case easyParking = "🚗 Easy Parking"
    case ergonomic = "🪑 Ergonomic"
    case bodyDoubling = "🗣️ Body Doubling"
    case deepFocus = "🧘 Deep Focus"
    case realFood = "🍽️ Real Food"
    case callFriendly = "📞 Call Friendly"
    case patioPower = "🌤️ Patio Power"
    case dayPass = "🎟️ Day Pass"
    case earlyBird = "🌅 Early Bird"
    case nightOwl = "🌙 Night Owl"
    case luxury = "💎 Luxury"
    case eliteCoffee = "☕️ Elite Coffee"
    case unknown

    var id: String { rawValue }

    /// The emoji component of the attribute
    var emoji: String {
        let chars = rawValue.unicodeScalars
        var result = ""
        for scalar in chars {
            if scalar.properties.isEmoji && scalar.properties.isEmojiPresentation {
                result.append(Character(scalar))
            } else if scalar.value >= 0x1F000 {
                result.append(Character(scalar))
            }
        }
        return result.isEmpty ? "•" : result
    }

    /// The text component without emoji
    var displayText: String {
        rawValue.replacingOccurrences(of: emoji, with: "").trimmingCharacters(in: .whitespaces)
    }

    /// Short display name for compact UI
    var shortName: String {
        switch self {
        case .powerHeavy: return "Power"
        case .easyParking: return "Parking"
        case .ergonomic: return "Ergonomic"
        case .bodyDoubling: return "Social"
        case .deepFocus: return "Focus"
        case .realFood: return "Food"
        case .callFriendly: return "Calls OK"
        case .patioPower: return "Patio"
        case .dayPass: return "Day Pass"
        case .earlyBird: return "Early"
        case .nightOwl: return "Late"
        case .luxury: return "Luxury"
        case .eliteCoffee: return "Coffee"
        case .unknown: return "Other"
        }
    }

    /// Keywords that map to this attribute for AI parsing
    var keywords: [String] {
        switch self {
        case .powerHeavy: return ["power", "outlet", "charge", "plug", "electric"]
        case .easyParking: return ["parking", "park", "car", "drive", "lot"]
        case .ergonomic: return ["ergonomic", "comfortable", "chair", "desk"]
        case .bodyDoubling: return ["social", "body", "people", "company", "community", "cowork"]
        case .deepFocus: return ["focus", "quiet", "deep", "concentrate", "work", "study", "silent"]
        case .realFood: return ["food", "lunch", "meal", "eat", "hungry", "breakfast", "dinner"]
        case .callFriendly: return ["call", "phone", "meeting", "zoom", "video"]
        case .patioPower: return ["outdoor", "patio", "outside", "fresh", "air", "sun"]
        case .dayPass: return ["day pass", "drop-in", "single day", "visitor"]
        case .earlyBird: return ["early", "morning", "am", "breakfast", "dawn"]
        case .nightOwl: return ["late", "night", "evening", "pm", "after hours"]
        case .luxury: return ["luxury", "premium", "upscale", "fancy", "nice"]
        case .eliteCoffee: return ["coffee", "espresso", "latte", "cafe"]
        case .unknown: return []
        }
    }
}

// MARK: - Price Tier

enum PriceTier: String, Codable, CaseIterable, Identifiable, Hashable {
    case free = "Free"
    case low = "$"
    case medium = "$$"
    case high = "$$$"
    case premium = "$$$$"

    var id: String { rawValue }

    var displayName: String { rawValue }

    var description: String {
        switch self {
        case .free: return "No cost to work here"
        case .low: return "Under $10"
        case .medium: return "$10-25"
        case .high: return "$25-50"
        case .premium: return "$50+"
        }
    }
}

// MARK: - WiFi Quality

enum WiFiQuality: String, Codable, CaseIterable, Identifiable, Hashable {
    case fast = "Fast"
    case moderate = "Moderate"
    case slow = "Slow"
    case none = "None"

    var id: String { rawValue }

    var icon: String {
        switch self {
        case .fast: return "wifi"
        case .moderate: return "wifi"
        case .slow: return "wifi.exclamationmark"
        case .none: return "wifi.slash"
        }
    }
}

// MARK: - Noise Level

enum NoiseLevel: String, Codable, CaseIterable, Identifiable, Hashable {
    case silent = "Silent"
    case quiet = "Quiet"
    case moderate = "Moderate"
    case loud = "Loud"

    var id: String { rawValue }

    var icon: String {
        switch self {
        case .silent: return "speaker.slash.fill"
        case .quiet: return "speaker.fill"
        case .moderate: return "speaker.wave.1.fill"
        case .loud: return "speaker.wave.3.fill"
        }
    }
}

// MARK: - LocationSpot

struct LocationSpot: Identifiable, Codable, Equatable, Hashable {
    // MARK: - Core Properties

    let id: String
    let name: String
    let city: String
    let neighborhood: String
    let placeType: PlaceType
    let tier: Tier
    let sentimentScore: Double
    let costBasis: String
    let openLate: Bool
    let closeToHome: Bool
    let closeToWork: Bool
    let safeToLeaveComputer: Bool
    let walkingFriendlyLocation: Bool
    let exerciseWellnessAvailable: Bool
    let chargedLaptopBrickOnly: Bool
    let attributes: [AttributeTag]
    let criticalFieldNotes: String
    let status: String

    // MARK: - Location

    var latitude: Double?
    var longitude: Double?

    // MARK: - Enhanced Properties (optional, for future data)

    var priceTier: PriceTier?
    var wifiQuality: WiFiQuality?
    var noiseLevel: NoiseLevel?
    var operatingHours: OperatingHours?
    var websiteURL: String?
    var phoneNumber: String?
    var address: String?

    // MARK: - User State (not persisted in JSON, decorated at runtime)

    var isFavorite: Bool = false
    var userNotes: String? = nil
    var lastVisited: Date? = nil

    // MARK: - Coding Keys

    enum CodingKeys: String, CodingKey {
        case name = "Name"
        case city = "City"
        case neighborhood = "Neighborhood"
        case placeType = "PlaceType"
        case tier = "Tier"
        case sentimentScore = "SentimentScore"
        case costBasis = "CostBasis"
        case openLate = "OpenLate"
        case closeToHome = "CloseToHome"
        case closeToWork = "CloseToWork"
        case safeToLeaveComputer = "SafeToLeaveComputer"
        case walkingFriendlyLocation = "WalkingFriendlyLocation"
        case exerciseWellnessAvailable = "ExerciseWellnessAvailable"
        case chargedLaptopBrickOnly = "ChargedLaptopBrickOnly"
        case attributes = "Attributes"
        case criticalFieldNotes = "CriticalFieldNotes"
        case status = "Status"
        case latitude, longitude
        case priceTier = "PriceTier"
        case wifiQuality = "WiFiQuality"
        case noiseLevel = "NoiseLevel"
        case operatingHours = "OperatingHours"
        case websiteURL = "WebsiteURL"
        case phoneNumber = "PhoneNumber"
        case address = "Address"
    }

    // MARK: - Decoder

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)

        name = try container.decode(String.self, forKey: .name)
        city = try container.decode(String.self, forKey: .city)
        neighborhood = try container.decode(String.self, forKey: .neighborhood)
        placeType = PlaceType(rawValue: try container.decode(String.self, forKey: .placeType)) ?? .unknown
        tier = Tier(rawValue: try container.decode(String.self, forKey: .tier)) ?? .unknown
        sentimentScore = try container.decode(Double.self, forKey: .sentimentScore)
        costBasis = try container.decode(String.self, forKey: .costBasis)
        openLate = try container.decode(Bool.self, forKey: .openLate)
        closeToHome = try container.decode(Bool.self, forKey: .closeToHome)
        closeToWork = try container.decode(Bool.self, forKey: .closeToWork)
        safeToLeaveComputer = try container.decode(Bool.self, forKey: .safeToLeaveComputer)
        walkingFriendlyLocation = try container.decode(Bool.self, forKey: .walkingFriendlyLocation)
        exerciseWellnessAvailable = try container.decode(Bool.self, forKey: .exerciseWellnessAvailable)
        chargedLaptopBrickOnly = try container.decode(Bool.self, forKey: .chargedLaptopBrickOnly)

        let rawAttributes = try container.decode(String.self, forKey: .attributes)
        attributes = rawAttributes
            .split(separator: ",")
            .map { $0.trimmingCharacters(in: .whitespaces) }
            .compactMap { rawValue in
                AttributeTag(rawValue: rawValue) ?? .unknown
            }
            .filter { $0 != .unknown }

        criticalFieldNotes = try container.decode(String.self, forKey: .criticalFieldNotes)
        status = try container.decode(String.self, forKey: .status)
        latitude = try container.decodeIfPresent(Double.self, forKey: .latitude)
        longitude = try container.decodeIfPresent(Double.self, forKey: .longitude)

        // Enhanced properties (optional)
        if let priceString = try container.decodeIfPresent(String.self, forKey: .priceTier) {
            priceTier = PriceTier(rawValue: priceString)
        }
        if let wifiString = try container.decodeIfPresent(String.self, forKey: .wifiQuality) {
            wifiQuality = WiFiQuality(rawValue: wifiString)
        }
        if let noiseString = try container.decodeIfPresent(String.self, forKey: .noiseLevel) {
            noiseLevel = NoiseLevel(rawValue: noiseString)
        }
        operatingHours = try container.decodeIfPresent(OperatingHours.self, forKey: .operatingHours)
        websiteURL = try container.decodeIfPresent(String.self, forKey: .websiteURL)
        phoneNumber = try container.decodeIfPresent(String.self, forKey: .phoneNumber)
        address = try container.decodeIfPresent(String.self, forKey: .address)

        id = LocationSpot.makeID(name: name, neighborhood: neighborhood)
    }

    // MARK: - Manual Initializer

    init(
        name: String,
        city: String,
        neighborhood: String,
        placeType: PlaceType,
        tier: Tier,
        sentimentScore: Double,
        costBasis: String,
        openLate: Bool,
        closeToHome: Bool,
        closeToWork: Bool,
        safeToLeaveComputer: Bool,
        walkingFriendlyLocation: Bool,
        exerciseWellnessAvailable: Bool,
        chargedLaptopBrickOnly: Bool,
        attributes: [AttributeTag],
        criticalFieldNotes: String,
        status: String,
        isFavorite: Bool = false,
        userNotes: String? = nil,
        lastVisited: Date? = nil,
        latitude: Double? = nil,
        longitude: Double? = nil,
        priceTier: PriceTier? = nil,
        wifiQuality: WiFiQuality? = nil,
        noiseLevel: NoiseLevel? = nil,
        operatingHours: OperatingHours? = nil,
        websiteURL: String? = nil,
        phoneNumber: String? = nil,
        address: String? = nil
    ) {
        self.id = LocationSpot.makeID(name: name, neighborhood: neighborhood)
        self.name = name
        self.city = city
        self.neighborhood = neighborhood
        self.placeType = placeType
        self.tier = tier
        self.sentimentScore = sentimentScore
        self.costBasis = costBasis
        self.openLate = openLate
        self.closeToHome = closeToHome
        self.closeToWork = closeToWork
        self.safeToLeaveComputer = safeToLeaveComputer
        self.walkingFriendlyLocation = walkingFriendlyLocation
        self.exerciseWellnessAvailable = exerciseWellnessAvailable
        self.chargedLaptopBrickOnly = chargedLaptopBrickOnly
        self.attributes = attributes
        self.criticalFieldNotes = criticalFieldNotes
        self.status = status
        self.isFavorite = isFavorite
        self.userNotes = userNotes
        self.lastVisited = lastVisited
        self.latitude = latitude
        self.longitude = longitude
        self.priceTier = priceTier
        self.wifiQuality = wifiQuality
        self.noiseLevel = noiseLevel
        self.operatingHours = operatingHours
        self.websiteURL = websiteURL
        self.phoneNumber = phoneNumber
        self.address = address
    }

    // MARK: - Computed Properties

    var coordinate: CLLocationCoordinate2D? {
        guard let lat = latitude, let lon = longitude else { return nil }
        return CLLocationCoordinate2D(latitude: lat, longitude: lon)
    }

    var hasCoordinates: Bool {
        latitude != nil && longitude != nil
    }

    var attributeSet: Set<AttributeTag> {
        Set(attributes)
    }

    /// Primary friction warning for this spot
    var primaryFriction: String? {
        if chargedLaptopBrickOnly {
            return "Charge before you go"
        }
        if !attributes.contains(.easyParking) && !walkingFriendlyLocation {
            return "Parking may be tricky"
        }
        return nil
    }

    /// Check if spot is likely open now based on operating hours
    func isLikelyOpenNow(at date: Date = Date()) -> Bool? {
        guard let hours = operatingHours else { return nil }
        return hours.isOpen(at: date)
    }

    // MARK: - Distance

    func distance(from location: CLLocation?) -> CLLocationDistance? {
        guard let latitude, let longitude, let origin = location else { return nil }
        let dest = CLLocation(latitude: latitude, longitude: longitude)
        return origin.distance(from: dest)
    }

    // MARK: - Matching

    func matches(tagFilters: Set<AttributeTag>) -> Bool {
        guard !tagFilters.isEmpty else { return true }
        return tagFilters.isSubset(of: attributeSet)
    }

    func matchesAny(tagFilters: Set<AttributeTag>) -> Bool {
        guard !tagFilters.isEmpty else { return true }
        return !attributeSet.isDisjoint(with: tagFilters)
    }

    // MARK: - ID Generation

    static func makeID(name: String, neighborhood: String) -> String {
        let slug = "\(name.lowercased())-\(neighborhood.lowercased())"
            .replacingOccurrences(of: " ", with: "-")
            .replacingOccurrences(of: ",", with: "")
            .replacingOccurrences(of: "'", with: "")
            .replacingOccurrences(of: "\"", with: "")
        return slug
    }

    // MARK: - Hashable

    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }

    static func == (lhs: LocationSpot, rhs: LocationSpot) -> Bool {
        lhs.id == rhs.id
    }
}

// MARK: - Operating Hours

struct OperatingHours: Codable, Equatable, Hashable {
    var monday: DayHours?
    var tuesday: DayHours?
    var wednesday: DayHours?
    var thursday: DayHours?
    var friday: DayHours?
    var saturday: DayHours?
    var sunday: DayHours?

    func hours(for weekday: Int) -> DayHours? {
        switch weekday {
        case 1: return sunday
        case 2: return monday
        case 3: return tuesday
        case 4: return wednesday
        case 5: return thursday
        case 6: return friday
        case 7: return saturday
        default: return nil
        }
    }

    func isOpen(at date: Date, calendar: Calendar = .current) -> Bool {
        let weekday = calendar.component(.weekday, from: date)
        guard let dayHours = hours(for: weekday) else { return false }
        return dayHours.isOpen(at: date, calendar: calendar)
    }
}

struct DayHours: Codable, Equatable, Hashable {
    let open: String  // "09:00"
    let close: String // "22:00"

    func isOpen(at date: Date, calendar: Calendar = .current) -> Bool {
        let hour = calendar.component(.hour, from: date)
        let minute = calendar.component(.minute, from: date)
        let currentMinutes = hour * 60 + minute

        let openParts = open.split(separator: ":").compactMap { Int($0) }
        let closeParts = close.split(separator: ":").compactMap { Int($0) }

        guard openParts.count >= 2, closeParts.count >= 2 else { return false }

        let openMinutes = openParts[0] * 60 + openParts[1]
        let closeMinutes = closeParts[0] * 60 + closeParts[1]

        if closeMinutes < openMinutes {
            // Crosses midnight
            return currentMinutes >= openMinutes || currentMinutes < closeMinutes
        } else {
            return currentMinutes >= openMinutes && currentMinutes < closeMinutes
        }
    }
}

// MARK: - SpotQuery

struct SpotQuery: Codable, Hashable {
    // MARK: - Set Filters

    var tiers: Set<Tier> = []
    var neighborhoods: Set<String> = []
    var placeTypes: Set<PlaceType> = []
    var attributes: Set<AttributeTag> = []

    // MARK: - Boolean Filters

    var openLate: Bool? = nil
    var closeToHome: Bool? = nil
    var closeToWork: Bool? = nil
    var safeToLeaveComputer: Bool? = nil
    var walkingFriendlyLocation: Bool? = nil
    var exerciseWellnessAvailable: Bool? = nil
    var chargedLaptopBrickOnly: Bool? = nil

    // MARK: - Enhanced Filters

    var favoriteOnly: Bool? = nil
    var searchText: String? = nil
    var priceTiers: Set<PriceTier> = []
    var minSentiment: Double? = nil
    var maxDistance: Double? = nil  // in meters

    // MARK: - Computed

    var hasFilters: Bool {
        !tiers.isEmpty ||
        !neighborhoods.isEmpty ||
        !placeTypes.isEmpty ||
        !attributes.isEmpty ||
        !priceTiers.isEmpty ||
        openLate != nil ||
        closeToHome != nil ||
        closeToWork != nil ||
        safeToLeaveComputer != nil ||
        walkingFriendlyLocation != nil ||
        exerciseWellnessAvailable != nil ||
        chargedLaptopBrickOnly != nil ||
        favoriteOnly == true ||
        (searchText != nil && !searchText!.isEmpty) ||
        minSentiment != nil ||
        maxDistance != nil
    }

    var filterCount: Int {
        var count = 0
        count += tiers.count
        count += neighborhoods.count
        count += placeTypes.count
        count += attributes.count
        count += priceTiers.count
        if openLate != nil { count += 1 }
        if closeToHome != nil { count += 1 }
        if closeToWork != nil { count += 1 }
        if safeToLeaveComputer != nil { count += 1 }
        if walkingFriendlyLocation != nil { count += 1 }
        if exerciseWellnessAvailable != nil { count += 1 }
        if chargedLaptopBrickOnly != nil { count += 1 }
        if favoriteOnly == true { count += 1 }
        if searchText != nil && !searchText!.isEmpty { count += 1 }
        return count
    }

    // MARK: - Summary

    func summaryDescription() -> String? {
        var parts: [String] = []

        if favoriteOnly == true { parts.append("Favorites") }
        if let text = searchText, !text.isEmpty { parts.append(""\(text)"") }
        if !tiers.isEmpty { parts.append(tiers.map { $0.rawValue }.sorted().joined(separator: ", ")) }
        if !neighborhoods.isEmpty { parts.append(neighborhoods.sorted().joined(separator: ", ")) }
        if !placeTypes.isEmpty { parts.append(placeTypes.map { $0.shortName }.sorted().joined(separator: ", ")) }
        if !attributes.isEmpty { parts.append(attributes.map { $0.shortName }.sorted().joined(separator: ", ")) }
        if openLate == true { parts.append("Open late") }
        if closeToHome == true { parts.append("Near home") }
        if closeToWork == true { parts.append("Near work") }
        if safeToLeaveComputer == true { parts.append("Safe for laptop") }
        if walkingFriendlyLocation == true { parts.append("Walkable") }
        if exerciseWellnessAvailable == true { parts.append("Gym/wellness") }
        if chargedLaptopBrickOnly == true { parts.append("Bring brick") }

        guard !parts.isEmpty else { return nil }
        return parts.joined(separator: " • ")
    }

    // MARK: - Mutation Helpers

    mutating func clear() {
        self = SpotQuery()
    }

    mutating func toggle(tier: Tier) {
        if tiers.contains(tier) {
            tiers.remove(tier)
        } else {
            tiers.insert(tier)
        }
    }

    mutating func toggle(attribute: AttributeTag) {
        if attributes.contains(attribute) {
            attributes.remove(attribute)
        } else {
            attributes.insert(attribute)
        }
    }
}

// MARK: - SpotSort

enum SpotSort: String, Codable, CaseIterable, Hashable {
    case distance
    case sentiment
    case tier
    case timeOfDay

    var displayName: String {
        switch self {
        case .distance: return "Distance"
        case .sentiment: return "Sentiment"
        case .tier: return "Tier"
        case .timeOfDay: return "Time of day"
        }
    }

    var icon: String {
        switch self {
        case .distance: return "location"
        case .sentiment: return "heart"
        case .tier: return "star"
        case .timeOfDay: return "clock"
        }
    }
}

// MARK: - SessionPreset

struct SessionPreset: Identifiable, Codable, Hashable {
    let id: UUID
    let title: String
    let description: String
    let tags: Set<AttributeTag>
    let requiresOpenLate: Bool
    let prefersElite: Bool

    init(id: UUID = UUID(), title: String, description: String, tags: Set<AttributeTag>, requiresOpenLate: Bool, prefersElite: Bool) {
        self.id = id
        self.title = title
        self.description = description
        self.tags = tags
        self.requiresOpenLate = requiresOpenLate
        self.prefersElite = prefersElite
    }

    /// Apply this preset to a query
    func apply(to query: inout SpotQuery) {
        query.attributes.formUnion(tags)
        if requiresOpenLate { query.openLate = true }
        if prefersElite { query.tiers.insert(.elite) }
    }

    /// Create a query from this preset
    func toQuery() -> SpotQuery {
        var query = SpotQuery()
        apply(to: &query)
        return query
    }

    // MARK: - Built-in Presets

    static let deepFocus = SessionPreset(
        title: "Deep Focus",
        description: "Quiet, power-friendly spots for heads-down work",
        tags: [.deepFocus, .powerHeavy],
        requiresOpenLate: false,
        prefersElite: false
    )

    static let bodyDoubling = SessionPreset(
        title: "Body Doubling",
        description: "Social energy with good wifi",
        tags: [.bodyDoubling],
        requiresOpenLate: false,
        prefersElite: false
    )

    static let quickSprint = SessionPreset(
        title: "Quick Sprint",
        description: "≤90m, low friction, easy access",
        tags: [.easyParking],
        requiresOpenLate: false,
        prefersElite: false
    )

    static let lateNight = SessionPreset(
        title: "Late Night",
        description: "Open late + safe environment",
        tags: [.nightOwl],
        requiresOpenLate: true,
        prefersElite: false
    )

    static let allPresets: [SessionPreset] = [
        .deepFocus,
        .bodyDoubling,
        .quickSprint,
        .lateNight
    ]

    /// Alias for allPresets (for clearer API)
    static let defaults: [SessionPreset] = allPresets
}
