import Foundation

final class AuthRepositoryImpl: AuthRepository {
    private let httpClient: HTTPClient
    private let authInterceptor: AuthInterceptor
    private let tenantInterceptor: TenantHeaderInterceptor

    init(
        httpClient: HTTPClient,
        authInterceptor: AuthInterceptor,
        tenantInterceptor: TenantHeaderInterceptor
    ) {
        self.httpClient = httpClient
        self.authInterceptor = authInterceptor
        self.tenantInterceptor = tenantInterceptor
    }

    func login(email: String, password: String) async throws -> (user: User, tokens: AuthTokens) {
        let endpoint = APIEndpoint(
            path: "api/v1/auth/login",
            method: .post,
            body: AuthLoginRequestDTO(email: email, password: password),
            requiresAuth: false,
            requiresTenant: true
        )
        let response: AuthLoginResponseDTO = try await httpClient.request(endpoint, responseType: AuthLoginResponseDTO.self)
        let tokens = AuthTokens(accessToken: response.tokens.accessToken, refreshToken: response.tokens.refreshToken, expiresIn: response.tokens.expiresIn)
        await authInterceptor.storeTokens(access: tokens.accessToken, refresh: tokens.refreshToken)
        let user = User(
            id: response.user.id, email: response.user.email,
            firstName: response.user.firstName, lastName: response.user.lastName,
            tenantId: response.user.tenantId, role: UserRole(rawValue: response.user.role) ?? .customer,
            isMfaEnabled: response.user.isMfaEnabled
        )
        return (user, tokens)
    }

    func register(email: String, password: String, firstName: String?, lastName: String?, tenantName: String) async throws -> User {
        let endpoint = APIEndpoint(
            path: "api/v1/auth/register",
            method: .post,
            body: AuthRegisterRequestDTO(email: email, password: password, firstName: firstName, lastName: lastName, tenantName: tenantName),
            requiresAuth: false,
            requiresTenant: false
        )
        let response: AuthUserDTO = try await httpClient.request(endpoint, responseType: AuthUserDTO.self)
        return mapUser(response)
    }

    func refreshToken(_ refreshToken: String) async throws -> AuthTokens {
        let endpoint = APIEndpoint(
            path: "api/v1/auth/refresh",
            method: .post,
            body: AuthRefreshRequestDTO(refreshToken: refreshToken),
            requiresAuth: false
        )
        let response: AuthTokensDTO = try await httpClient.request(endpoint, responseType: AuthTokensDTO.self)
        let tokens = AuthTokens(accessToken: response.accessToken, refreshToken: response.refreshToken, expiresIn: response.expiresIn)
        await authInterceptor.storeTokens(access: tokens.accessToken, refresh: tokens.refreshToken)
        return tokens
    }

    func logout(refreshToken: String) async throws {
        let endpoint = APIEndpoint(
            path: "api/v1/auth/logout",
            method: .post,
            body: AuthRefreshRequestDTO(refreshToken: refreshToken),
            requiresAuth: true
        )
        let _: AuthEmptyResponse = try await httpClient.request(endpoint, responseType: AuthEmptyResponse.self)
        await authInterceptor.clearTokens()
    }

    func setupMFA() async throws -> MFASetup {
        let endpoint = APIEndpoint(path: "api/v1/auth/mfa/setup", method: .post)
        let response: AuthMFASetupDTO = try await httpClient.request(endpoint, responseType: AuthMFASetupDTO.self)
        return MFASetup(secret: response.secret, qrCodeURL: response.qrCodeUrl, backupCodes: response.backupCodes, tempToken: response.tempToken)
    }

    func verifyMFA(code: String, tempToken: String) async throws -> (user: User, tokens: AuthTokens) {
        let endpoint = APIEndpoint(
            path: "api/v1/auth/mfa/verify",
            method: .post,
            body: AuthMFAVerifyDTO(code: code, tempToken: tempToken)
        )
        let response: AuthLoginResponseDTO = try await httpClient.request(endpoint, responseType: AuthLoginResponseDTO.self)
        let tokens = AuthTokens(accessToken: response.tokens.accessToken, refreshToken: response.tokens.refreshToken, expiresIn: response.tokens.expiresIn)
        await authInterceptor.storeTokens(access: tokens.accessToken, refresh: tokens.refreshToken)
        let user = User(
            id: response.user.id, email: response.user.email,
            firstName: response.user.firstName, lastName: response.user.lastName,
            tenantId: response.user.tenantId, role: UserRole(rawValue: response.user.role) ?? .customer,
            isMfaEnabled: response.user.isMfaEnabled
        )
        return (user, tokens)
    }

    private func mapUser(_ dto: AuthUserDTO) -> User {
        User(id: dto.id, email: dto.email, firstName: dto.firstName, lastName: dto.lastName, tenantId: dto.tenantId, role: UserRole(rawValue: dto.role) ?? .customer, isMfaEnabled: dto.isMfaEnabled)
    }
}

// MARK: - Private DTOs (prefixed to avoid module-level conflicts)
private struct AuthLoginRequestDTO: Encodable { let email: String; let password: String }
private struct AuthRegisterRequestDTO: Encodable {
    let email: String; let password: String
    let firstName: String?; let lastName: String?; let tenantName: String
    enum CodingKeys: String, CodingKey {
        case email, password; case firstName = "first_name"; case lastName = "last_name"; case tenantName = "tenant_name"
    }
}
private struct AuthRefreshRequestDTO: Encodable {
    let refreshToken: String
    enum CodingKeys: String, CodingKey { case refreshToken = "refresh_token" }
}
private struct AuthMFASetupDTO: Decodable, Sendable {
    let secret: String; let qrCodeUrl: String; let backupCodes: [String]; let tempToken: String
}
private struct AuthMFAVerifyDTO: Encodable, Sendable {
    let code: String; let tempToken: String
    enum CodingKeys: String, CodingKey { case code; case tempToken = "temp_token" }
}
private struct AuthUserDTO: Decodable, Sendable {
    let id: UUID; let email: String; let firstName: String; let lastName: String
    let tenantId: UUID; let role: String; let isMfaEnabled: Bool
    enum CodingKeys: String, CodingKey {
        case id, email, role; case firstName = "first_name"; case lastName = "last_name"
        case tenantId = "tenant_id"; case isMfaEnabled = "mfa_enabled"
    }
}
private struct AuthTokensDTO: Decodable, Sendable {
    let accessToken: String; let refreshToken: String; let expiresIn: Int
    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"; case refreshToken = "refresh_token"; case expiresIn = "expires_in"
    }
}
private struct AuthLoginResponseDTO: Decodable, Sendable { let user: AuthUserDTO; let tokens: AuthTokensDTO }
private struct AuthEmptyResponse: Decodable, Sendable {}