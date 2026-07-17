import Foundation
import Testing
@testable import NexusApp

struct NexusAppCoreTests {

    @Test("AppContainer initializes all dependencies")
    @MainActor
    func appContainerInitializesCorrectly() {
        let container = AppContainer.shared
        #expect(container.loginUseCase is LoginUseCaseImpl)
        #expect(container.customerRepository is CustomerRepository)
    }

    @Test("DomainError provides localized descriptions")
    func domainErrorDescriptions() {
        #expect(DomainError.invalidCredentials.errorDescription != nil)
        #expect(DomainError.unauthorized.errorDescription != nil)
        #expect(DomainError.notFound.errorDescription == "Resource not found")
        #expect(DomainError.conflict("Test").errorDescription == "Test")
        #expect(DomainError.networkError("Down").errorDescription == "Down")
    }

    @Test("User entity initializes correctly")
    func userEntityInitialization() {
        let user = User(
            id: UUID(), email: "test@example.com",
            firstName: "Ion", lastName: "Popescu",
            tenantId: UUID(), role: .admin, isMfaEnabled: true
        )
        #expect(user.email == "test@example.com")
        #expect(user.role == .admin)
        #expect(user.isMfaEnabled == true)
    }

    @Test("Customer entity fullName computed property")
    func customerFullName() {
        let customer = Customer(
            id: UUID(), tenantId: UUID(),
            firstName: "Ana", lastName: "Maria",
            email: nil, phone: nil,
            addressLine1: nil, addressLine2: nil,
            city: nil, county: nil, postalCode: nil, country: nil,
            isActive: true, createdAt: .now, updatedAt: .now
        )
        #expect(customer.fullName == "Ana Maria")
    }
}
