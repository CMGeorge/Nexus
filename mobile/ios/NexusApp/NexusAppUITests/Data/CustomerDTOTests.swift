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
            id: id, tenant_id: tenantId,
            first_name: "Ion", last_name: "Popescu",
            email: "ion@test.com", phone: "+40722123456",
            address_line1: "Str. Principala 42", address_line2: nil,
            city: "Brasov", county: "Brasov", postal_code: "500001", country: "RO",
            is_active: true, created_at: now, updated_at: now
        )

        let domain = dto.toDomain()

        #expect(domain.id == id)
        #expect(domain.tenantId == tenantId)
        #expect(domain.firstName == "Ion")
        #expect(domain.lastName == "Popescu")
        #expect(domain.email == "ion@test.com")
        #expect(domain.phone == "+40722123456")
        #expect(domain.city == "Brasov")
        #expect(domain.country == "RO")
        #expect(domain.isActive == true)
        #expect(domain.fullName == "Ion Popescu")
    }

    @Test("CustomerDTO with nil optional fields maps correctly")
    func dtoWithNilOptionals() async throws {
        let dto = CustomerDTO(
            id: UUID(), tenant_id: UUID(),
            first_name: "Ana", last_name: "Maria",
            email: nil, phone: nil,
            address_line1: nil, address_line2: nil,
            city: nil, county: nil, postal_code: nil, country: nil,
            is_active: false,
            created_at: ISO8601DateFormatter().string(from: Date()),
            updated_at: ISO8601DateFormatter().string(from: Date())
        )

        let domain = dto.toDomain()

        #expect(domain.email == nil)
        #expect(domain.phone == nil)
        #expect(domain.city == nil)
        #expect(domain.isActive == false)
    }

    @Test("Customer full address combines non-nil address fields")
    func fullAddressCombinesFields() async throws {
        let customer = Customer(
            id: UUID(), tenantId: UUID(),
            firstName: "Test", lastName: "User",
            email: nil, phone: nil,
            addressLine1: "Str. A", addressLine2: "Ap. 1",
            city: "Bucuresti", county: "Sector 1",
            postalCode: "010001", country: "RO",
            isActive: true, createdAt: .now, updatedAt: .now
        )

        let address = customer.fullAddress
        #expect(address.contains("Str. A"))
        #expect(address.contains("Ap. 1"))
        #expect(address.contains("Bucuresti"))
        #expect(address.contains("Sector 1"))
    }
}