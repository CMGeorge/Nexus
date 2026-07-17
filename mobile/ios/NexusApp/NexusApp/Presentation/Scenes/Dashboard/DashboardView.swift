import SwiftUI

struct DashboardView: View {
    @Environment(AppContainer.self) private var container

    var body: some View {
        NavigationStack {
            List {
                Section("Quick Actions") {
                    NavigationLink(destination: CustomerListView()) {
                        Label("Customers", systemImage: "person.2")
                    }
                    Label("Appointments", systemImage: "calendar")
                    Label("Invoices", systemImage: "doc.text")
                    Label("Jobs", systemImage: "wrench")
                }
                Section("Recent Activity") {
                    Text("No recent activity")
                        .foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Dashboard")
        }
    }
}
