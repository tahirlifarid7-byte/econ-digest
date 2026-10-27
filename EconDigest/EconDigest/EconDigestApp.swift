import SwiftUI

@main
struct EconDigestApp: App {
    @StateObject private var store = DigestStore()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(store)
                .task { await store.refresh() }
        }
    }
}
