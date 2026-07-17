import Foundation

struct LoginResponseDTO: Decodable, Sendable {
    let user: UserDTO
    let tokens: TokensDTO
}

struct UserDTO: Decodable, Sendable {
    let id: UUID
    let email: String
    let firstName: String
    let lastName: String
    let tenantId: UUID
    let role: String
    let isMfaEnabled: Bool
}

struct TokensDTO: Decodable, Sendable {
    let accessToken: String
    let refreshToken: String
    let expiresIn: Int
}

struct ErrorResponseDTO: Decodable, Sendable {
    let detail: String
}
