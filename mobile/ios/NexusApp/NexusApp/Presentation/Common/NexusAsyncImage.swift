import Kingfisher
import SwiftUI

/// Async image view using Kingfisher for caching and progressive loading.
struct NexusAsyncImage: View {
    let url: URL?
    var placeholder: Image = Image(systemName: "photo")

    var body: some View {
        KFImage(url)
            .placeholder { ProgressView() }
            .fade(duration: 0.25)
            .cacheOriginalImage()
            .resizable()
            .aspectRatio(contentMode: .fill)
    }
}

/// Circular avatar using Kingfisher with initials fallback.
struct NexusAvatar: View {
    let url: URL?
    let initials: String
    var size: CGFloat = 40

    var body: some View {
        Group {
            if let url {
                KFImage(url)
                    .placeholder { initialsView }
                    .fade(duration: 0.25)
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } else {
                initialsView
            }
        }
        .frame(width: size, height: size)
        .clipShape(Circle())
    }

    private var initialsView: some View {
        ZStack {
            Circle().fill(.tint.opacity(0.2))
            Text(initials)
                .font(.system(size: size * 0.4, weight: .semibold))
                .foregroundStyle(.tint)
        }
    }
}