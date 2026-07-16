import SwiftUI

struct DashboardView: View {
    @Environment(AppContainer.self) private var container

    var body: some View {
        NavigationStack {
            List {
                Section("Quick Actions") {
                    Label("Appointments", systemImage: "calendar")
                    Label("Customers", systemImage: "person.2")
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
