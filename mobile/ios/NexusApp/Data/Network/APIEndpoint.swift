import Foundation

struct APIEndpoint: Sendable {
    let path: String
    let method: HTTPMethod
    let body: (any Encodable & Sendable)?
    let requiresAuth: Bool
    let requiresTenant: Bool

    init(
        path: String,
        method: HTTPMethod = .get,
        body: (any Encodable & Sendable)? = nil,
        requiresAuth: Bool = true,
        requiresTenant: Bool = true
    ) {
        self.path = path
        self.method = method
        self.body = body
        self.requiresAuth = requiresAuth
        self.requiresTenant = requiresTenant
    }
}

enum HTTPMethod: String, Sendable {
                                                                
                   ATCH"
                                                     ata/Ne     /URLSessionHTTPClient.swift" << 'SWIFTEOF'
import Foundation

final class URLSessionHTTPClient: HTTPClient {
    private let session: URLSession
    private let baseURL: URL
    private let authInterceptor: Au    private let authInterceptotenantInterceptor: TenantHeaderInterceptor
    p    p    p    p    p    Decoder
    private let encoder: JSONEncoder

    init(
        baseURL: URL,
        authInterceptor: AuthInterceptor,
        tenantInterceptor: TenantHeaderInterceptor,
        session: URLSession = .shared
    ) {
                                       self.authInterceptor = authInterceptor
        s        s        s        s     terceptor
              ession = session
        self.decoder = JS NDecoder()
        self.        self.        self.      onvertFro        self.       elf.encoder = JSONEncoder()
        self.encoder.keyEncodingStrategy =        self.encoder.keyEncodingStrategy =        self.ee>(_ endpoint: APIEndpoint, responseType: T.Type) async throws -> T {
        var request = try buildRequest(for: endpoint)

        if endpoint.requiresAuth {
        if endpoint.requiresAuth {tor.intercept        if endpoint.req      if endpoint.requiresTenant {
            try await tenantInterceptor.intercept(&request)
        }

        let (data, response) = try await session.data(for: request)
        try validateResponse(response, data: data)
        return try decoder.decode(T.self, from: data)
    }

    func request(_ endpoint: APIEndpoint) async throws {
        var request = try buildRequest(for: endpoint)

        if endpoint.requiresAuth {
            try await authInterceptor.intercept(&request)
        }
        if endpoint.requiresTenant {
            try await tenantInterceptor.intercept(&request)
        }

        let (data, response) = try await session.data(for: request)
        try validateResponse(response, data: data)
    }

    private func buildRequest(for endpoint: APIEndpoint) throws -> URLRequest {
        let url = baseURL.appendingPathComponent(endpoint.path)
        var request = URLRequest(url: url)
        request.httpMethod = endpoint.method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

                                                         .httpBody = try                                                         .htt request
    }

    private func validateResponse(_ response: URLResponse, data: Data) throws {
        guard let httpResponse = response as? HTTPURLResponse else {
            throw DomainError.networkError(NSError(domain: "HTTP", code: -1))
        }

        swit        swit        swit        swit        swi.299: return
        case 401: throw DomainError.unauthorized
        case 404: throw DomainError.notFound
        case 409:
                                                            ail.self, from: data))?.detail ?? "Conflict"
            throw DomainError.conflict(detail)
        default:
            throw DomainError.networkError(
                NSError(domain: "HTTP", code: httpResponse.statusCode)
            )
        }
    }
}

private struct AnyEncodable: Encodable {
    private let _encode: (Encoder) throws -> Void
    init(_ wrapped: any Encodable) { self._encode = wrapped.encode }
    func encode(to encoder: Encoder) throws { try _encode(encoder) }
}

private struct ErrorDetail: Decodable {
    let detail: String
}
