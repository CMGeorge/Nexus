import Testing
@testable import NexusApp
import Foundation

@MainActor
struct CustomerListViewModelTests {

    @Test("Load customers populates list on success")
    func loadCustomersSucceeds() async throws {
        let repo = MockCustomerRepository()
        let sut = CustomerListViewModel(repository: repo, tenantId: UUID())
        await sut.loadCustomers()
        #expect(sut.customers.count == 2)
        #expect(sut.customers[0].firstName == "Ion")
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
}

private final class MockCustomerRepository: CustomerRepositoryProtocol {
    func fetchCustomers(tenantId: UUID, search: String?, limit: Int) async throws -> [Customer] {
        [
            Customer(id: UUID(), tenantId: tenantId, firstName: "Ion", lastName: "Popescu", email: nil, phone: nil, addressLine1: nil, addressLine2: nil, city: nil, county: nil, postalCode: nil, country: "RO", isActive: true, createdAt: .now, updatedAt: .now),
            Customer(id: UUID(), tenantId: tenantId, firstName: "Maria", lastName: "Ionescu", email: nil, phone: nil, addressLine1: nil, addressLine2: nil, city: nil, county: nil, postalCode: nil, country: "RO", isActive: true, createdAt: .now, updatedAt: .now),
        ]
    }
    func fetchCustomer(id: UUID, tenantId: UUID) async throws -> Customer { throw DomainError.notFound }
    func createCustomer(_ c: Customer, tenantId: UUID) async throws -> Customer { c }
    func updateCustomer(id: UUID, data: CustomerUpdateData, tenantId: UUID) async throws -> Customer { throw DomainError.notFound }
    func deleteCustomer(id: UUID, tenantId: UUID) async throws {}
}

private final class FailingCustomerRepository: CustomerRepositoryProtocol {
    func fetchCustomers(tenantId: UUID, search: String?, limit: Int) async throws -> [Customer] {
        throw DomainError.networkError("Connection failed")
    }
    func fetchCustomer(id: UUID, tenantId: UUID) async throws -> Customer { throw DomainError.notFound }
    func createCustomer(_ c: Customer, tenantId: UUID) async throws -> Customer { c }
    func updateCustomer(id: UUID, data: CustomerUpdateData, tenantId: UUID) async throws -> Customer { throw DomainError.notFound }
    func deleteCustomer(id: UUID, tenantId: UUID) async throws {}
}