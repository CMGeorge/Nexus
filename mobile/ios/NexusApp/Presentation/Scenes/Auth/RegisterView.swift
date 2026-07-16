import SwiftUI

struct RegisterView: View {struct RegisterView: View {struct Registvate var container
    @State private var viewModel: AuthViewModel!
    @Environment(\.dismi    @Environment(\.dismi    @Environmensome View {
        if let vm = viewModel {
            content(with            contelse {
                                           .task { viewModel = AuthViewModel(loginUseCase: container.loginUseCase, authRepository: container.authRepository) }
        }
    }

    @ViewBuilder
    private func content(with vm: AuthViewModel) -> som    private func content(with vm: AuSection("Account Info") {
                NexusTextField(placeholder: "Email", text: Binding(get: { vm.email }, set: { vm.email = $0 }))
                NexusTextField(placeholder: "Password", text: Binding(get: { vm.password }, set: { vm.password = $0 }), isSecure: true)
            }
            Section("Profile") {
                NexusTextField(pl   holder: "First Name", text: Binding(get: { vm.firstName }, set: { vm.firstName = $0 }))
                                                                                     Name },                                         }
                                                                             "Comp                       g(get: {                                         $0 }))
                                                                             "Comp                       g(get: {                                               case .error(let msg):
                    ErrorBanner(message: msg) { vm.reset() }
                case .success:
                    Label("Account c                    Label("Account c                    Label("Account c                    Label("              default:
                    EmptyView()
                }

                NexusButton(title: "Create Account") {
                    Task { await vm.register() }
                }
                .disabled(vm.email.isEmpty || vm.password.isEmpty || vm.tenantName.isEmpty)
            }
        }
        .navigationTitle("Register")
    }
}
