import SwiftUI

enum NexusTheme {
    enum Colors {
        static let primary = Color.blue
        static let secondary = Color.indigo
        static let accent = Color.orange
        static let success = Color.green
        static let error = Color.red
        static let warning = Color.yellow
    }

    enum Spacing {
        static let xs: CGFloat = 4
        static let sm: CGFloat = 8
        static let md: CGFloat = 16
        static let lg: CGFloat = 24
        static let xl: CGFloat = 32
    }

    enum CornerRadius {
        static let sm: CGFloat = 8
        static let md: CGFloat = 12
        static let lg: CGFloat = 16
    }
}