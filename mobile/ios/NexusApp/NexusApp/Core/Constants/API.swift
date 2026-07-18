import Foundation

// MARK: - API Configuration

/// Resolves the Nexus API base URL with different behaviour per build configuration:
/// - **Debug**: falls back to `http://localhost:3670`. If we still can't produce a URL,
///   the app logs a warning and shows an on-screen banner — no crash.
/// - **Release**: if the URL is missing or malformed, the app crashes immediately.
///   Production builds MUST have `API_BASE_URL` set in the environment or Info.plist.
enum APIConfiguration {

    /// The resolved base URL. Safe to access at any time.
    /// Use `isConfigured` to check whether it's valid before making network calls.
    static let baseURL: URL = resolveBaseURL()

    /// `true` when the base URL was resolved successfully.
    /// When `false` in Debug builds, the login screen shows a warning banner.
    static let isConfigured: Bool = URLComponents(url: baseURL, resolvingAgainstBaseURL: false) != nil

    /// How the base URL is expected to be provided, shown in warning messages.
    static let expectedKey = "API_BASE_URL"

    // MARK: - Private

    private static func resolveBaseURL() -> URL {
        // 1. Environment variable (Xcode scheme, CI, or `swift run`)
        if let env = ProcessInfo.processInfo.environment[expectedKey],
           let url = URL(string: env) {
            return url
        }

        // 2. Info.plist (via Xcode build settings or manual .plist entry)
        if let plist = Bundle.main.object(forInfoDictionaryKey: expectedKey) as? String,
           let url = URL(string: plist) {
            return url
        }

        // 3. Debug fallback — harmless, devs see a banner
        #if DEBUG
        let baseUrl: String = "http://localhost:3670/"
        print("[API] ⚠️ \(expectedKey) not set. Falling back to \(baseUrl)")
        return URL(string: baseUrl)!
        #else
        // 4. Release — missing URL is a fatal misconfiguration
        fatalError("\(expectedKey) must be set in environment or Info.plist for release builds.")
        #endif
    }
}

// MARK: - Legacy Convenience

/// Convenience constants derived from `APIConfiguration`.
enum APIConstants {
    static var baseURL: URL { APIConfiguration.baseURL }
    static let apiVersion = "v1"
    static let apiPrefix = "/api/\(apiVersion)"
}
