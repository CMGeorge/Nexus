import SwiftUI

@MainActor
struct CustomerListView: View {
    @Environment(AppContainer.self) private var container
    @State private var viewModel: CustomerListViewModel?

    var body: some View {
        NavigationStack {
            Group {
                if let vm = viewModel {
                    customerContent(with: vm)
                } else {
                    ProgressView()
                        .task {
                            viewModel = CustomerListViewModel(
                                repository: container.customerRepository,
                                tenantId: UUID() // Production: from auth state
                            )
                        }
                }
            }
        }
    }

    @ViewBuilder
    private func customerContent(with vm: CustomerListViewModel) -> some View {
        Group {
            if vm.isLoading && vm.customers.isEmpty {
                LoadingView(message: "Loading customers...")
            } else if let error = vm.errorMessage {
                ContentUnavailableView(
                    "Error",
                    systemImage: "exclamationmark.triangle",
                    description: Text(error)
                )
            } else if vm.customers.isEmpty {
                ContentUnavailableView(
                    "No Customers",
                    systemImage: "person.2.slash",
                    description: Text(vm.searchText.isEmpty
                        ? "Add your first customer to get started."
                        : "No customers match your search.")
                )
            } else {
                List(vm.customers) { customer in
                    NavigationLink(value: customer) {
                        CustomerRowView(customer: customer)
                    }
                }
                .listStyle(.plain)
                .refreshable { await vm.refresh() }
            }
        }
        .navigationTitle("Customers")
        .navigationDestination(for: Customer.self) { customer in
            CustomerDetailView(customer: customer)
        }
        .searchable(text: Binding(
            get: { vm.searchText },
            set: { vm.searchText = $0 }
        ), prompt: "Search by name, email, phone")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    vm.showAddSheet = true
                } label: {
                    Image(systemName: "plus")
                }
                .accessibilityLabel("Add new customer")
            }
        }
        .sheet(isPresented: Binding(
            get: { vm.showAddSheet },
            set: { vm.showAddSheet = $0 }
        )) {
            CustomerFormView { created in
                vm.customers.insert(created, at: 0)
            }
        }
        .task { await vm.loadCustomers() }
        .onChange(of: vm.searchText) { _ in
            Task { await vm.loadCustomers() }
        }
    }
}

struct CustomerRowView: View {
    let customer: Customer

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(customer.fullName)
                .font(.headline)
            if let phone = customer.phone {
                Text(phone)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
            if let city = customer.city {
                Text(city)
                    .font(.caption)
                    .foregroundStyle(.tertiary)
            }
        }
        .padding(.vertical, 2)
    }
}

@MainActor
@Observable
final class CustomerListViewModel {
    var customers: [Customer] = []
    var isLoading = false
    var searchText = ""
    var showAddSheet = false
    var errorMessage: String?

    private let repository: any CustomerRepositoryProtocol
    private let tenantId: UUID

    init(repository: any CustomerRepositoryProtocol, tenantId: UUID) {
        self.repository = repository
        self.tenantId = tenantId
    }

    func loadCustomers() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            customers = try await repository.fetchCustomers(
                tenantId: tenantId,
                search: searchText.isEmpty ? nil : searchText,
                limit: 50
            )
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func refresh() async {
        await loadCustomers()
    }
}