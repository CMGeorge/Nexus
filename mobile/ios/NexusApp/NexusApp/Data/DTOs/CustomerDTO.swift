import Foundation

struct CustomerDTO: Codable, Sendable {
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
    let createdAt: String
    let updatedAt: String
}

extension CustomerDTO {
    func toDomain() -> Customer {
        let isoFormatter = ISO8601DateFormatter()
        return Customer(
            id: id,
            tenantId: tenantId,
            firstName: firstName,
            lastName: lastName,
            email: email,
            phone: phone,
            addressLine1: addressLine1,
            addressLine2: addressLine2,
            city: city,
            county: county,
            postalCode: postalCode,
            country: country,
            isActive: isActive,
            createdAt: isoFormatter.date(from: createdAt) ?? .now,
            updatedAt: isoFormatter.date(from: updatedAt) ?? .now
        )
    }
}

struct CustomerCreateDTO: Codable, Sendable {
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
}

struct CustomerUpdateDTO: Codable, Sendable {
    var firstName: String?
    var lastName: String?
    var email: String?
    var phone: String?
    var addressLine1: String?
    var addressLine2: String?
    var city: String?
    var county: String?
    var postalCode: String?
    var country: String?

    init(from data: CustomerUpdateData) {
        self.firstName = data.firstName
        self.lastName = data.lastName
        self.email = data.email
        self.phone = data.phone
        self.addressLine1 = data.addressLine1
        self.addressLine2 = data.addressLine2
        self.city = data.city
        self.county = data.county
        self.postalCode = data.postalCode
        self.country = data.country
    }
}

struct CustomerListResponseDTO: Codable, Sendable {
    let data: [CustomerDTO]
    let cursor: CursorDTO?
}

struct CursorDTO: Codable, Sendable {
    let next: String?
    let hasMore: Bool
}