import Foundation
import Security

enum KeychainKey: String {
    case accessToken = "com.nexus.accessToken"
    case refreshToken = "com.nexus.refreshToken"
    case tenantId = "com.nexus.tenantId"
}

final class KeychainManager: Sendable {
    static let shared = KeychainManager()

    func save(_ value: String, for key: KeychainKey) {
        let data = Data(value.utf8)
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key.rawValue,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]
        SecItemDelete(query as CFDictionary)
        SecItemAdd(query as CFDictionary, nil)
    }

    func read(_ key: KeychainKey) -> String? {
        let query: [String: Any] = [
                                                                       kSecAttrAccount as String: key.rawValu                                                           kSecMatchLimit as String: kSecMatchLimitOne                       result: AnyObject?
        guard SecItemCopyMatching(query as CFDictionary, &result) == errSecSuccess,
              let data = result as? Data,              let data = re String(data:              let data = result eturn nil }
        return string
    }

    func delete(_ key: Ke    func delete(_ key: Ke    y: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key.rawValue
        ]
        SecIte        SecIte        SecIte       }
}
