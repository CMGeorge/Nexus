import Foundation
import Kingfisher

@MainActor
@Observable
final class AppContainer {
    static let shared = AppContainer()

    /// Whether Firebase was successfully configured at launch.
    /// When `false`, push notifications are unavailable.
    /// The login screen checks this to show an on-screen warning.
    static var isFirebaseConfigured: Bool = false

    /// Whether the API base URL is properly configured.
    /// When `false` in Debug builds, the login screen shows a warning banner.
    /// In Release builds this is always `true` (the app would crash otherwise).
    static var isAPIConfigured: Bool { APIConfiguration.isConfigured }

    let authInterceptor: AuthInterceptor
    let tenantInterceptor: TenantHeaderInterceptor
    let httpClient: HTTPClient
    let authRepository: any AuthRepository
    let customerRepository: any CustomerRepositoryProtocol
    let loginUseCase: LoginUseCase

    init(baseURL: URL = APIConstants.baseURL) {
        let keychain = KeychainManager.shared
        let auth = AuthInterceptor(keychain: keychain, baseURL: baseURL)
        let tenant = TenantHeaderInterceptor()
        authInterceptor = auth
        tenantInterceptor = tenant

        httpClient = AlamofireHTTPClient(baseURL: baseURL, authInterceptor: auth, tenantInterceptor: tenant)
        authRepository = AuthRepositoryImpl(httpClient: httpClient, authInterceptor: auth, tenantInterceptor: tenant)
        customerRepository = CustomerRepository(httpClient: httpClient, tenantInterceptor: tenant)
        loginUseCase = LoginUseCaseImpl(authRepository: authRepository)
    }
}

// MARK: - Kingfisher Configuration
extension AppContainer {
    /// Configure Kingfisher global settings for the app.
    static func configureImageLoading() {
        let cache = ImageCache.default
        cache.memoryStorage.config.totalCostLimit = 50 * 1024 * 1024  // 50 MB
        cache.diskStorage.config.sizeLimit = 200 * 1024 * 1024         // 200 MB
    }
}