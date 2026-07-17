import Foundation

struct User: Identifiable, Sendable {
    let id: UUID
    let email: String
    let firstName: String
    let lastName: String
    let tenantId: UUID
    let role: UserRole
    let isMfaEnabled: Bool
}

enum UserRole: String, Sendable, Codable {
    case admin = "Admin"
    case manager = "Manager"
    case employee = "Employee"
    case customer = "Customer"
}
