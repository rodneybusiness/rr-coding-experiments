import Foundation
import CoreLocation

// MARK: - Distance Formatting

enum DistanceFormatter {
    private static let milesPerMeter: Double = 1 / 1609.34

    /// Formats a distance in meters to a human-readable string
    /// - Parameter meters: Distance in meters
    /// - Returns: Formatted string like "0.5 mi" or "2.3 mi"
    static func format(meters: Double) -> String {
        let miles = meters * milesPerMeter
        if miles < 0.1 {
            return "< 0.1 mi"
        } else if miles < 10 {
            return String(format: "%.1f mi", miles)
        } else {
            return String(format: "%.0f mi", miles)
        }
    }

    /// Formats distance between a spot and an anchor location
    /// - Parameters:
    ///   - spot: The location spot
    ///   - anchor: The anchor location (user position, home, or work)
    /// - Returns: Formatted distance string or nil if coordinates unavailable
    static func format(spot: LocationSpot, from anchor: CLLocation?) -> String? {
        guard let distance = spot.distance(from: anchor) else { return nil }
        return format(meters: distance)
    }

    /// Returns estimated travel time based on distance
    /// - Parameters:
    ///   - meters: Distance in meters
    ///   - mode: Travel mode (drive, walk, bike)
    /// - Returns: Formatted time string like "5 min drive"
    static func estimatedTime(meters: Double, mode: TravelMode = .drive) -> String {
        let minutes = Int(ceil(meters / mode.metersPerMinute))
        if minutes < 1 {
            return "< 1 min \(mode.suffix)"
        } else if minutes == 1 {
            return "1 min \(mode.suffix)"
        } else if minutes < 60 {
            return "\(minutes) min \(mode.suffix)"
        } else {
            let hours = minutes / 60
            let remainingMinutes = minutes % 60
            if remainingMinutes == 0 {
                return "\(hours) hr \(mode.suffix)"
            }
            return "\(hours) hr \(remainingMinutes) min \(mode.suffix)"
        }
    }

    enum TravelMode {
        case drive
        case walk
        case bike

        var metersPerMinute: Double {
            switch self {
            case .drive: return 670  // ~25 mph average with traffic
            case .walk: return 80    // ~3 mph
            case .bike: return 250   // ~9 mph
            }
        }

        var suffix: String {
            switch self {
            case .drive: return "drive"
            case .walk: return "walk"
            case .bike: return "bike"
            }
        }
    }
}

// MARK: - Friction Badges

enum FrictionBadge {
    /// Determines the appropriate friction warning for a spot
    /// - Parameter spot: The location spot to evaluate
    /// - Returns: A tuple of (badge text, severity) or nil if no friction
    static func evaluate(for spot: LocationSpot) -> FrictionWarning? {
        // High severity: things that could ruin a work session
        if spot.chargedLaptopBrickOnly {
            return FrictionWarning(
                text: "Charge before you go",
                detail: "Limited or no power outlets available",
                severity: .high,
                icon: "battery.25"
            )
        }

        // Medium severity: inconveniences
        if !spot.attributes.contains(.easyParking) && !spot.walkingFriendlyLocation {
            return FrictionWarning(
                text: "Parking may be tricky",
                detail: "Street parking or paid lots only",
                severity: .medium,
                icon: "car.fill"
            )
        }

        // Low severity: nice-to-know info
        if !spot.safeToLeaveComputer {
            return FrictionWarning(
                text: "Keep laptop with you",
                detail: "Not ideal for bathroom breaks",
                severity: .low,
                icon: "eye.fill"
            )
        }

        return nil
    }

    /// All applicable friction warnings for a spot (may be multiple)
    static func allWarnings(for spot: LocationSpot) -> [FrictionWarning] {
        var warnings: [FrictionWarning] = []

        if spot.chargedLaptopBrickOnly {
            warnings.append(FrictionWarning(
                text: "Charge before you go",
                detail: "Limited or no power outlets available",
                severity: .high,
                icon: "battery.25"
            ))
        }

        if !spot.attributes.contains(.easyParking) && !spot.walkingFriendlyLocation {
            warnings.append(FrictionWarning(
                text: "Parking may be tricky",
                detail: "Street parking or paid lots only",
                severity: .medium,
                icon: "car.fill"
            ))
        }

        if !spot.safeToLeaveComputer {
            warnings.append(FrictionWarning(
                text: "Keep laptop with you",
                detail: "Not ideal for bathroom breaks",
                severity: .low,
                icon: "eye.fill"
            ))
        }

        if !spot.attributes.contains(.powerHeavy) && !spot.chargedLaptopBrickOnly {
            warnings.append(FrictionWarning(
                text: "Limited outlets",
                detail: "Bring a fully charged laptop",
                severity: .low,
                icon: "bolt.slash.fill"
            ))
        }

        return warnings
    }
}

struct FrictionWarning: Identifiable, Equatable {
    let id = UUID()
    let text: String
    let detail: String
    let severity: Severity
    let icon: String

    enum Severity: Int, Comparable {
        case low = 0
        case medium = 1
        case high = 2

        static func < (lhs: Severity, rhs: Severity) -> Bool {
            lhs.rawValue < rhs.rawValue
        }
    }

    static func == (lhs: FrictionWarning, rhs: FrictionWarning) -> Bool {
        lhs.text == rhs.text && lhs.severity == rhs.severity
    }
}

// MARK: - Relative Time Formatting

enum RelativeTimeFormatter {
    private static let formatter: RelativeDateTimeFormatter = {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .abbreviated
        return formatter
    }()

    private static let fullFormatter: RelativeDateTimeFormatter = {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .full
        return formatter
    }()

    /// Formats a date relative to now in abbreviated form
    /// - Parameter date: The date to format
    /// - Returns: String like "2h ago" or "3d ago"
    static func abbreviated(from date: Date) -> String {
        formatter.localizedString(for: date, relativeTo: Date())
    }

    /// Formats a date relative to now in full form
    /// - Parameter date: The date to format
    /// - Returns: String like "2 hours ago" or "3 days ago"
    static func full(from date: Date) -> String {
        fullFormatter.localizedString(for: date, relativeTo: Date())
    }

    /// Formats last visited date with context
    /// - Parameter date: The last visited date
    /// - Returns: Formatted string like "Visited 2 days ago"
    static func lastVisited(_ date: Date?) -> String? {
        guard let date else { return nil }
        return "Visited \(abbreviated(from: date))"
    }
}

// MARK: - Attribute Display

extension AttributeTag {
    /// The emoji component of the attribute
    var emoji: String {
        String(rawValue.prefix(while: { !$0.isLetter && !$0.isWhitespace }))
    }

    /// The text component without emoji
    var displayText: String {
        rawValue.drop(while: { !$0.isLetter }).trimmingCharacters(in: .whitespaces)
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
}

// MARK: - Tier Display

extension Tier {
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

// MARK: - PlaceType Display

extension PlaceType {
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
        case .cafeRestaurant: return "Cafe"
        case .bookstoreCafe: return "Bookstore"
        case .bankCafe: return "Bank Cafe"
        case .library: return "Library"
        case .unknown: return "Other"
        }
    }
}
