import Foundation

protocol CustomerRepositoryProtocol: Sendable {
    func fetchCustomers(tenantId: UUID, search: String?, limit: Int) async throws -> [Customer]
    func fetchCustomer(id: UUID, tenantId: UUID) async throws -> Customer
    func createCustomer(_ customer: Customer, tenantId: UUID) async throws -> Customer
    func updateCustomer(id: UUID, data: CustomerUpdateData, tenantId: UUID) async throws -> Customer
    func deleteCustomer(id: UUID, tenantId: UUID) async throws
}

struct CustomerUpdateData: Sendable {
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
}