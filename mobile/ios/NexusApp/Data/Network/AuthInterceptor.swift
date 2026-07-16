import Foundation

actor AuthInterceptor {
    private var accessToken: String?
    private var refreshToken: String?
    private let keychain: KeychainManager
    private let baseURL: URL
    private var refreshTask: Task<(String, String), Error>?

    init(keychain: KeychainManager, baseURL: URL) {
        self.keychain = keychain
        self.baseURL = baseURL
        Task { await loadTokens() }
    }

    func intercept(_ request: inout URLRequest) async throws {
        var token = await accessToken
        if token == nil {
            token = try await refreshAccessToken()
        }
        if let token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
    }

    func storeTokens(access: String, refresh: String) async {
        accessToken = access
        refreshToken = refresh
        keychain.save(access, for: .accessToken)
        keychain.save(refresh, for: .refreshToken)
    }

    func clearTokens() async {
        accessToken = nil
        refreshToken = nil
        keychain.delete(.accessToken)
        keychain.delete(.refreshToken)
    }

    private func loadTokens() async {
        accessToken = keychain.read(.accessToken)
        refreshToken = keychain.read(.refreshToken)
    }

    private func refreshAccessToken() async throws -> String {
        if let task = refreshTask { return try await task.value }
        let task = Task<(String, String), Error> { [weak self] in
            guard let self else { throw DomainError.unauthorized }
            let currentRefresh = await refreshToken
            guard let currentRefresh else { throw DomainError.unauthorized }
            let url = await baseURL.appendingPathComponent("api/v1/auth/refresh")
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try JSONEncoder().encode(["refresh_token": currentRefresh])
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
                await clearTokens()
                throw DomainError.unauthorized
            }
            struct TokenResponse: Decodable { let accessToken: String; let refreshToken: String }
            let tr = try JSONDecoder().decode(TokenResponse.self, from: data)
            await storeTokens(access: tr.accessToken, refresh: tr.refreshToken)
            return (tr.accessToken, tr.refreshToken)
        }
        refreshTask = task
        let (access, _) = try await task.value
        refreshTask = nil
        return access
    }
}