import Foundation

struct Customer: Identifiable, Sendable, Hashable {
    let id: UUID
    let tenantId: UUID
    let firstName: String
    let lastName: String
    let email: String?
    let phone: String?
    let addressLine1: String?
    let addressLine2: String?
    let city: String?
    let county: String?
    let postalCode: String?
    let country: String?
    let isActive: Bool
    let createdAt: Date
    let updatedAt: Date

    var fullName: String { "\(firstName) \(lastName)" }
    var fullAddress: String {
        [addressLine1, addressLine2, city, county]
            .compactMap { $0 }
            .filter { !$0.isEmpty }
            .joined(separator: ", ")
    }
}