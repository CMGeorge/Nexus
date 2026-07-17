import Foundation
import Observation

@MainActor
@Observable
final class AuthViewModel {
    enum LoginState {
        case idle
        case loading
        case success(User)
        case mfaRequired(String)
        case error(String)
    }

    enum RegisterState {
        case idle
        case loading
        case success(User)
        case error(String)
    }

    private let loginUseCase: LoginUseCase
    private let authRepository: any AuthRepository

    // MARK: - Input Fields
    var loginState: LoginState = .idle
    var registerState: RegisterState = .idle
    var email = "" { didSet { validateEmail() } }
    var password = "" { didSet { validatePassword() } }
    var firstName = "" { didSet { validateFirstName() } }
    var lastName = "" { didSet { validateLastName() } }
    var tenantName = "" { didSet { validateTenantName() } }
    var mfaCode = ""
    var tempToken = ""

    // MARK: - Field-Level Validation Errors
    var emailError: String?
    var passwordError: String?
    var firstNameError: String?
    var lastNameError: String?
    var tenantNameError: String?

    // MARK: - Derived Validation State
    var isLoginValid: Bool {
        emailError == nil && passwordError == nil
            && !email.trimmingCharacters(in: .whitespaces).isEmpty
            && !password.trimmingCharacters(in: .whitespaces).isEmpty
    }

    var isRegisterValid: Bool {
        emailError == nil && passwordError == nil && tenantNameError == nil
            && !email.trimmingCharacters(in: .whitespaces).isEmpty
            && !password.trimmingCharacters(in: .whitespaces).isEmpty
            && !tenantName.trimmingCharacters(in: .whitespaces).isEmpty
    }

    init(loginUseCase: LoginUseCase, authRepository: any AuthRepository) {
        self.loginUseCase = loginUseCase
        self.authRepository = authRepository
    }

    // MARK: - Validation

    func validateEmail() {
        emailError = Validators.email(email).errorMessage
    }

    func validatePassword() {
        if password.isEmpty {
            passwordError = "Password is required."
        } else {
            passwordError = Validators.password(password).errorMessage
        }
    }

    func validateFirstName() {
        firstNameError = firstName.isEmpty ? nil : Validators.name(firstName, field: "First name").errorMessage
    }

    func validateLastName() {
        lastNameError = lastName.isEmpty ? nil : Validators.name(lastName, field: "Last name").errorMessage
    }

    func validateTenantName() {
        tenantNameError = Validators.required(tenantName, field: "Company name", minLength: 2).errorMessage
    }

    func clearFieldErrors() {
        emailError = nil
        passwordError = nil
        firstNameError = nil
        lastNameError = nil
        tenantNameError = nil
    }

    // MARK: - Actions

    func login() async {
        guard isLoginValid else { return }
        loginState = .loading
        do {
            let user = try await loginUseCase.execute(
                email: email.trimmingCharacters(in: .whitespaces),
                password: password
            )
            loginState = .success(user)
        } catch {
            loginState = .error(error.localizedDescription)
        }
    }

    func register() async {
        guard isRegisterValid else { return }
        registerState = .loading
        do {
            _ = try await authRepository.register(
                email: email.trimmingCharacters(in: .whitespaces),
                password: password,
                firstName: firstName.trimmingCharacters(in: .whitespaces).isEmpty ? nil : firstName.trimmingCharacters(in: .whitespaces),
                lastName: lastName.trimmingCharacters(in: .whitespaces).isEmpty ? nil : lastName.trimmingCharacters(in: .whitespaces),
                tenantName: tenantName.trimmingCharacters(in: .whitespaces)
            )
            let user = User(
                id: UUID(), email: email.trimmingCharacters(in: .whitespaces),
                firstName: firstName.trimmingCharacters(in: .whitespaces),
                lastName: lastName.trimmingCharacters(in: .whitespaces),
                tenantId: UUID(), role: .admin, isMfaEnabled: false
            )
            registerState = .success(user)
        } catch {
            registerState = .error(error.localizedDescription)
        }
    }

    func reset() {
        loginState = .idle
        registerState = .idle
        clearFieldErrors()
    }
}