import SwiftUI

struct ContentView: View {
    @EnvironmentObject var store: DigestStore
    @State private var showSettings = false

    var body: some View {
        TabView {
            tab("Мир", icon: "globe") { $0.world }
            tab("Турция", icon: "turkishlirasign") { $0.turkey }
        }
        .sheet(isPresented: $showSettings) { SettingsView() }
    }

    private func tab(_ title: String, icon: String, section: @escaping (Digest) -> DigestSection) -> some View {
        NavigationStack {
            List {
                if let error = store.errorMessage {
                    Text(error).font(.footnote).foregroundStyle(.orange)
                }
                if let digest = store.digest {
                    let s = section(digest)
                    Section {
                        Text(s.summary).font(.body)
                    } header: {
                        Text(digest.date)
                    }
                    if !digest.indicators.isEmpty {
                        Section("Показатели") { IndicatorsRow(indicators: digest.indicators) }
                    }
                    Section("События") {
                        ForEach(s.items) { NewsRow(item: $0) }
                    }
                } else {
                    ProgressView()
                }
            }
            .navigationTitle(title)
            .refreshable { await store.refresh() }
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button { showSettings = true } label: { Image(systemName: "gearshape") }
                }
            }
            .overlay { if store.isLoading && store.digest == nil { ProgressView() } }
        }
        .tabItem { Label(title, systemImage: icon) }
    }
}

struct IndicatorsRow: View {
    let indicators: [Indicator]
    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(indicators) { i in
                    VStack(alignment: .leading, spacing: 2) {
                        Text(i.name).font(.caption).foregroundStyle(.secondary)
                        Text(i.value ?? "—").font(.headline)
                        if let c = i.change {
                            Text(c).font(.caption2).foregroundStyle(c.hasPrefix("-") ? .red : .green)
                        }
                    }
                    .padding(10)
                    .background(.quaternary, in: RoundedRectangle(cornerRadius: 10))
                }
            }
        }
    }
}

struct NewsRow: View {
    let item: NewsItem

    private var color: Color {
        switch item.impact {
        case "positive": .green
        case "negative": .red
        default: .gray
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .top, spacing: 8) {
                Circle().fill(color).frame(width: 8, height: 8).padding(.top, 6)
                Text(item.title).font(.headline)
            }
            Text(item.detail).font(.subheadline).foregroundStyle(.secondary)
            if let source = item.source {
                if let u = item.url, let url = URL(string: u) {
                    Link(source, destination: url).font(.caption)
                } else {
                    Text(source).font(.caption).foregroundStyle(.tertiary)
                }
            }
        }
        .padding(.vertical, 4)
    }
}

struct SettingsView: View {
    @EnvironmentObject var store: DigestStore
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            Form {
                Section("Адрес digest.json") {
                    TextField("URL", text: $store.serverURL)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .keyboardType(.URL)
                }
            }
            .navigationTitle("Настройки")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Готово") { dismiss(); Task { await store.refresh() } }
                }
            }
        }
    }
}
