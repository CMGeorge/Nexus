import SwiftUI

// #if !os(macOS)
@main
// #endif
struct NexusApp: App {
    // #if !os(macOS)
    @UIApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    // #endif
    private let container = AppContainer.shared

    var body: some Scene {
        WindowGroup {
            LoginView()
                .environment(container)
        }
    }
}
