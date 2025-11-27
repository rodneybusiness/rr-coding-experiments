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
    ///   - mode: Travel mode (driving, walking, transit)
    /// - Returns: Formatted time string like "5 min drive"
    static func estimatedTime(meters: Double, mode: TravelMode = .driving) -> String {
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

}

// MARK: - Travel Mode

enum TravelMode {
    case driving
    case walking
    case transit

    var metersPerMinute: Double {
        switch self {
        case .driving: return 670  // ~25 mph average with traffic
        case .walking: return 80   // ~3 mph
        case .transit: return 400  // ~15 mph with stops
        }
    }

    var suffix: String {
        switch self {
        case .driving: return "drive"
        case .walking: return "walk"
        case .transit: return "transit"
        }
    }
}

// MARK: - Friction Badges

enum FrictionBadge {
    /// Determines the appropriate friction warning for a spot
    /// - Parameter spot: The location spot to evaluate
    /// - Returns: A FrictionWarning or nil if no friction
    static func evaluate(for spot: LocationSpot) -> FrictionWarning? {
        return evaluate(for: spot, hour: Calendar.current.component(.hour, from: Date()))
    }

    /// Determines the appropriate friction warning for a spot at a given hour
    /// - Parameters:
    ///   - spot: The location spot to evaluate
    ///   - hour: The hour of day (0-23)
    /// - Returns: A FrictionWarning or nil if no friction
    static func evaluate(for spot: LocationSpot, hour: Int) -> FrictionWarning? {
        // High severity: things that could ruin a work session
        if spot.chargedLaptopBrickOnly {
            return FrictionWarning(
                message: "Charge before you go",
                detail: "Limited or no power outlets available",
                severity: .high,
                icon: "battery.25"
            )
        }

        // Time-sensitive: evening/night safety
        if hour >= 20 && !spot.safeToLeaveComputer {
            return FrictionWarning(
                message: "Keep belongings close at night",
                detail: "May be busier/less secure after dark",
                severity: .high,
                icon: "moon.fill"
            )
        }

        // Time-sensitive: rush hour parking
        if (hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19) {
            if !spot.attributes.contains(.easyParking) && !spot.walkingFriendlyLocation {
                return FrictionWarning(
                    message: "Rush hour - expect parking delays",
                    detail: "Consider arriving early or using transit",
                    severity: .medium,
                    icon: "car.fill"
                )
            }
        }

        // Medium severity: inconveniences
        if !spot.attributes.contains(.easyParking) && !spot.walkingFriendlyLocation {
            return FrictionWarning(
                message: "Parking may be tricky",
                detail: "Street parking or paid lots only",
                severity: .medium,
                icon: "car.fill"
            )
        }

        // Low severity: nice-to-know info
        if !spot.safeToLeaveComputer {
            return FrictionWarning(
                message: "Keep laptop with you",
                detail: "Not ideal for bathroom breaks",
                severity: .low,
                icon: "eye.fill"
            )
        }

        return nil
    }

    /// All applicable friction warnings for a spot (may be multiple)
    static func allWarnings(for spot: LocationSpot) -> [FrictionWarning] {
        return allWarnings(for: spot, hour: Calendar.current.component(.hour, from: Date()))
    }

    /// All applicable friction warnings for a spot at a given hour
    static func allWarnings(for spot: LocationSpot, hour: Int) -> [FrictionWarning] {
        var warnings: [FrictionWarning] = []

        if spot.chargedLaptopBrickOnly {
            warnings.append(FrictionWarning(
                message: "Charge before you go",
                detail: "Limited or no power outlets available",
                severity: .high,
                icon: "battery.25"
            ))
        }

        // Time-sensitive: evening/night
        if hour >= 20 && !spot.safeToLeaveComputer {
            warnings.append(FrictionWarning(
                message: "Keep belongings close at night",
                detail: "May be busier/less secure after dark",
                severity: .high,
                icon: "moon.fill"
            ))
        }

        // Time-sensitive: rush hour
        if (hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19) {
            if !spot.attributes.contains(.easyParking) && !spot.walkingFriendlyLocation {
                warnings.append(FrictionWarning(
                    message: "Rush hour - expect parking delays",
                    detail: "Consider arriving early or using transit",
                    severity: .medium,
                    icon: "car.fill"
                ))
            }
        } else if !spot.attributes.contains(.easyParking) && !spot.walkingFriendlyLocation {
            warnings.append(FrictionWarning(
                message: "Parking may be tricky",
                detail: "Street parking or paid lots only",
                severity: .medium,
                icon: "car.fill"
            ))
        }

        if !spot.safeToLeaveComputer && hour < 20 {
            warnings.append(FrictionWarning(
                message: "Keep laptop with you",
                detail: "Not ideal for bathroom breaks",
                severity: .low,
                icon: "eye.fill"
            ))
        }

        if !spot.attributes.contains(.powerHeavy) && !spot.chargedLaptopBrickOnly {
            warnings.append(FrictionWarning(
                message: "Limited outlets",
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
    let message: String
    let detail: String
    let severity: Severity
    let icon: String

    /// Convenience alias for message
    var text: String { message }

    enum Severity: Int, Comparable {
        case low = 0
        case medium = 1
        case high = 2

        static func < (lhs: Severity, rhs: Severity) -> Bool {
            lhs.rawValue < rhs.rawValue
        }
    }

    static func == (lhs: FrictionWarning, rhs: FrictionWarning) -> Bool {
        lhs.message == rhs.message && lhs.severity == rhs.severity
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

// MARK: - Note
// AttributeTag, Tier, and PlaceType display properties (emoji, displayText, shortName,
// displayColor, icon, etc.) are defined in LocationSpot.swift as part of the enum definitions.
// This avoids duplicate definitions and keeps all model-related code together.
