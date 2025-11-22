import Foundation

enum TimeOfDayScoring {
    static func score(for spot: LocationSpot, context: TimeContext) -> Double {
        let hour = context.hour
        var score = spot.sentimentScore

        // Early morning preference
        if hour < 8 {
            if spot.attributes.contains(.earlyBird) { score += 1.5 }
            if spot.chargedLaptopBrickOnly { score -= 0.5 }
        }

        // Evening bias
        if hour >= 18 {
            if spot.openLate || spot.attributes.contains(.nightOwl) { score += 1.0 }
            if !spot.safeToLeaveComputer { score -= 0.3 }
        }

        // Quick sprint heuristic (<=90m): prioritize frictionless parking/walking
        if spot.attributes.contains(.easyParking) || spot.walkingFriendlyLocation {
            score += 0.3
        }

        return score
    }
}
