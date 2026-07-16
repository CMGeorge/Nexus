import Foundation

protocol ViewModel: AnyObject, Sendable {
    associatedtype State
    @MainActor var state: State { get }
}
