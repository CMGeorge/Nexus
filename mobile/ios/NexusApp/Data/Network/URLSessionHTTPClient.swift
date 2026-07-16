import Foundation

final class URLSessionHTTPClient: HTTPClient {
    private let session: URLSession
    private let baseURL: URL
    private let authInterceptor: AuthInterceptor
    private let tenantInterceptor: TenantHeaderInterceptor
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder

    init(baseURL: URL, authInterceptor: AuthInterceptor, tenantInterceptor: TenantHeaderInterceptor, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.authInterceptor = authInterceptor
        self.tenantInterceptor = tenantInterceptor
        self.session = session
        self.decoder = JSONDecoder()
        self.decoder.keyDecodingStrategy = .convertFromSnakeCase
        self.encoder = JSONEncoder()
        self.encoder.keyEncodingStrategy = .convertToSnakeCase
    }

    func request<T: Decodable>(_ endpoint: APIEndpoint, responseType: T.Type) async throws -> T {
        var request = try buildRequest(for: endpoint)
        if endpoint.requiresAuth { try await authInterceptor.intercept(&request) }
        if endpoint.requiresTenant { try await tenantInterceptor.intercept(&request) }
        let (data, response) = try await session.data(for: request)
        try validateResponse(response, data: data)
        return try decoder.decode(T.self, from: data)
    }

    func request(_ endpoint: APIEndpoint) async throws {
        var request = try buildRequest(for: endpoint)
        if endpoint.requiresAuth { try await authInterceptor.intercept(&request) }
        if endpoint.requiresTenant { try await tenantInterceptor.intercept(&request) }
        let (data, response) = try await session.data(for: request)
        try validateResponse(response, data: data)
    }

    private func buildRequest(for endpoint: APIEndpoint) throws -> URLRequest {
        let url = baseURL.appendingPathComponent(endpoint.path)
        var request = URLRequest(url: url)
        request.httpMethod = endpoint.method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if let body = endpoint.body {
            request.httpBody = try encoder.encode(AnyEncodable(body))
        }
        return request
    }

    private func validateResponse(_ response: URLResponse, data: Data) throws {
        guard let httpResponse = response as? HTTPURLResponse else {
            throw DomainError.networkError("Invalid response")
        }
        switch httpResponse.statusCode {
        case 200...299: return
        case 401: throw DomainError.unauthorized
        case 404: throw DomainError.notFound
        case 409:
            struct ErrDetail: Decodable { let detail: String }
            let detail = (try? JSONDecoder().decode(ErrDetail.self, from: data))?.detail ?? "Conflict"
            throw DomainError.conflict(detail)
        default:
            throw DomainError.networkError("HTTP \(httpResponse.statusCode)")
        }
    }
}

private struct AnyEncodable: Encodable {
    private let _encode: (Encoder) throws -> Void
    init(_ wrapped: any Encodable) { self._encode = wrapped.encode }
    func encode(to encoder: Encoder) throws { try _encode(encoder) }
}