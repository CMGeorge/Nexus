import SwiftUI

struct RegisterView: View {
    @Environment(AppContainer.self) private var container
    @State private var viewModel: AuthViewModel?
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        if let vm = viewModel {
            content(with: vm)
        } else {
            Color.clear
                .task {
                    viewModel = AuthViewModel(
                        loginUseCase: container.loginUseCase,
                        authRepository: container.authRepository
                    )
                }
        }
    }

    @ViewBuilder
    private func content(with vm: AuthViewModel) -> some View {
        Form {
            Section("Account Info") {
                NexusTextField(
                    placeholder: "Email",
                    text: Binding(get: { vm.email }, set: { vm.email = $0 }),
                    errorMessage: vm.emailError,
                    keyboardType: .emailAddress,
                    textContentType: .emailAddress
                )
                NexusTextField(
                    placeholder: "Password",
                    text: Binding(get: { vm.password }, set: { vm.password = $0 }),
                    isSecure: true,
                    errorMessage: vm.passwordError,
                    textContentType: .newPassword
                )
            }
            Section("Profile") {
                NexusTextField(
                    placeholder: "First Name",
                    text: Binding(get: { vm.firstName }, set: { vm.firstName = $0 }),
                    errorMessage: vm.firstNameError
                )
                NexusTextField(
                    placeholder: "Last Name",
                    text: Binding(get: { vm.lastName }, set: { vm.lastName = $0 }),
                    errorMessage: vm.lastNameError
                )
            }
            Section("Company") {
                NexusTextField(
                    placeholder: "Company Name",
                    text: Binding(get: { vm.tenantName }, set: { vm.tenantName = $0 }),
                    errorMessage: vm.tenantNameError
                )
            }
            Section {
                switch vm.registerState {
                case .loading:
                    HStack { Spacer(); ProgressView(); Spacer() }
                case .error(let msg):
                    ErrorBanner(message: msg) { vm.reset() }
                case .success:
                    Label("Account created.", systemImage: "checkmark.circle.fill")
                        .foregroundStyle(.green)
                default:
                    EmptyView()
                }

                NexusButton(title: "Create Account") {
                    Task { await vm.register() }
                }
                .disabled(!vm.isRegisterValid)
            }
        }
        .navigationTitle("Register")
    }
}
