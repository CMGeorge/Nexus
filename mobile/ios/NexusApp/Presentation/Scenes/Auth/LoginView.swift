import SwiftUI

struct LoginView: View {
    @Environment(AppContainer.self) private var container
    @State private var viewModel: AuthViewModel?
    @State private var showRegister = false

    var body: some View {
        NavigationStack {
            if let vm = viewModel {
                content(with: vm)
            } else {
                ProgressView()
                    .task { viewModel = AuthViewModel(loginUseCase: container.loginUseCase, authRepository: container.authRepository) }
            }
        }
    }

    @ViewBuilder
    private func content(with vm: AuthViewModel) -> some View {
        VStack(spacing: 24) {
            Spacer()
            Image(systemName: "building.2").font(.system(size: 60)).foregroundStyle(.blue)
            Text("Nexus").font(.largeTitle.bold())
            Text("Multi-Tenant Business Management").font(.subheadline).foregroundStyle(.secondary)
            Spacer().frame(height: 24)

            NexusTextField(placeholder: "Email", text: Binding(get: { vm.email }, set: { vm.email = $0 }))
                .keyboardType(.emailAddress).textContentType(.emailAddress).autocapitalization(.none)
            NexusTextField(placeholder: "Password", text: Binding(get: { vm.password }, set: { vm.password = $0 }), isSecure: true)
                .textContentType(.password)

            switch vm.loginState {
            case .loading: ProgressView().padding()
            case .error(let message): ErrorBanner(message: message) { vm.reset() }
            default: EmptyView()
            }

            NexusButton(title: "Sign In") { Task { await vm.login() } }
                .disabled(vm.email.isEmpty || vm.password.isEmpty)

            Button("Create Account") { showRegister = true }.font(.subheadline)
            Spacer()
        }
        .padding(.horizontal, 32)
        .navigationDestination(isPresented: $showRegister) { RegisterView() }
    }
}