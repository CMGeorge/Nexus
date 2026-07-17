import Foundation

/// Logs API requests, responses, and errors for debugging and monitoring.
/// All logs are stored in memory and accessible via `entries` for UI display.
@Observable
final class APILogger: @unchecked Sendable {
    static let shared = APILogger()

    /// A single API log entry.
    struct Entry: Identifiable, Sendable {
        let id = UUID()
        let timestamp: Date
        let method: String
        let path: String
        let statusCode: Int?
        let duration: TimeInterval
        let success: Bool
        let error: String?

        var formattedDuration: String {
            if duration < 1 { return "\((duration * 1000).rounded())ms" }
            return "\(duration.rounded(to: 2))s"
        }

        var formattedTimestamp: String {
            timestamp.formatted(date: .omitted, time: .standard)
        }
    }

    private(set) var entries: [Entry] = []
    private let maxEntries = 100

    private init() {}

    func log(
        method: String,
        path: String,
        statusCode: Int?,
        duration: TimeInterval,
        success: Bool,
        error: String? = nil
    ) {
        let entry = Entry(
            timestamp: Date(),
            method: method,
            path: path,
            statusCode: statusCode,
            duration: duration,
            success: success,
            error: error
        )
        entries.insert(entry, at: 0)
        if entries.count > maxEntries {
            entries = Array(entries.prefix(maxEntries))
        }
        #if DEBUG
        let status = statusCode.map { "\($0)" } ?? "???"
        let icon = success ? "✅" : "❌"
        print("\(icon) [\(method)] \(path) → \(status) (\(entry.formattedDuration))")
        if let error { print("   Error: \(error)") }
        #endif
    }

    func clear() { entries.removeAll() }
}

private extension Double {
    func rounded(to places: Int) -> Double {
        let divisor = pow(10.0, Double(places))
        return (self * divisor).rounded() / divisor
    }
}