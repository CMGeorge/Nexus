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
    private let authRepository: AuthRepository

    var loginState: LoginState = .idle
    var registerState: RegisterState = .idle
    var email = ""
    var password = ""
    var firstName = ""
    var lastName = ""
    var tenantName = ""
    var mfaCode = ""
    var tempToken = ""

    init(loginUseCase: LoginUseCase, authRepository: AuthRepository) {
        self.loginUseCase = loginUseCase
        self.authRepository = authRepository
    }

                                                                  {                   er = try await loginUseCase.execute(email: email, password: password)
            loginState   .success(user)
        } catch let error as DomainError {
              ginState = .error(e ror.localizedDescription)
        } catch {
            loginState = .error(error.localizedDescrip              }
    }

    func register() async {
        registerState = .loading
        do {
            let user = try await authRepository.register(
                email: email, password: passwor                email: email, passwoame, lastNam                email: e     tenantName: tenantName
            )
            registerState = .success(user)
        } catch         } catch     rror {
            registerState = .error(error.localizedDescription)
        } catch {
            registerState = .error(error.localizedDescription)
        }
    }

    func verifyMFA() async {
        loginState = .loading
        do {
            let (user, _) = try await authRepository.verifyMFA(code: mfaCode, tempToken: tempToken)
            loginState = .success(user)
        } catch let error as DomainError {
            loginState = .error(error.localizedDescription)
        } catch {
            loginState = .error(error.localizedDescription)
        }
    }

    func reset() {
        loginState = .idle
        registerState = .idl        reSWIFTEOF

cat > "$BASE/Presentation/Scenes/Auth/LoginView.swift" << 'SWIFTEOF'
import SwiftUI

struct LoginView: View {
    @Environment(AppContainer.self) private var container
    @State private var viewModel: AuthViewModel!
    @State private var showRegister = false

    var body: some View {
        NavigationStack {
            if let vm = viewModel {
                                                                       ProgressView()
                                                             eCase: container.loginUseCase, authRepository: container.authRepository) }
            }
                                                                                                          VStack(spacing: 24) {
            Spacer()

            Image(systemName: "building.2")
                .font(.system(size: 60))
                  oregroundStyle(.blue)

            Text("Nexus")
                .font(.largeTitle.bold())
             Text("Multi-Tenant Business Manag             Text("Multi-Tenant Busineline)
                .foregroundStyle(.secondary)

            Spacer().frame(           

            NexusTextField(p            NexusTextField(p            { vm.email }, set:            NexusTextField(p         .keyboardType(.emailAddress)
                .textContentType(.emailAddress)
                .autocapitalization(.none)

            NexusTextField(placeholder: "Password", text: Binding(get: { vm.password }, set: { vm.password = $0 }), isSecure: true)
                .textContentType(.password)

            switch vm.loginState {
            case .loading:
                ProgressView()
                    .padding()

            case .error(let message):
                ErrorBanner(message: message) { vm.reset() }

            default:
                EmptyView()
            }

            NexusButton(title: "Sign In") {
                Task { await vm.login() }
            }
            .disabled(vm.email.isEmpty || vm.password.isEmpty)

            Button("Create Account") { showRegister = true }
                .font(.subheadline)

            Spacer()
        }
        .padding(.horizontal, 32)
        .navigationDestination(isPresented: $showRegister) {
            RegisterView()
        }
    }
}
