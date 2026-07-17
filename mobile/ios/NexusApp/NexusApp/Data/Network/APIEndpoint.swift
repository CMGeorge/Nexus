import Foundation

struct APIEndpoint: Sendable {
    let path: String
    let method: HTTPMethod
    let body: (any Encodable & Sendable)?
    let requiresAuth: Bool
    let requiresTenant: Bool

    init(
        path: String,
        method: HTTPMethod = .get,
        body: (any Encodable & Sendable)? = nil,
        requiresAuth: Bool = true,
        requiresTenant: Bool = true
    ) {
        self.path = path
        self.method = method
        self.body = body
        self.requiresAuth = requiresAuth
        self.requiresTenant = requiresTenant
    }
}

enum HTTPMethod: String, Sendable {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case patch = "PATCH"
    case delete = "DELETE"
}