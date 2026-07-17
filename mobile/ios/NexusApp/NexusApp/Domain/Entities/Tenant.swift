import Foundation

struct Tenant: Identifiable, Sendable, Hashable {
    let id: UUID
    let name: String
    let subdomain: String?
    let isInstitution: Bool
    let parentId: UUID?
    let isActive: Bool
}
