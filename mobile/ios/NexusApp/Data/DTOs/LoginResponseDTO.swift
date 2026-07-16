import Foundation

struct LoginResponseDTO: Decodable {
    let user: UserDTO
    let tokens: TokensDTO
}

struct UserDTO: Decodable {
    let id: UUID
    let email: String
    let firstName: String
    let lastName: String
    let tenantId: UUID
    let role: String
    let isMfaEnabled: Bool
}

struct TokensDTO: Decodable {
    let accessToken: String
    let refreshToken: String
    let expiresIn: Int
}

struct ErrorResponseDTO: Decodable {
    let detail: String
}
