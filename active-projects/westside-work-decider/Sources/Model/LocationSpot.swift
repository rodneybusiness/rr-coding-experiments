import Foundation
import CoreLocation

enum Tier: String, Codable, CaseIterable, Identifiable {
    case elite = "Elite"
    case reliable = "Reliable"
    case unknown

    var id: String { rawValue }
}

enum PlaceType: String, Codable, CaseIterable, Identifiable {
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
}

enum AttributeTag: String, Codable, CaseIterable, Identifiable {
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
}

struct LocationSpot: Identifiable, Codable, Equatable {
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
    var isFavorite: Bool = false
    var userNotes: String? = nil
    var lastVisited: Date? = nil
    var latitude: Double?
    var longitude: Double?

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
    }

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
            .compactMap { AttributeTag(rawValue: $0) ?? (AttributeTag(rawValue: $0 + "") ?? .unknown) }
        criticalFieldNotes = try container.decode(String.self, forKey: .criticalFieldNotes)
        status = try container.decode(String.self, forKey: .status)
        latitude = try container.decodeIfPresent(Double.self, forKey: .latitude)
        longitude = try container.decodeIfPresent(Double.self, forKey: .longitude)
        id = LocationSpot.makeID(name: name, neighborhood: neighborhood)
    }

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
        longitude: Double? = nil
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
    }

    func distance(from location: CLLocation?) -> CLLocationDistance? {
        guard let latitude, let longitude, let origin = location else { return nil }
        let dest = CLLocation(latitude: latitude, longitude: longitude)
        return origin.distance(from: dest)
    }

    func matches(tagFilters: Set<AttributeTag>) -> Bool {
        guard !tagFilters.isEmpty else { return true }
        let attrSet = Set(attributes)
        return tagFilters.isSubset(of: attrSet)
    }

    static func makeID(name: String, neighborhood: String) -> String {
        let slug = "\(name.lowercased())-\(neighborhood.lowercased())"
            .replacingOccurrences(of: " ", with: "-")
            .replacingOccurrences(of: ",", with: "")
        return slug
    }
}

struct SpotQuery: Codable {
    var tiers: Set<Tier> = []
    var neighborhoods: Set<String> = []
    var placeTypes: Set<PlaceType> = []
    var attributes: Set<AttributeTag> = []
    var openLate: Bool? = nil
    var closeToHome: Bool? = nil
    var closeToWork: Bool? = nil
    var safeToLeaveComputer: Bool? = nil
    var walkingFriendlyLocation: Bool? = nil
    var exerciseWellnessAvailable: Bool? = nil
    var chargedLaptopBrickOnly: Bool? = nil

    var hasFilters: Bool {
        !tiers.isEmpty || !neighborhoods.isEmpty || !placeTypes.isEmpty || !attributes.isEmpty ||
        openLate != nil || closeToHome != nil || closeToWork != nil || safeToLeaveComputer != nil ||
        walkingFriendlyLocation != nil || exerciseWellnessAvailable != nil || chargedLaptopBrickOnly != nil
    }

    func summaryDescription() -> String? {
        var parts: [String] = []
        if !tiers.isEmpty { parts.append("Tier: \(tiers.map { $0.rawValue }.sorted().joined(separator: ", "))") }
        if !neighborhoods.isEmpty { parts.append("Areas: \(neighborhoods.sorted().joined(separator: ", "))") }
        if !placeTypes.isEmpty { parts.append("Types: \(placeTypes.map { $0.rawValue }.sorted().joined(separator: ", "))") }
        if !attributes.isEmpty { parts.append("Tags: \(attributes.map { $0.rawValue }.sorted().joined(separator: ", "))") }
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
}

enum SpotSort: String, CaseIterable {
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
}

struct SessionPreset: Identifiable, Codable {
    let id = UUID()
    let title: String
    let description: String
    let tags: Set<AttributeTag>
    let requiresOpenLate: Bool
    let prefersElite: Bool
}
