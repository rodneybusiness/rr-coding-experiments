import SwiftUI
import CoreLocation

struct SpotCard: View {
    let spot: LocationSpot
    let distanceText: String?
    let frictionBadge: String?
    var isFavorite: Bool = false
    var onFavorite: (() -> Void)? = nil
    var onTap: (() -> Void)? = nil

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(spot.name)
                        .font(.headline)
                        .foregroundStyle(.primary)
                    Text("\(spot.neighborhood) • \(spot.placeType.rawValue)")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                Spacer()
                if let distanceText {
                    Text(distanceText)
                        .font(.subheadline.weight(.semibold))
                        .padding(8)
                        .background(Capsule().fill(.blue.opacity(0.12)))
                }
                if let onFavorite {
                    Button(action: onFavorite) {
                        Image(systemName: isFavorite ? "heart.fill" : "heart")
                            .foregroundStyle(isFavorite ? .red : .primary)
                    }
                    .buttonStyle(.plain)
                }
            }

            Text(spot.criticalFieldNotes)
                .font(.footnote)
                .foregroundStyle(.primary)
                .lineLimit(3)

            HStack(spacing: 6) {
                ForEach(spot.attributes.prefix(4)) { tag in
                    Text(tag.rawValue)
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 6)
                        .background(Capsule().fill(.gray.opacity(0.15)))
                }
            }

            if let frictionBadge {
                Label(frictionBadge, systemImage: "exclamationmark.triangle.fill")
                    .font(.caption)
                    .foregroundStyle(.orange)
            }
        }
        .padding()
        .background(RoundedRectangle(cornerRadius: 16, style: .continuous).fill(Color(uiColor: .secondarySystemBackground)))
        .shadow(color: .black.opacity(0.05), radius: 4, x: 0, y: 2)
        .contentShape(Rectangle())
        .onTapGesture { onTap?() }
    }
}
