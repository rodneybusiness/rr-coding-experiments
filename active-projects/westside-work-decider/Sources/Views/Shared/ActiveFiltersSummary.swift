import SwiftUI

struct ActiveFiltersSummary: View {
    let query: SpotQuery
    let sort: SpotSort

    var body: some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Label(query.summaryDescription() ?? "No filters applied", systemImage: "line.3.horizontal.decrease.circle")
                .font(.footnote)
                .foregroundStyle(.secondary)
            Spacer()
            Text("Sort: \(sort.displayName)")
                .font(.footnote.weight(.semibold))
                .foregroundStyle(.secondary)
        }
        .padding(.vertical, 6)
    }
}
