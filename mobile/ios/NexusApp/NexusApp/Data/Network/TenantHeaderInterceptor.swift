import Foundation

/// Injects X-Tenant-ID and X-Branch-ID headers on every API request.
///
/// Implements ADR-0010 hierarchical multi-tenancy:
/// - Institution users (isInstitution=true): sends X-Tenant-ID=institution UUID,
///   optionally X-Branch-ID to filter to a specific branch
/// - Branch users (isInstitution=false): sends X-Tenant-ID=branch UUID, no X-Branch-ID
actor TenantHeaderInterceptor {
    private var tenantId: UUID?
    private var branchId: UUID?
    private var isInstitution: Bool = false

    /// Configure as institution-level user (can see all branches)
    func setInstitution(_ id: UUID) async {
        tenantId = id
        isInstitution = true
        branchId = nil
    }

    /// Configure as branch-level user (scoped to one branch)
    func setBranch(_ id: UUID) async {
        tenantId = id
        isInstitution = false
        branchId = nil
    }

    /// For institution users: filter to a specific branch
    func filterToBranch(_ id: UUID) async {
        guard isInstitution else { return }
        branchId = id
    }

    func clearBranchFilter() async {
        branchId = nil
    }

    func clearTenant() async {
        tenantId = nil
        branchId = nil
        isInstitution = false
    }

    func intercept(_ request: inout URLRequest) async throws {
        if let tenantId {
            request.setValue(tenantId.uuidString.lowercased(), forHTTPHeaderField: "X-Tenant-ID")
        }
        if let branchId {
            request.setValue(branchId.uuidString.lowercased(), forHTTPHeaderField: "X-Branch-ID")
        }
    }
}