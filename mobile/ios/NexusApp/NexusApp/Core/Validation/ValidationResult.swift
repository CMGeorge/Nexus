import Foundation

/// A validation result for a single field.
public enum ValidationResult: Equatable {
    case valid
    case invalid(String)

    public var isValid: Bool {
        if case .valid = self { return true }
        return false
    }

    public var errorMessage: String? {
        if case .invalid(let message) = self { return message }
        return nil
    }
}
