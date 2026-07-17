import Foundation
import Testing
@testable import NexusApp

struct LoginUseCaseTests {

    @Test("Login succeeds with valid credentials")
    func loginSucceeds() async throws {
        let mockRepo = MockAuthRepository()
        let sut = LoginUseCaseImpl(authRepository: mockRepo)
        let user = try await sut.execute(email: "test@test.com", password: "password")
        #expect(user.email == "test@test.com")
    }

    @Test("Login fails with empty email")
    func loginFailsWithEmptyEmail() async {
        let mockRepo = MockAuthRepository()
        let sut = LoginUseCaseImpl(authRepository: mockRepo)
        await #expect(throws: DomainError.invalidCredentials) {
            _ = try await sut.execute(email: "", password: "password")
        }
    }

    @Test("Login fails with empty password")
    func loginFailsWithEmptyPassword() async {
        let mockRepo = MockAuthRepository()
        let sut = LoginUseCaseImpl(authRepository: mockRepo)
        await #expect(throws: DomainError.invalidCredentials) {
            _ = try await sut.execute(email: "test@test.com", password: "")
        }
    }
}

private final class MockAuthRepository: AuthRepository {
    func login(email: String, password: String) async throws -> (user: User, tokens: AuthTokens) {
        guard !email.isEmpty, !password.isEmpty else { throw DomainError.invalidCredentials }
        let user = User(id: UUID(), email: email, firstName: "Test", lastName: "User", tenantId: UUID(), role: .admin, isMfaEnabled: false)
        return (user, AuthTokens(accessToken: "at", refreshToken: "rt", expiresIn: 900))
    }
    func register(email: String, password: String, firstName: String?, lastName: String?, tenantName: String) async throws -> User {
        User(id: UUID(), email: email, firstName: firstName ?? "", lastName: lastName ?? "", tenantId: UUID(), role: .admin, isMfaEnabled: false)
    }
    func refreshToken(_ t: String) async throws -> AuthTokens { AuthTokens(accessToken: "at", refreshToken: "rt", expiresIn: 900) }
    func logout(refreshToken: String) async throws {}
    func setupMFA() async throws -> MFASetup { MFASetup(secret: "s", qrCodeURL: "url", backupCodes: ["c"], tempToken: "t") }
    func verifyMFA(code: String, tempToken: String) async throws -> (user: User, tokens: AuthTokens) {
        let user = User(id: UUID(), email: "t@t.com", firstName: "T", lastName: "U", tenantId: UUID(), role: .admin, isMfaEnabled: true)
        return (user, AuthTokens(accessToken: "at", refreshToken: "rt", expiresIn: 900))
    }
}