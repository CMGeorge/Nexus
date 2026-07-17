import Foundation

actor AuthInterceptor {
    private(set) var accessToken: String?
    private var refreshToken: String?
    private let keychain: KeychainManager
    private let baseURL: URL
    private(set) var isRefreshing = false
    private var refreshTask: Task<String, Error>?

    init(keychain: KeychainManager, baseURL: URL) {
        self.keychain = keychain
        self.baseURL = baseURL
        Task { await loadTokens() }
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

    func refreshAccessToken() async throws -> String {
        // Deduplicate concurrent refresh attempts
        if let existing = refreshTask { return try await existing.value }
        let task = Task<String, Error> {
            defer { refreshTask = nil }
            guard let currentRefresh = refreshToken else { throw DomainError.unauthorized }
            let url = baseURL.appendingPathComponent("api/v1/auth/refresh")
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try JSONEncoder().encode(["refresh_token": currentRefresh])
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
                await clearTokens()
                throw DomainError.unauthorized
            }
            struct TR: Decodable { let access_token: String; let refresh_token: String }
            let tr = try JSONDecoder().decode(TR.self, from: data)
            await storeTokens(access: tr.access_token, refresh: tr.refresh_token)
            return tr.access_token
        }
        refreshTask = task
        return try await task.value
    }

    private func loadTokens() async {
        accessToken = keychain.read(.accessToken)
        refreshToken = keychain.read(.refreshToken)
    }
}