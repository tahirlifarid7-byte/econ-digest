import Foundation

@MainActor
final class DigestStore: ObservableObject {
    @Published var digest: Digest?
    @Published var isLoading = false
    @Published var errorMessage: String?

    /// Where digest.json is published (GitHub Pages, updated daily by .github/workflows/daily-digest.yml).
    @Published var serverURL: String {
        didSet { UserDefaults.standard.set(serverURL, forKey: "digestURL") }
    }

    private let cacheURL = FileManager.default
        .urls(for: .cachesDirectory, in: .userDomainMask)[0]
        .appendingPathComponent("digest.json")

    init() {
        serverURL = UserDefaults.standard.string(forKey: "digestURL") ?? "https://tahirlifarid7-byte.github.io/econ-digest/digest.json"
        digest = loadCached() ?? loadSample()
    }

    func refresh() async {
        guard let url = URL(string: serverURL) else {
            errorMessage = "Неверный адрес сервера"
            return
        }
        isLoading = true
        defer { isLoading = false }
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            digest = try JSONDecoder().decode(Digest.self, from: data)
            try? data.write(to: cacheURL)
            errorMessage = nil
        } catch {
            errorMessage = "Не удалось обновить: \(error.localizedDescription)"
        }
    }

    private func loadCached() -> Digest? {
        guard let data = try? Data(contentsOf: cacheURL) else { return nil }
        return try? JSONDecoder().decode(Digest.self, from: data)
    }

    private func loadSample() -> Digest? {
        guard let url = Bundle.main.url(forResource: "SampleDigest", withExtension: "json"),
              let data = try? Data(contentsOf: url) else { return nil }
        return try? JSONDecoder().decode(Digest.self, from: data)
    }
}
