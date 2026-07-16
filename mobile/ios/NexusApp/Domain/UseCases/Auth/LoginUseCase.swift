import Foundation

protocol LoginUseCase: Sendable {
    func execute(email: String, password: String) async throws -> User
}

final class LoginUseCaseImpl: LoginUseCase {
    private let authRepository: AuthRepository

    init(authRepository: AuthRepository) {
        self.authRepository = authRepository
    }

    func execute(email: String, password: String) async throws -> User {
        guard !email.isEmpty, !password.isEmpty else {
            throw DomainError.invalidCredentials
        }
        let (user, _) = try await authRepository.login(email: email, password: password)
        return user
    }
}