import UIKit
import UserNotifications
import FirebaseCore
import FirebaseMessaging

#if !os(macOS)
/// All known deep link routes in the Nexus app.
///
/// Parse an incoming URL with `DeepLinkRoute(url:)`, then switch exhaustively.
/// Adding a new case here forces every `switch` site to handle it — no silent
/// fallthrough via `default`.
enum DeepLinkRoute: Equatable {
    case resetPassword(token: String)
    case magicLink(email: String)
    case appointment(id: String)
    case unknown(host: String?)

    /// Attempts to parse a URL into a known `DeepLinkRoute`.
    /// Returns `nil` only when the URL itself is malformed (can't be parsed as `URLComponents`).
    /// Unrecognised hosts produce `.unknown(host:)`, not `nil`.
    init?(url: URL) {
        guard let components = URLComponents(url: url, resolvingAgainstBaseURL: false) else { return nil }
        let host = components.host?.lowercased()

        switch host {
        case "reset-password":
            guard let token = components.queryItems?.first(where: { $0.name == "token" })?.value else { return nil }
            self = .resetPassword(token: token)
        case "magic-link":
            guard let email = components.queryItems?.first(where: { $0.name == "email" })?.value else { return nil }
            self = .magicLink(email: email)
        case "appointments":
            let pathComponents = url.pathComponents
            guard let id = pathComponents.last, id != "/" else { return nil }
            self = .appointment(id: id)
        default:
            self = .unknown(host: host)
        }
    }
}


/// UIKit app delegate for application-level system callbacks.
///
/// ## Why this exists
/// SwiftUI's `App` lifecycle manages scenes, but some system callbacks are still delivered
/// through `UIApplicationDelegate`, while others can optionally be handled using SwiftUI
/// APIs such as `.onOpenURL`:
///
/// | Callback | SwiftUI alternative | Why we use the delegate |
/// |---|---|---|
/// | Push notification token | — | No SwiftUI equivalent. Must go through the delegate. |
/// | Push registration failure | — | No SwiftUI equivalent. |
/// | Custom URL schemes | `.onOpenURL` | Delegate for unified routing in one place. |
/// | Universal Links | `.onContinueUserActivity` | Delegate for unified routing in one place. |
///
/// ## Lifecycle safety
/// This delegate runs alongside `WindowGroup` — it does NOT replace or override the SwiftUI
/// scene lifecycle. The `UIApplicationDelegateAdaptor` property wrapper in `NexusApp.swift`
/// bridges only the delegate callbacks without touching scenes.
final class AppDelegate: NSObject, UIApplicationDelegate, UNUserNotificationCenterDelegate, MessagingDelegate {

    // MARK: - Firebase & Push Notifications

    /// Called when the app launch sequence finishes.
    /// Configures Firebase (if the plist exists), sets up push preferences, and requests permission.
    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil
    ) -> Bool {
        // Check for GoogleService-Info.plist before configuring Firebase.
        // Without this guard, FirebaseApp.configure() crashes with a fatal error.
        if Bundle.main.path(forResource: "GoogleService-Info", ofType: "plist") != nil {
            FirebaseApp.configure()
            AppContainer.isFirebaseConfigured = true
            Messaging.messaging().delegate = self
            print("[Firebase] Configured successfully")
        } else {
            AppContainer.isFirebaseConfigured = false
            print("[Firebase] ⚠️ GoogleService-Info.plist not found — Firebase features disabled")
        }

        registerForPushNotifications(application)
        return true
    }

    /// Called when the device successfully registers for remote notifications.
    /// Forwards the APNs token to Firebase Messaging for swizzled setup.
    /// - Parameter deviceToken: The APNs token data.
    func application(
        _ application: UIApplication,
        didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
    ) {
        let tokenString = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()

        // Forward to Firebase Messaging only if Firebase is configured
        if AppContainer.isFirebaseConfigured {
            Messaging.messaging().apnsToken = deviceToken
        }

        // Send token to backend for push notification targeting
        // e.g., await container.authRepository.updatePushToken(tokenString)
        print("[APNs] Registered with token: \(tokenString)")
    }

    /// Called when remote notification registration fails.
    func application(
        _ application: UIApplication,
        didFailToRegisterForRemoteNotificationsWithError error: Error
    ) {
        print("[APNs] Registration failed: \(error.localizedDescription)")
    }

    /// Called when a push notification arrives while the app is in the foreground.
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        // Show banner + sound even when app is in the foreground
        completionHandler([.banner, .sound, .badge])
    }

    /// Called when the user taps on a push notification.
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        let userInfo = response.notification.request.content.userInfo
        // Route based on notification payload, e.g.:
        //   ["type": "appointment", "id": "uuid-here"]
        if let type = userInfo["type"] as? String {
            print("[Notification] Tapped: \(type)")
        }
        completionHandler()
    }

    // MARK: - Firebase Messaging Delegate

    /// Called when Firebase generates or refreshes the registration token.
    /// - Parameters:
    ///   - messaging: The Firebase Messaging instance.
    ///   - fcmToken: The new or refreshed FCM token.
    func messaging(_ messaging: Messaging, didReceiveRegistrationToken fcmToken: String?) {
        guard let token = fcmToken else { return }
        print("[FCM] Registration token: \(token)")

        // In production: send token to backend for device targeting
        // let container = AppContainer.shared
        // Task { try? await container.authRepository.updatePushToken(token) }
    }

    // MARK: - Custom URL Schemes & Deep Links

    /// Handles incoming custom URL schemes (e.g., `nexus://reset-password?token=abc`).
    func application(
        _ app: UIApplication,
        open url: URL,
        options: [UIApplication.OpenURLOptionsKey: Any] = [:]
    ) -> Bool {
        handleDeepLink(url)
        return true
    }

    /// Handles Universal Links (Associated Domains).
    func application(
        _ application: UIApplication,
        continue userActivity: NSUserActivity,
        restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void
    ) -> Bool {
        guard userActivity.activityType == NSUserActivityTypeBrowsingWeb,
              let incomingURL = userActivity.webpageURL
        else { return false }

        handleDeepLink(incomingURL)
        return true
    }

    // MARK: - Private Helpers

    private func registerForPushNotifications(_ application: UIApplication) {
        let center = UNUserNotificationCenter.current()
        center.delegate = self  // Handle foreground notifications
        center.requestAuthorization(options: [.alert, .sound, .badge]) { granted, _ in
            guard granted else {
                print("[APNs] Permission denied")
                return
            }
            DispatchQueue.main.async {
                application.registerForRemoteNotifications()
            }
        }
    }

    private func handleDeepLink(_ url: URL) {
        print("[DeepLink] Received: \(url.absoluteString)")

        guard let route = DeepLinkRoute(url: url) else {
            print("[DeepLink] Failed to parse: \(url.absoluteString)")
            return
        }

        // ── Exhaustive pattern match ──────────────────────
        // Every case is explicit. Adding a new case to DeepLinkRoute
        // forces the compiler to flag this switch as non-exhaustive.
        switch route {
        case .resetPassword(let token):
            // Post notification or update state machine to show reset-password flow
            print("[DeepLink] Reset password token: \(token)")

        case .magicLink(let email):
            print("[DeepLink] Magic link for: \(email)")

        case .appointment(let id):
            print("[DeepLink] Navigate to appointment: \(id)")

        case .unknown(let host):
            print("[DeepLink] Unhandled host: \(host ?? "nil")")
        }
    }
}
#endif
