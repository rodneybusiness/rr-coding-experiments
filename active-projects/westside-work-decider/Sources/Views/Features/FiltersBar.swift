import SwiftUI

struct FiltersBar: View {
    @ObservedObject var queryModel: SpotQueryModel

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                TogglePill(title: "Elite", isOn: Binding(
                    get: { queryModel.query.tiers.contains(.elite) },
                    set: { isOn in
                        updateQuery { query in
                            if isOn { query.tiers.insert(.elite) } else { query.tiers.remove(.elite) }
                        }
                    }
                ))
                TogglePill(title: "Reliable", isOn: Binding(
                    get: { queryModel.query.tiers.contains(.reliable) },
                    set: { isOn in
                        updateQuery { query in
                            if isOn { query.tiers.insert(.reliable) } else { query.tiers.remove(.reliable) }
                        }
                    }
                ))
                TogglePill(title: "Open late", isOn: Binding(
                    get: { queryModel.query.openLate ?? false },
                    set: { isOn in
                        updateQuery { query in query.openLate = isOn }
                    }
                ))
                TogglePill(title: "Easy parking", isOn: Binding(
                    get: { queryModel.query.attributes.contains(.easyParking) },
                    set: { isOn in
                        updateQuery { query in
                            if isOn { query.attributes.insert(.easyParking) } else { query.attributes.remove(.easyParking) }
                        }
                    }
                ))
                TogglePill(title: "Deep focus", isOn: Binding(
                    get: { queryModel.query.attributes.contains(.deepFocus) },
                    set: { isOn in
                        updateQuery { query in
                            if isOn { query.attributes.insert(.deepFocus) } else { query.attributes.remove(.deepFocus) }
                        }
                    }
                ))
            }
            .padding(.vertical, 8)
            .padding(.horizontal, 4)
        }
    }

    private func updateQuery(_ mutate: (inout SpotQuery) -> Void) {
        var updated = queryModel.query
        mutate(&updated)
        queryModel.query = updated
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
