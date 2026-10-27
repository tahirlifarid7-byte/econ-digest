import Foundation

@MainActor
final class DigestStore: ObservableObject {
    @Published var digest: Digest?
    @Published var isLoading = false
    @Published var errorMessage: String?

    /// Where the backend serves digest.json (see README). The simulator reaches the Mac at localhost.
    @Published var serverURL: String {
        didSet { UserDefaults.standard.set(serverURL, forKey: "serverURL") }
    }

    private let cacheURL = FileManager.default
        .urls(for: .cachesDirectory, in: .userDomainMask)[0]
        .appendingPathComponent("digest.json")

    init() {
        serverURL = UserDefaults.standard.string(forKey: "serverURL") ?? "http://localhost:8000/digest.json"
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
