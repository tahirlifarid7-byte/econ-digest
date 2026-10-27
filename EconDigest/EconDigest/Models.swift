import Foundation

struct Digest: Codable {
    let date: String
    let generatedAt: String?
    let indicators: [Indicator]
    let world: DigestSection
    let turkey: DigestSection

    enum CodingKeys: String, CodingKey {
        case date, indicators, world, turkey
        case generatedAt = "generated_at"
    }
}

struct Indicator: Codable, Identifiable {
    var id: String { name }
    let name: String
    let value: String?
    let change: String?
}

struct DigestSection: Codable {
    let summary: String
    let items: [NewsItem]
}

struct NewsItem: Codable, Identifiable {
    var id: String { title }
    let title: String
    let detail: String
    let impact: String?
    let source: String?
    let url: String?
}
