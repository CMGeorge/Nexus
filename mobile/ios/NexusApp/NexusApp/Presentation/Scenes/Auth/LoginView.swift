import SwiftUI

struct LoginView: View {
    @Environment(AppContainer.self) private var container
    @State private var viewModel: AuthViewModel?
    @State private var showRegister = false
    @State private var isLoggedIn = false
    @State private var apiStatus: APIHealthStatus?
    @State private var showAPILog = false
    @State private var isCheckingHealth = false

    var body: some View {
        Group {
            if isLoggedIn {
                MainTabView()
            } else if let vm = viewModel {
                loginContent(with: vm)
            } else {
                ProgressView()
                    .task {
                        viewModel = AuthViewModel(
                            loginUseCase: container.loginUseCase,
                            authRepository: container.authRepository
                        )
                    }
            }
        }
    }

    private func loginContent(with vm: AuthViewModel) -> some View {
        NavigationStack {
            VStack(spacing: 24) {
                // ── Firebase Warning ────────────────────────
                if !AppContainer.isFirebaseConfigured {
                    HStack(spacing: 6) {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundStyle(.orange)
                        Text("GoogleService-Info.plist not found. Push notifications disabled.")
                            .font(.caption)
                            .foregroundStyle(.orange)
                    }
                    .padding(10)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(.orange.opacity(0.1), in: RoundedRectangle(cornerRadius: 8))
                }

                // ── API URL Warning (Debug only) ───────────
                if !AppContainer.isAPIConfigured {
                    HStack(spacing: 6) {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundStyle(.orange)
                        Text("API_BASE_URL not set. Falling back to api.nexus.local")
                            .font(.caption)
                            .foregroundStyle(.orange)
                    }
                    .padding(10)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(.orange.opacity(0.1), in: RoundedRectangle(cornerRadius: 8))
                }

                // ── API Status Badge ────────────────────────
                HStack(spacing: 8) {
                    if let status = apiStatus {
                        Text(status.icon + " API: " + status.label)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    } else {
                        Text("Checking API connection...")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    Spacer()
                    Button(action: { showAPILog.toggle() }) {
                        Image(systemName: "list.bullet.clipboard")
                            .font(.caption)
                    }
                    Button(action: { checkAPIHealth() }) {
                        Image(systemName: "arrow.clockwise")
                            .font(.caption)
                    }
                    .disabled(isCheckingHealth)
                }
                .padding(.horizontal, 32)
                .padding(.top, 8)

                Spacer()
                Image(systemName: "building.2")
                    .font(.system(size: 60))
                    .foregroundStyle(.tint)
                Text("Nexus")
                    .font(.largeTitle.bold())
                Text("Business Management Platform")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                Spacer().frame(height: 24)

                NexusTextField(
                    placeholder: "Email",
                    text: Binding(get: { vm.email }, set: { vm.email = $0 }),
                    keyboardType: .emailAddress,
                    textContentType: .emailAddress
                )

                NexusTextField(
                    placeholder: "Password",
                    text: Binding(get: { vm.password }, set: { vm.password = $0 }),
                    isSecure: true,
                    textContentType: .password
                )

                switch vm.loginState {
                case .loading:
                    ProgressView().padding()
                case .error(let message):
                    ErrorBanner(message: message) { vm.reset() }
                case .success:
                    Color.clear
                        .onAppear { isLoggedIn = true }
                default:
                    EmptyView()
                }

                NexusButton(title: "Sign In") {
                    Task { await vm.login() }
                }
                .disabled(!vm.isLoginValid)
                .accessibilityLabel("Sign in to your account")

                Button("Create Account") { showRegister = true }
                    .font(.subheadline)

                Spacer()
            }
            .padding(.horizontal, 32)
            .navigationDestination(isPresented: $showRegister) {
                RegisterView()
            }
            .sheet(isPresented: $showAPILog) {
                APILogView()
            }
            .task { checkAPIHealth() }
        }
    }

    private func checkAPIHealth() {
        isCheckingHealth = true
        Task {
            apiStatus = await container.httpClient.checkHealth()
            isCheckingHealth = false
        }
    }
}

// MARK: - API Log Sheet

struct APILogView: View {
    @State private var logger = APILogger.shared

    var body: some View {
        NavigationStack {
            if logger.entries.isEmpty {
                ContentUnavailableView(
                    "No API Calls",
                    systemImage: "antenna.radiowaves.left.and.right.slash",
                    description: Text("API calls will appear here once you start using the app.")
                )
            } else {
                List(logger.entries) { entry in
                    HStack(spacing: 8) {
                        Text(entry.success ? "✅" : "❌")
                            .font(.caption)
                        VStack(alignment: .leading, spacing: 4) {
                            HStack {
                                Text(entry.method)
                                    .font(.caption.bold())
                                    .foregroundStyle(entry.method == "GET" ? .blue : .orange)
                                Text(entry.path)
                                    .font(.caption)
                                    .lineLimit(1)
                                Spacer()
                                if let code = entry.statusCode {
                                    Text("\(code)")
                                        .font(.caption.monospaced())
                                        .foregroundStyle(code < 400 ? .green : .red)
                                }
                            }
                            HStack {
                                Text(entry.formattedTimestamp)
                                    .font(.caption2)
                                    .foregroundStyle(.secondary)
                                Text(entry.formattedDuration)
                                    .font(.caption2)
                                    .foregroundStyle(.secondary)
                            }
                            if let error = entry.error {
                                Text(error)
                                    .font(.caption2)
                                    .foregroundStyle(.red)
                            }
                        }
                    }
                    .padding(.vertical, 2)
                }
                .listStyle(.plain)
            }
        }
        .navigationTitle("API Log")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button("Clear") { logger.clear() }
            }
        }
    }
}