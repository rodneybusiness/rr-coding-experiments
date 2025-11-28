import Foundation
import CoreLocation

// MARK: - City

/// Represents a city/region where work spots are available
struct City: Identifiable, Codable, Hashable {
    let id: String              // "la-westside", "sf-bay", "nyc", etc.
    let name: String            // Short display name: "LA Westside"
    let region: String          // Region/country: "California, USA"
    let dataFileName: String    // JSON file name without extension
    let spotCount: Int          // Number of spots (0 if no data yet)

    // Location anchors for distance calculations
    let defaultLatitude: Double
    let defaultLongitude: Double
    let homeLatitude: Double?
    let homeLongitude: Double?
    let workLatitude: Double?
    let workLongitude: Double?

    // MARK: - Computed Properties

    var defaultAnchor: CLLocation {
        CLLocation(latitude: defaultLatitude, longitude: defaultLongitude)
    }

    var homeAnchor: CLLocation? {
        guard let lat = homeLatitude, let lon = homeLongitude else { return nil }
        return CLLocation(latitude: lat, longitude: lon)
    }

    var workAnchor: CLLocation? {
        guard let lat = workLatitude, let lon = workLongitude else { return nil }
        return CLLocation(latitude: lat, longitude: lon)
    }

    /// Whether this city has spot data available
    var hasData: Bool { spotCount > 0 }

    /// Display string showing spot count
    var spotCountLabel: String {
        if spotCount == 0 {
            return "Coming soon"
        } else if spotCount == 1 {
            return "1 spot"
        } else {
            return "\(spotCount) spots"
        }
    }

    /// Full display name with region
    var fullName: String {
        "\(name), \(region)"
    }
}

// MARK: - Available Cities

extension City {

    // MARK: - California

    /// LA Westside - Primary city with full data
    static let laWestside = City(
        id: "la-westside",
        name: "LA Westside",
        region: "California, USA",
        dataFileName: "westside_remote_work_master_verified",
        spotCount: 44,
        defaultLatitude: 34.015,
        defaultLongitude: -118.45,
        homeLatitude: 33.958,
        homeLongitude: -118.396,
        workLatitude: 34.040,
        workLongitude: -118.429
    )

    /// San Francisco Bay Area
    static let sanFrancisco = City(
        id: "sf-bay",
        name: "San Francisco",
        region: "California, USA",
        dataFileName: "sf_bay_spots",
        spotCount: 2, // Kimpton Alton + AvantSpace Marina
        defaultLatitude: 37.7749,
        defaultLongitude: -122.4194,
        homeLatitude: nil,
        homeLongitude: nil,
        workLatitude: 37.7858,  // Financial District
        workLongitude: -122.4008
    )

    // MARK: - East Coast USA

    /// New York City
    static let newYork = City(
        id: "nyc",
        name: "New York",
        region: "New York, USA",
        dataFileName: "nyc_spots",
        spotCount: 0,
        defaultLatitude: 40.7128,
        defaultLongitude: -74.0060,
        homeLatitude: nil,
        homeLongitude: nil,
        workLatitude: 40.7580,  // Midtown
        workLongitude: -73.9855
    )

    // MARK: - Midwest USA

    /// Detroit / Ann Arbor region
    static let detroitAnnArbor = City(
        id: "detroit-aa",
        name: "Detroit / Ann Arbor",
        region: "Michigan, USA",
        dataFileName: "detroit_ann_arbor_spots",
        spotCount: 0,
        defaultLatitude: 42.2808,  // Between Detroit and Ann Arbor
        defaultLongitude: -83.7430,
        homeLatitude: nil,
        homeLongitude: nil,
        workLatitude: 42.3314,  // Detroit downtown
        workLongitude: -83.0458
    )

    // MARK: - Europe

    /// London, UK
    static let london = City(
        id: "london",
        name: "London",
        region: "United Kingdom",
        dataFileName: "london_spots",
        spotCount: 1, // Second Home Kensington
        defaultLatitude: 51.5074,
        defaultLongitude: -0.1278,
        homeLatitude: nil,
        homeLongitude: nil,
        workLatitude: 51.5155,  // City of London
        workLongitude: -0.0922
    )

    /// Paris, France
    static let paris = City(
        id: "paris",
        name: "Paris",
        region: "France",
        dataFileName: "paris_spots",
        spotCount: 0,
        defaultLatitude: 48.8566,
        defaultLongitude: 2.3522,
        homeLatitude: nil,
        homeLongitude: nil,
        workLatitude: 48.8738,  // 8th arrondissement
        workLongitude: 2.2950
    )

    // MARK: - All Available Cities

    /// All cities, sorted by data availability then name
    static let available: [City] = [
        .laWestside,
        .sanFrancisco,
        .london,
        .newYork,
        .detroitAnnArbor,
        .paris
    ].sorted { lhs, rhs in
        // Cities with data come first
        if lhs.hasData != rhs.hasData {
            return lhs.hasData
        }
        // Then sort by name
        return lhs.name < rhs.name
    }

    /// Cities that have spot data
    static var citiesWithData: [City] {
        available.filter { $0.hasData }
    }

    /// Find a city by its ID
    static func find(byID id: String) -> City? {
        available.first { $0.id == id }
    }

    /// Default city when none is selected
    static var `default`: City { .laWestside }
}

// MARK: - City Group (for UI organization)

struct CityGroup: Identifiable {
    let id: String
    let name: String
    let cities: [City]

    static let all: [CityGroup] = [
        CityGroup(id: "usa-west", name: "West Coast USA", cities: [.laWestside, .sanFrancisco]),
        CityGroup(id: "usa-east", name: "East Coast USA", cities: [.newYork]),
        CityGroup(id: "usa-midwest", name: "Midwest USA", cities: [.detroitAnnArbor]),
        CityGroup(id: "europe", name: "Europe", cities: [.london, .paris])
    ]
}
