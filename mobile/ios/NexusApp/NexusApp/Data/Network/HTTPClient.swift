import Foundation

protocol HTTPClient: Sendable {
    func request<T: Decodable>(_ endpoint: APIEndpoint, responseType: T.Type) async throws -> T
    func request(_ endpoint: APIEndpoint) async throws
    func checkHealth() async -> APIHealthStatus
}

struct APIHealthStatus: Sendable, Equatable {
    let isReachable: Bool
    let statusCode: Int?
    let responseTime: TimeInterval
    let error: String?

    static let unreachable = APIHealthStatus(
        isReachable: false, statusCode: nil, responseTime: 0, error: "No connection"
    )

    var icon: String {
        if !isReachable { return "🔴" }
        if responseTime < 0.5 { return "🟢" }
        if responseTime < 2 { return "🟡" }
        return "🟠"
    }

    var label: String {
        if !isReachable { return "Disconnected" }
        return "Connected (\((responseTime * 1000).rounded())ms)"
    }
}
