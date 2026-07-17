import Foundation

// MARK: - Validation Rules

public enum Validators {

    // MARK: - Email

    /// Validates an email address format.
    /// - Parameter email: The email string to validate.
    /// - Returns: `.valid` if the email is empty (optional) or matches RFC 5322 simplified pattern.
    public static func email(_ email: String, required: Bool = true) -> ValidationResult {
        let trimmed = email.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty {
            return required ? .invalid("Email is required.") : .valid
        }
        // RFC 5322 simplified: local@domain.tld
        let pattern = #"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"#
        let predicate = NSPredicate(format: "SELF MATCHES %@", pattern)
        return predicate.evaluate(with: trimmed) ? .valid : .invalid("Enter a valid email address.")
    }

    // MARK: - Password

    /// Validates password strength.
    /// Rules: min 8 chars, at least 1 uppercase, 1 lowercase, 1 digit.
    public static func password(_ password: String) -> ValidationResult {
        let trimmed = password.trimmingCharacters(in: .whitespacesAndNewlines)
        guard trimmed.count >= 8 else {
            return .invalid("Password must be at least 8 characters.")
        }
        let hasUppercase = trimmed.range(of: #"[A-Z]"#, options: .regularExpression) != nil
        let hasLowercase = trimmed.range(of: #"[a-z]"#, options: .regularExpression) != nil
        let hasDigit = trimmed.range(of: #"\d"#, options: .regularExpression) != nil

        var missing: [String] = []
        if !hasUppercase { missing.append("uppercase letter") }
        if !hasLowercase { missing.append("lowercase letter") }
        if !hasDigit { missing.append("digit") }

        if missing.isEmpty { return .valid }
        return .invalid("Password must include at least one \(missing.joined(separator: ", ")).")
    }

    // MARK: - Name

    /// Validates a person's name.
    /// Rules: 2-100 characters, letters, spaces, hyphens, apostrophes only.
    public static func name(_ name: String, field: String = "Name") -> ValidationResult {
        let trimmed = name.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            return .invalid("\(field) is required.")
        }
        guard trimmed.count >= 2 else {
            return .invalid("\(field) must be at least 2 characters.")
        }
        guard trimmed.count <= 100 else {
            return .invalid("\(field) must be under 100 characters.")
        }
        let allowed = CharacterSet.letters.union(.whitespaces).union(.init(charactersIn: "-'ăâîșțĂÂÎȘȚ"))
        let hasInvalidChars = trimmed.rangeOfCharacter(from: allowed.inverted) != nil
        if hasInvalidChars {
            return .invalid("\(field) contains invalid characters.")
        }
        return .valid
    }

    // MARK: - Phone (Romanian)

    /// Validates a Romanian phone number.
    /// Accepts: 07xx xxx xxx, +40 7xx xxx xxx, 021 xxx xxxx, etc.
    /// Optional when `required` is false and value is empty.
    public static func phone(_ phone: String, required: Bool = false) -> ValidationResult {
        let trimmed = phone.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty {
            return required ? .invalid("Phone number is required.") : .valid
        }
        // Remove common separators
        let digitsOnly = trimmed
            .replacingOccurrences(of: " ", with: "")
            .replacingOccurrences(of: "-", with: "")
            .replacingOccurrences(of: ".", with: "")
            .replacingOccurrences(of: "(", with: "")
            .replacingOccurrences(of: ")", with: "")

        // Romanian patterns:
        // 07xx xxx xxx (mobile)
        // 021/023x/024x/025x/026x/027x/028x/029x (landline)
        // +40 7xx or +40 2xx
        let pattern = #"^(?:\+40|0)[0-9]{9}$"#
        let predicate = NSPredicate(format: "SELF MATCHES %@", pattern)
        return predicate.evaluate(with: digitsOnly) ? .valid : .invalid("Enter a valid Romanian phone number (e.g. 07xx xxx xxx).")
    }

    // MARK: - Required (generic)

    /// Validates a generic required field with min/max length.
    public static func required(
        _ value: String,
        field: String = "This field",
        minLength: Int = 1,
        maxLength: Int = 200
    ) -> ValidationResult {
        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            return .invalid("\(field) is required.")
        }
        guard trimmed.count >= minLength else {
            return .invalid("\(field) must be at least \(minLength) characters.")
        }
        guard trimmed.count <= maxLength else {
            return .invalid("\(field) must be under \(maxLength) characters.")
        }
        return .valid
    }
}
