import Foundation

protocol AuthRepository: Sendable {
    func login(email: String, password: String) async throws -> (User, AuthTokens)
    func register(email: String, password: String, firstName: String, lastName: String, tenantName: String) async throws -> User
    func refreshToken(_ refreshToken: String) async throws -> AuthTokens
    func logout(refreshToken: String) async throws
    func setupMFA() async throws -> MFASetup
    func verifyMFA(code: String, tempToken: String) async throws -> (User, AuthTokens)
}

struct AuthTokens: Sendable, Codable {
    let accessToken: String
    let refreshToken: String
    let expiresIn: Int
}

struct MFASetup: Sendable, Codable {
    let secret: String
    let qrCodeURL: String
    let backupCodes: [String]
    let tempToken: String
}