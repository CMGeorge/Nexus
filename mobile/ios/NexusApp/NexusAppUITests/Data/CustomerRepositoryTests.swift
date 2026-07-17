import Testing
@testable import NexusApp
import Foundation

struct CustomerRepositoryTests {

    @Test("CustomerRepository uses HTTPClient for fetch customers")
    func fetchCustomersDelegatesToHTTPClient() async throws {
        let mockClient = MockHTTPClient()
        let tenantInterceptor = TenantHeaderInterceptor()
        let repo = CustomerRepository(httpClient: mockClient, tenantInterceptor: tenantInterceptor)

        let customers = try await repo.fetchCustomers(tenantId: UUID(), search: nil, limit: 20)

        #expect(customers.count == 1)
        #expect(customers[0].firstName == "Test")
        #expect(mockClient.lastEndpoint?.path.contains("api/v1/customers") == true)
    }

    @Test("CustomerRepository delete sends DELETE request")
    func deleteCustomerSendsDeleteRequest() async throws {
        let mockClient = MockHTTPClient()
        let tenantInterceptor = TenantHeaderInterceptor()
        let repo = CustomerRepository(httpClient: mockClient, tenantInterceptor: tenantInterceptor)

        try await repo.deleteCustomer(id: UUID(), tenantId: UUID())

        #expect(mockClient.lastEndpoint?.method == .delete)
    }
}

// MARK: - Mock HTTPClient
private final class MockHTTPClient: HTTPClient {
    var lastEndpoint: APIEndpoint?

    func request<T: Decodable>(_ endpoint: APIEndpoint, responseType: T.Type) async throws -> T {
        lastEndpoint = endpoint
        let json = """
        {"data":[{"id":"\(UUID().uuidString)","tenant_id":"\(UUID().uuidString)","first_name":"Test","last_name":"User","email":null,"phone":null,"address_line1":null,"address_line2":null,"city":null,"county":null,"postal_code":null,"country":"RO","is_active":true,"created_at":"2026-01-01T00:00:00Z","updated_at":"2026-01-01T00:00:00Z"}],"cursor":{"next":null,"has_more":false}}
        """
        let data = json.data(using: .utf8)!
        let decoder = JSONDecoder()
        if T.self == CustomerListResponseDTO.self {
            return try decoder.decode(CustomerListResponseDTO.self, from: data) as! T
        }
        if T.self == EmptyResponseDTO.self {
            struct EmptyResponseDTO: Decodable {}
            return EmptyResponseDTO() as! T
        }
        throw DomainError.unknown
    }
}