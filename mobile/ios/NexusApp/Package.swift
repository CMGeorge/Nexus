// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "NexusApp",
    platforms: [
        .iOS(.v17),
        .macOS(.v14),
    ],
    products: [
        .library(name: "NexusApp", targets: ["NexusApp"]),
    ],
    dependencies: [
        .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.10.0"),
        .package(url: "https://github.com/onevcat/Kingfisher.git", from: "8.0.0"),
    ],
    targets: [
        .target(
            name: "NexusApp",
            dependencies: [
                .product(name: "Alamofire", package: "Alamofire"),
                .product(name: "Kingfisher", package: "Kingfisher"),
            ],
            path: "NexusApp",
            exclude: ["Assets.xcassets"]
        ),
        .testTarget(
            name: "NexusAppTests",
            dependencies: ["NexusApp"],
            path: "NexusAppTests"
        ),
    ]
)