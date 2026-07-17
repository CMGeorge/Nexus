import SwiftUI

struct NexusTextField: View {
    let placeholder: String
    @Binding var text: String
    var isSecure: Bool = false
    var errorMessage: String? = nil
    var keyboardType: UIKeyboardType = .default
    var textContentType: UITextContentType? = nil
    var onSubmit: (() -> Void)? = nil

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Group {
                if isSecure {
                    SecureField(placeholder, text: $text)
                } else {
                    TextField(placeholder, text: $text)
                }
            }
            .textFieldStyle(.plain)
            .keyboardType(keyboardType)
            .textContentType(textContentType)
            .padding(12)
            .background(.background, in: RoundedRectangle(cornerRadius: 10))
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(borderColor, lineWidth: borderWidth)
            )
            .onSubmit { onSubmit?() }

            // Reserve space for error text — prevents layout shifts that
            // trigger keyboard constraint recalculations (SecureField's
            // _UIRemoteKeyboardPlaceholderView conflict is harmless but
            // noisy when fired repeatedly).
            Text(errorMessage ?? " ")
                .font(.caption)
                .foregroundStyle(.red)
                .padding(.leading, 4)
                .frame(minHeight: 16)
                .opacity(errorMessage != nil ? 1 : 0)
        }
        .animation(.easeInOut(duration: 0.2), value: errorMessage)
    }

    private var borderColor: Color {
        errorMessage != nil ? .red : .secondary.opacity(0.3)
    }

    private var borderWidth: CGFloat {
        errorMessage != nil ? 1.5 : 1
    }
}
