import SwiftUI

struct CustomerDetailView: View {
    let customer: Customer
    @State private var viewModel = CustomerDetailViewModel()

    var body: some View {
        List {
            Section("Contact") {
                if let email = customer.email {
                    LabeledContent("Email", value: email)
                }
                if let phone = customer.phone {
                    LabeledContent("Phone", value: phone)
                }
                if !customer.fullAddress.isEmpty {
                    LabeledContent("Address", value: customer.fullAddress)
                }
                if let country = customer.country {
                    LabeledContent("Country", value: country)
                }
            }

            Section("Activity") {
                LabeledContent("Status", value: customer.isActive ? "Active" : "Inactive")
                LabeledContent("Created", value: customer.createdAt.formatted(date: .abbreviated, time: .omitted))
            }

            Section("History") {
                if viewModel.isLoading {
                    ProgressView()
                } else {
                    LabeledContent("Appointments", value: "\(viewModel.history.appointments)")
                    LabeledContent("Jobs", value: "\(viewModel.history.jobs)")
                    LabeledContent("Invoices", value: "\(viewModel.history.invoices)")
                    LabeledContent("Notes", value: "\(viewModel.history.notes)")
                }
            }
        }
        .navigationTitle(customer.fullName)
        .task { await viewModel.loadHistory(for: customer.id) }
    }
}

@Observable
final class CustomerDetailViewModel {
    var isLoading = false
    var history = CustomerHistory(appointments: 0, jobs: 0, invoices: 0, notes: 0)

    func loadHistory(for customerId: UUID) async {
        isLoading = true
        defer { isLoading = false }
        // In production, this calls the history API endpoint
        history = CustomerHistory(appointments: 0, jobs: 0, invoices: 0, notes: 0)
    }
}

struct CustomerHistory {
    var appointments: Int
    var jobs: Int
    var invoices: Int
    var notes: Int
}

struct CustomerFormView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var firstName = ""
    @State private var lastName = ""
    @State private var email = ""
    @State private var phone = ""
    @State private var city = ""

    // Validation errors
    @State private var firstNameError: String?
    @State private var lastNameError: String?
    @State private var emailError: String?
    @State private var phoneError: String?

    var onCreated: (Customer) -> Void = { _ in }

    private var isFormValid: Bool {
        Validators.name(firstName, field: "First name").isValid
            && Validators.name(lastName, field: "Last name").isValid
            && Validators.email(email, required: false).isValid
            && Validators.phone(phone).isValid
    }

    var body: some View {
        NavigationStack {
            Form {
                Section("Name") {
                    NexusTextField(
                        placeholder: "First Name",
                        text: $firstName,
                        onSubmit: { validateFirstName() }
                    )
                    NexusTextField(
                        placeholder: "Last Name",
                        text: $lastName,
                        onSubmit: { validateLastName() }
                    )
                }
                Section("Contact") {
                    NexusTextField(
                        placeholder: "Email",
                        text: $email,
                        keyboardType: .emailAddress,
                        textContentType: .emailAddress
                    )
                    NexusTextField(
                        placeholder: "Phone",
                        text: $phone,
                        keyboardType: .phonePad,
                        textContentType: .telephoneNumber
                    )
                    NexusTextField(
                        placeholder: "City",
                        text: $city
                    )
                }
            }
            .navigationTitle("New Customer")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        saveCustomer()
                    }
                    .disabled(!isFormValid)
                }
            }
        }
    }

    // MARK: - Validation

    private func validateFirstName() {
        firstNameError = Validators.name(firstName, field: "First name").errorMessage
    }

    private func validateLastName() {
        lastNameError = Validators.name(lastName, field: "Last name").errorMessage
    }

    private func validateEmail() {
        emailError = Validators.email(email, required: false).errorMessage
    }

    private func validatePhone() {
        phoneError = Validators.phone(phone).errorMessage
    }

    private func validateAll() {
        validateFirstName()
        validateLastName()
        validateEmail()
        validatePhone()
    }

    // MARK: - Save

    private func saveCustomer() {
        validateAll()
        guard isFormValid else { return }

        let trimmedFirst = firstName.trimmingCharacters(in: .whitespaces)
        let trimmedLast = lastName.trimmingCharacters(in: .whitespaces)
        let trimmedEmail = email.trimmingCharacters(in: .whitespaces)
        let trimmedPhone = phone.trimmingCharacters(in: .whitespaces)
        let trimmedCity = city.trimmingCharacters(in: .whitespaces)

        let customer = Customer(
            id: UUID(), tenantId: UUID(),
            firstName: trimmedFirst, lastName: trimmedLast,
            email: trimmedEmail.isEmpty ? nil : trimmedEmail,
            phone: trimmedPhone.isEmpty ? nil : trimmedPhone,
            addressLine1: nil, addressLine2: nil,
            city: trimmedCity.isEmpty ? nil : trimmedCity,
            county: nil, postalCode: nil,
            country: "RO", isActive: true,
            createdAt: .now, updatedAt: .now
        )
        onCreated(customer)
        dismiss()
    }
}