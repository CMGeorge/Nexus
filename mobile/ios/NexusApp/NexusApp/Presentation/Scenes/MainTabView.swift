import SwiftUI

struct MainTabView: View {
    @Environment(AppContainer.self) private var container

    var body: some View {
        TabView {
            DashboardView()
                .tabItem {
                    Label("Dashboard", systemImage: "square.grid.2x2")
                }

            CustomerListView()
                .tabItem {
                    Label("Customers", systemImage: "person.2")
                }

            Text("Appointments")
                .tabItem {
                    Label("Calendar", systemImage: "calendar")
                }

            Text("Invoices")
                .tabItem {
                    Label("Invoices", systemImage: "doc.text")
                }
        }
    }
}