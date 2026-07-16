import SwiftUI

@main
struct NexusApp: App {
    @State private var container = AppContainer.shared

    var body: some Scene {
        WindowGroup {
            LoginView()
                .environment(container)
        }
    }
}
