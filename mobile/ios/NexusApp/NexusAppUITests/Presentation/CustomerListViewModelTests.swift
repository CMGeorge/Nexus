import Testing
@testable import NexusApp
import Foundation

@MainActor
struct CustomerListViewModelTests {

    @Test("Load customers populates list on success")
    func loadCustomersSucceeds() async throws {
        let repo = MockCustomerRepository()
        let tenantId = UUID()
        let sut = CustomerListViewModel(repository: repo, tenantId: tenantId)

        await sut.loadCustomers()

        #expect(sut.customers.count == 2)
        #expect(sut.customers[0].firstName == "Ion")
        #expect(sut.customers[1].firstName == "Maria")
        #expect(sut.errorMessage == nil)
    }

    @Test("Load customers sets error on failure")
    func loadCustomersFails() async throws {
        let repo = FailingCustomerRepository()
        let sut = CustomerListViewModel(repository: repo, tenantId: UUID())

        await sut.loadCustomers()

        #expect(sut.customers.isEmpty)
        #expect(sut.errorMessage != nil)
    }

    @Test("Search filters trigger reload")
    func searchTriggersReload() async throws {
        let repo = MockCustomerRepository()
        let sut = CustomerListViewModel(repository: repo, tenantId: UUID())

        sut.searchText = "Ion"
        await sut.loadCustomers()

        #expect(sut.customers.count == 2)
    }
}

// MARK: - Mocks
private final class MockCustomerRepository: CustomerRepositoryProtocol {
    func fetchCustomers(tenantId: UUID, search: String?, limit: Int) async throws -> [Customer] {
        [
            Customer(id: UUID(), tenantId: tenantId, firstName: "Ion", lastName: "Popescu",
                     email: "ion@test.com", phone: nil, addressLine1: nil, addressLine2: nil,
                     city: "Bucuresti", county: nil, postalCode: nil, country: "RO",
                     isActive: true, createdAt: .now, updatedAt: .now),
            Customer(id: UUID(), tenantId: tenantId, firstName: "Maria", lastName: "Ionescu",
                     email: "maria@test.com", phone: nil, addressLine1: nil, addressLine2: nil,
                     city: "Cluj", county: nil, postalCode: nil, country: "RO",
                     isActive: true, createdAt: .now, updatedAt: .now),
        ]
    }

    func fetchCustomer(id: UUID, tenantId: UUID) async throws -> Customer {
        Customer(id: id, tenantId: tenantId, firstName: "Test", lastName: "User",
                 email: nil, phone: nil, addressLine1: nil, addressLine2: nil,
                 city: nil, county: nil, postalCode: nil, country: "RO",
                 isActive: true, createdAt: .now, updatedAt: .now)
    }

    func createCustomer(_ customer: Customer, tenantId: UUID) async throws -> Customer { customer }
    func updateCustomer(id: UUID, data: CustomerUpdateData, tenantId: UUID) async throws -> Customer {
        Customer(id: id, tenantId: tenantId, firstName: "Updated", lastName: "User",
                 email: nil, phone: nil, addressLine1: nil, addressLine2: nil,
                 city: nil, county: nil, postalCode: nil, country: "RO",
                 isActive: true, createdAt: .now, updatedAt: .now)
    }
    func deleteCustomer(id: UUID, tenantId: UUID) async throws {}
}

private final class FailingCustomerRepository: CustomerRepositoryProtocol {
    func fetchCustomers(tenantId: UUID, search: String?, limit: Int) async throws -> [Customer] {
        throw DomainError.networkError(NSError(domain: "test", code: -1))
    }
    func fetchCustomer(id: UUID, tenantId: UUID) async throws -> Customer {
        throw DomainError.networkError(NSError(domain: "test", code: -1))
    }
    func createCustomer(_ customer: Customer, tenantId: UUID) async throws -> Customer { customer }
    func updateCustomer(id: UUID, data: CustomerUpdateData, tenantId: UUID) async throws -> Customer {
        throw DomainError.networkError(NSError(domain: "test", code: -1))
    }
    func deleteCustomer(id: UUID, tenantId: UUID) async throws {}
}