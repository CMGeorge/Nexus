import Testing
@testable import NexusApp
import Foundation

struct CustomerDTOTests {

    @Test("CustomerDTO maps to Customer domain model correctly")
    func dtoToDomainMapping() async throws {
        let id = UUID()
        let tenantId = UUID()
        let now = ISO8601DateFormatter().string(from: Date())
        let dto = CustomerDTO(
            id: id, tenantId: tenantId,
            firstName: "Ion", lastName: "Popescu",
            email: "ion@test.com", phone: "+40722123456",
            addressLine1: "Str. Principala 42", addressLine2: nil,
            city: "Brasov", county: "Brasov", postalCode: "500001", country: "RO",
            isActive: true, createdAt: now, updatedAt: now
        )
        let domain = dto.toDomain()
        #expect(domain.id == id)
        #expect(domain.firstName == "Ion")
        #expect(domain.city == "Brasov")
        #expect(domain.isActive == true)
        #expect(domain.fullName == "Ion Popescu")
    }

    @Test("Customer full address combines non-nil fields")
    func fullAddressCombinesFields() async throws {
        let customer = Customer(
            id: UUID(), tenantId: UUID(), firstName: "Test", lastName: "User",
            email: nil, phone: nil, addressLine1: "Str. A", addressLine2: "Ap. 1",
            city: "Bucuresti", county: "Sector 1", postalCode: "010001", country: "RO",
            isActive: true, createdAt: .now, updatedAt: .now
        )
        let address = customer.fullAddress
        #expect(address.contains("Str. A"))
        #expect(address.contains("Bucuresti"))
    }
}