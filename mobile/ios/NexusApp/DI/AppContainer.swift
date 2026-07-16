import Foundation

@MainActor
@Observable
final class AppContainer {
    static let shared = AppContainer()

    let authInterceptor: AuthInterceptor
    let tenantInterceptor: TenantHeaderInterceptor
    let httpClient: HTTPClient
    let authRepository: AuthRepository
    let loginUseCase: LoginUseCase

    init(baseURL: URL = APIConstants.baseURL) {
        let keychain = KeychainManager.shared
        let auth = AuthInterceptor(keychain: keychain, baseURL: baseURL)
        let tenant = TenantHeaderInterceptor()
        authInterceptor = auth
        tenantInterceptor = tenant

        httpClient = URLSessionHTTPClient(baseURL: baseURL, authInterceptor: auth, tenantInterceptor: tenant)
        authRepository = AuthRepositoryImpl(httpClient: httpClient, authInterceptor: auth, tenantInterceptor: tenant)
        loginUseCase = LoginUseCaseImpl(authRepository: authRepository)
    }
}