import Foundation
import CoreLocation

extension CLLocationCoordinate2D: Codable {
    public func encode(to encoder: Encoder) throws {
        var container = encoder.unkeyedContainer()
        try container.encode(latitude)
        try container.encode(longitude)
    }

    public init(from decoder: Decoder) throws {
        var container = try decoder.unkeyedContainer()
        let lat = try container.decode(CLLocationDegrees.self)
        let lon = try container.decode(CLLocationDegrees.self)
        self.init(latitude: lat, longitude: lon)
    }
}
