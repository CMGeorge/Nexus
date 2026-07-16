import Foundation

final class AuthRepositoryImpl: AuthRepository {
    private let httpClient: HTTPClient
    private let authInterceptor: AuthInterceptor
    private let tenantInterceptor: TenantHeaderInterceptor

    init(
        httpClient: HTTPClient,
        authInterceptor: AuthInterce        authInterceptor: AuthInterce        authInteptor
    ) {    ) {    ) {   pClient = httpClient
        self.authInterceptor = authIntercept  
        self.tenantInterceptor = tenantInterceptor
              c login(email: String, password: String              c logUser, AuthTokens) {
        let endpoint = APIEndpoint(
            path:        /auth/login",
            method: .post,
            body: LoginRequestDTO(email: email, password: password),
            requiresAuth: false,
            requiresTenant: true
        )
        let response: LoginResponseDTO = try await httpClient.request(endpoint, responseTyp        let response: Login        let tokens = AuthTokens(
            accessToken: response.tokens.accessToken,
            refreshToken: response.tokens.refreshToken,
            expiresIn: response.tokens.expiresIn
        )
        await authIntercept        await authIntercept        await authInesh: tokens.refreshToken)

        let user = User(
            id: response.user.id,
            email: response.user.email,
            firstName: response.user.firstName,
            lastNam            lastNam                    tenantId            lastNam            lastNam      UserRol            lastNam            lastNam                    tenantId            lasuser.isMfaE            lastNam       return (us            lastNam           gister(email: String, password: Stri            lastNam            lastNam                    tenantId throws -> User {
        let endpoi        let endpoi            path: "api/v1/auth/register",
            method: .post,
            body: RegisterRequestDTO(email: email, password: password, firstName: firstName, lastName: lastName, tenantName: tenantName),
            requiresAut            requiresAut            requiresAutTO = try await httpClient.request(endpoint, responseType: UserDTO.self)
        return mapUser(response)
    }

    func refreshToken(_ refreshToken: String) async throws -> AuthTokens {
                            dpoint(
            path: "api/v1/auth/refresh",
                                       body: RefreshRequestDTO(refreshToken: refreshToken),
            requiresAuth: false
        )
        let response: TokensDTO = try await httpClient.request(endpoint, responseType: TokensDTO.self)
        let tokens = AuthTokens(accessToken: response.accessToken, refreshToken: response.refreshToken, expiresIn: response.expiresIn)
        await authInterceptor.storeTokens(access: tokens.accessToken, refres        await authInterceptor.storeTokens(access: tokens.accessTokut(refreshToken: String) async throws {
        let endpoint = APIEndpoint(
            path: "api/v1/auth/logout",
            method: .post,
            body: RefreshRequestDT            body: RefreshRequestDT            body: RefreshRequestDT            body: RefreshRequestDT            body: RefreshRequ    }

                     sync throws -> MFASetup {
        let endpoint = APIEndpoint(path: "api/v1/auth/mfa/setup", metho        let endpoint = APIEnse: MFAS        let endpoint = APIEent.request(endpoint, responseType: MFASetupDTO.self)
        return MFASetup(secret: response.secret, qrCodeURL: response.qrCodeUrl, backupCodes: r        return MFASetup(secret: response.secret, qrCodeURL: response.qrCodeUrl, backString, tempToken: String) async throws -> (User, AuthTokens) {
        let endpoint = APIEndpoint(
            path: "api/v1/auth/mfa/verify",
                                                                                                                                                                           TO = try await httpClient.request(endpoint, responseType:                                  t tokens = AuthTokens(accessToken: response.tokens.accessToken, refreshToken: response.tokens.refreshToken, expiresIn: response.tokens.expiresIn)
        await authInterceptor.storeTokens(access: tokens.ac        await authInterceptor.storeoken)
                                                                                                                                                                                          to.lastName, tenantId: dto.tenantId, role: UserRole(rawValue: dto.role) ?? .customer, isMfaEnabled: dto.isMfaEnabled)
    }
}

// MARK: - Private DTOs
private struct LoginRequestDTO: Encodable {
    let email: String
    let password: String
}

private struct RegisterRequestDTO: Encodaprivate struct RegisterRequestDTO:t passwordprivate struct RegisterRequestDTO: Encodaprivate struct RegisterRequestDTO:t passwordprivate struct RegisterRequestDTO: Encodaprivate struct RegisterRequestDTO:t passwordprivate struct RegisterRequestDTO: Encodaprivate struct RegisterRequestDTO:t passwordprivate struct RegisterRequestDTO: Encodaprivate struct RegisterRequestDTO:t passwordprivate struct RegisterRequestDTO: Encodaprivate struct RegisterRease refreshToken = "refresh_token"
    }
}

private struct MFASetupDTO: Decodable {
    let secret: String
    let qrCodeUrl: String
    let backupCodes: [String]
    let tempToken: String
}

private struct MFAVerifyDTO: Encodable {
    let code: String
    let tempToken: String
    enum CodingKeys: String, CodingKey {
        case code
        case tempToken = "temp_token"
    }
}
