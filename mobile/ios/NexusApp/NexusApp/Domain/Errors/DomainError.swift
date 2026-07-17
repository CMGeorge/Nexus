import Foundation

enum DomainError: LocalizedError, Equatable {
    case invalidCredentials
    case unauthorized
    case notFound
    case conflict(String)
    case networkError(String)
    case unknown

    var errorDescription: String? {
        switch self {
        case .invalidCredentials: "Invalid email or password"
        case .unauthorized: "Session expired. Please log in again"
        case .notFound: "Resource not found"
        case .conflict(let msg): msg
        case .networkError(let msg): msg
        case .unknown: "An unexpected error occurred"
        }
    }
}