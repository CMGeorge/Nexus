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
        do {
            _ = try await sut.execute(email: "", password: "password")
            Issue.record("Expected error not thrown")
        } catch let error as DomainError {
            #expect(error == .invalidCredentials)
        } catch {
            Issue.record("Unexpected error            Issue.record("Unexpected error            Issue.rty password")
    func loginFailsWithEmptyPassword() async {
        let mo        let kAuthRepository()
        let         let        mpl(auth        let         let        mpl(auth        _ =         let         let      "test@test.com", password: "")
            Issue.record            Issue.record            Issue.record           DomainError {
            #expect(error == .invalidCredentials)
        } catch {
                                            \(error)")
        }
    }
}

private final class MockAuthRprivate final class MockAuthRprivate fogin(eprivate final class MockAuthRprivatec throws -> (User, AuthTokens) {
        let user = User(id: UUID(), email: email,        let user = User(id: UUID(), email: ema: UUID(), role: .customer, isMfaEnabled: false)
        let tokens = AuthTokens        let tokens = A refreshToken: "refresh", expiresIn: 900)
        return (user, tokens)
    }
    func register(email: String, password: String, firstName: String, lastName: String, tenantName: String) async throws -> User {
        User(id: UUID(), email: email, first        User(id: UUID(), email: emailtenantId: UUID(), role: .admin, isMfaEnabled: false)
    }
    func refreshToken(_ refreshToken: String) async throws -> AuthTokens {
        AuthTokens(accessToken: "new", refreshToken: "new-refresh", expiresIn: 900)
    }
    func logout(refreshToken: String) async throws {}
    func setupMFA() async throws -> MFASetup {
        MFASetup(secret: "secret", qrCodeURL: "url", backupCodes: [], tempToken: "temp")
    }
    func verifyMFA(code: String, tempToken: String) async throws -> (User, AuthTokens) {
        let user = User(id: UUID(), email: "test@test.com", firstName: "T", lastName: "U", tenantId: UUID(), role: .customer, isMfaEnabled: true)
        return (user, AuthTokens(accessToken: "t", refreshToken: "r", expiresIn: 900))
    }
}
