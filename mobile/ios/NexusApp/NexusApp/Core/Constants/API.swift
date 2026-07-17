import Foundation

enum APIConstants {
    static let baseURL = URL(string: ProcessInfo.processInfo.environment["API_BASE_URL"] ?? "https://api.nexus.local")!
    static let apiVersion = "v1"
    static let apiPrefix = "/api/\(apiVersion)"
}
