import SwiftUI

struct FiltersBar: View {
    @Binding var query: SpotQuery

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                TogglePill(title: "Elite", isOn: Binding(
                    get: { query.tiers.contains(.elite) },
                    set: { isOn in
                        if isOn { query.tiers.insert(.elite) } else { query.tiers.remove(.elite) }
                    }
                ))
                TogglePill(title: "Reliable", isOn: Binding(
                    get: { query.tiers.contains(.reliable) },
                    set: { isOn in
                        if isOn { query.tiers.insert(.reliable) } else { query.tiers.remove(.reliable) }
                    }
                ))
                TogglePill(title: "Open late", isOn: Binding(
                    get: { query.openLate ?? false },
                    set: { query.openLate = $0 }
                ))
                TogglePill(title: "Easy parking", isOn: Binding(
                    get: { query.attributes.contains(.easyParking) },
                    set: { isOn in
                        if isOn { query.attributes.insert(.easyParking) } else { query.attributes.remove(.easyParking) }
                    }
                ))
                TogglePill(title: "Deep focus", isOn: Binding(
                    get: { query.attributes.contains(.deepFocus) },
                    set: { isOn in
                        if isOn { query.attributes.insert(.deepFocus) } else { query.attributes.remove(.deepFocus) }
                    }
                ))
            }
            .padding(.vertical, 8)
            .padding(.horizontal, 4)
        }
    }
}

private struct TogglePill: View {
    let title: String
    @Binding var isOn: Bool

    var body: some View {
        Button {
            isOn.toggle()
        } label: {
            Text(title)
                .font(.subheadline.weight(.semibold))
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(Capsule().fill(isOn ? Color.accentColor.opacity(0.2) : Color.gray.opacity(0.15)))
        }
        .buttonStyle(.plain)
    }
}
