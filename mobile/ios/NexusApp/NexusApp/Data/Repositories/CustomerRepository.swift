import Foundation

final class CustomerRepository: CustomerRepositoryProtocol, Sendable {
    private let httpClient: HTTPClient
    private let tenantInterceptor: TenantHeaderInterceptor

    init(httpClient: HTTPClient, tenantInterceptor: TenantHeaderInterceptor) {
        self.httpClient = httpClient
        self.tenantInterceptor = tenantInterceptor
    }

    func fetchCustomers(tenantId: UUID, search: String?, limit: Int) async throws -> [Customer] {
        var path = "api/v1/customers?limit=\(limit)"
        if let search, !search.isEmpty {
            path += "&search=\(search.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? search)"
        }
        let endpoint = APIEndpoint(path: path, method: .get, requiresTenant: true)
        let response: CustomerListResponseDTO = try await httpClient.request(endpoint, responseType: CustomerListResponseDTO.self)
        return response.data.map { $0.toDomain() }
    }

    func fetchCustomer(id: UUID, tenantId: UUID) async throws -> Customer {
        let endpoint = APIEndpoint(path: "api/v1/customers/\(id.uuidString)", method: .get, requiresTenant: true)
        let dto: CustomerDTO = try await httpClient.request(endpoint, responseType: CustomerDTO.self)
        return dto.toDomain()
    }

    func createCustomer(_ customer: Customer, tenantId: UUID) async throws -> Customer {
        let body = CustomerCreateDTO(
            firstName: customer.firstName,
            lastName: customer.lastName,
            email: customer.email,
            phone: customer.phone,
            addressLine1: customer.addressLine1,
            addressLine2: customer.addressLine2,
            city: customer.city,
            county: customer.county,
            postalCode: customer.postalCode,
            country: customer.country
        )
        let endpoint = APIEndpoint(path: "api/v1/customers", method: .post, body: body, requiresTenant: true)
        let dto: CustomerDTO = try await httpClient.request(endpoint, responseType: CustomerDTO.self)
        return dto.toDomain()
    }

    func updateCustomer(id: UUID, data: CustomerUpdateData, tenantId: UUID) async throws -> Customer {
        let body = CustomerUpdateDTO(from: data)
        let endpoint = APIEndpoint(path: "api/v1/customers/\(id.uuidString)", method: .patch, body: body, requiresTenant: true)
        let dto: CustomerDTO = try await httpClient.request(endpoint, responseType: CustomerDTO.self)
        return dto.toDomain()
    }

    func deleteCustomer(id: UUID, tenantId: UUID) async throws {
        let endpoint = APIEndpoint(path: "api/v1/customers/\(id.uuidString)", method: .delete, requiresTenant: true)
        let _: EmptyResponseDTO = try await httpClient.request(endpoint, responseType: EmptyResponseDTO.self)
    }
}

private struct EmptyResponseDTO: Decodable, Sendable {}