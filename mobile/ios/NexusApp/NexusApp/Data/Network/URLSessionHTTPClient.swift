import Alamofire
import Foundation

final class AlamofireHTTPClient: HTTPClient, Sendable {
    private let baseURL: URL
    private let authInterceptor: AuthInterceptor
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder
    private let logger = APILogger.shared

    init(
        baseURL: URL,
        authInterceptor: AuthInterceptor,
        tenantInterceptor: TenantHeaderInterceptor
    ) {
        self.baseURL = baseURL
        self.authInterceptor = authInterceptor
        self.decoder = JSONDecoder()
        self.decoder.keyDecodingStrategy = .convertFromSnakeCase
        self.encoder = JSONEncoder()
        self.encoder.keyEncodingStrategy = .convertToSnakeCase
    }

    // MARK: - Health Check

    func checkHealth() async -> APIHealthStatus {
        let start = Date()
        do {
            let url = baseURL.appendingPathComponent("health")
            let response = await AF.request(url).serializingData().response
            let duration = Date().timeIntervalSince(start)
            if let httpResponse = response.response {
                logger.log(method: "GET", path: "/health", statusCode: httpResponse.statusCode, duration: duration, success: true)
                return APIHealthStatus(
                    isReachable: true,
                    statusCode: httpResponse.statusCode,
                    responseTime: duration,
                    error: nil
                )
            }
            logger.log(method: "GET", path: "/health", statusCode: nil, duration: duration, success: false, error: "No response")
            return .unreachable
        } catch {
            let duration = Date().timeIntervalSince(start)
            logger.log(method: "GET", path: "/health", statusCode: nil, duration: duration, success: false, error: error.localizedDescription)
            return APIHealthStatus(isReachable: false, statusCode: nil, responseTime: duration, error: error.localizedDescription)
        }
    }

    // MARK: - Typed Request

    func request<T: Decodable>(_ endpoint: APIEndpoint, responseType: T.Type) async throws -> T {
        let start = Date()
        let url = baseURL.appendingPathComponent(endpoint.path)
        let afMethod = Alamofire.HTTPMethod(rawValue: endpoint.method.rawValue)

        var headers: HTTPHeaders = [.contentType("application/json")]
        if endpoint.requiresAuth {
            let token: String = if let existing = await authInterceptor.accessToken { existing } else { try await authInterceptor.refreshAccessToken() }
            headers.add(.authorization(bearerToken: token))
        }

        let dataRequest = AF.request(url, method: afMethod, parameters: nil, headers: headers)
        let response = await dataRequest.validate().serializingDecodable(T.self, decoder: decoder).response
        let duration = Date().timeIntervalSince(start)

        switch response.result {
        case .success(let value):
            let code = response.response?.statusCode ?? 200
            logger.log(method: endpoint.method.rawValue, path: endpoint.path, statusCode: code, duration: duration, success: true)
            return value
        case .failure(let error):
            let code = response.response?.statusCode
            if error.responseCode == 401 {
                logger.log(method: endpoint.method.rawValue, path: endpoint.path, statusCode: 401, duration: duration, success: false, error: "Token expired, refreshing...")
                _ = try? await authInterceptor.refreshAccessToken()
                let retryStart = Date()
                let retryResponse = await AF.request(url, method: afMethod, headers: headers)
                    .validate()
                    .serializingDecodable(T.self, decoder: decoder)
                    .response
                let retryDuration = Date().timeIntervalSince(retryStart)
                switch retryResponse.result {
                case .success(let value):
                    logger.log(method: endpoint.method.rawValue, path: endpoint.path, statusCode: retryResponse.response?.statusCode ?? 200, duration: retryDuration, success: true)
                    return value
                case .failure(let retryError):
                    logger.log(method: endpoint.method.rawValue, path: endpoint.path, statusCode: retryResponse.response?.statusCode, duration: retryDuration, success: false, error: retryError.localizedDescription)
                    throw mapError(retryError)
                }
            }
            logger.log(method: endpoint.method.rawValue, path: endpoint.path, statusCode: code, duration: duration, success: false, error: error.localizedDescription)
            throw mapError(error)
        }
    }

    // MARK: - Void Request

    func request(_ endpoint: APIEndpoint) async throws {
        let start = Date()
        let url = baseURL.appendingPathComponent(endpoint.path)
        let afMethod = Alamofire.HTTPMethod(rawValue: endpoint.method.rawValue)

        var headers: HTTPHeaders = [.contentType("application/json")]
        if endpoint.requiresAuth {
            let token: String = if let existing = await authInterceptor.accessToken { existing } else { try await authInterceptor.refreshAccessToken() }
            headers.add(.authorization(bearerToken: token))
        }

        let response = await AF.request(url, method: afMethod, headers: headers)
            .validate()
            .serializingData()
            .response
        let duration = Date().timeIntervalSince(start)

        if let httpResponse = response.response {
            logger.log(method: endpoint.method.rawValue, path: endpoint.path, statusCode: httpResponse.statusCode, duration: duration, success: true)
        }
        if case .failure(let error) = response.result {
            logger.log(method: endpoint.method.rawValue, path: endpoint.path, statusCode: response.response?.statusCode, duration: duration, success: false, error: error.localizedDescription)
            throw mapError(error)
        }
    }

    // MARK: - Error Mapping

    private func mapError(_ error: AFError) -> Error {
        switch error.responseCode {
        case 401: return DomainError.unauthorized
        case 404: return DomainError.notFound
        case 409: return DomainError.conflict("Conflict")
        default: return DomainError.networkError(error.localizedDescription)
        }
    }
}