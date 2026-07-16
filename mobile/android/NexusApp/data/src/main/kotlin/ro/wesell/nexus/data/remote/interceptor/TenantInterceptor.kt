package ro.wesell.nexus.data.remote.interceptor

import okhttp3.Interceptor
import okhttp3.Response

/**
 * Injects X-Tenant-ID and X-Branch-ID headers on every API request.
 *
 * Implements ADR-0010 hierarchical multi-tenancy:
 * - Institution users: X-Tenant-ID = institution UUID, X-Branch-ID = optional branch filter
 * - Branch users: X-Tenant-ID = branch UUID, no X-Branch-ID
 */
class TenantInterceptor(
    private val tenantIdProvider: () -> String?,
    private val branchIdProvider: () -> String?
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val builder = chain.request().newBuilder()

        tenantIdProvider()?.let { tenantId ->
            builder.addHeader("X-Tenant-ID", tenantId)
        }

        branchIdProvider()?.let { branchId ->
            builder.addHeader("X-Branch-ID", branchId)
        }

        return chain.proceed(builder.build())
    }
}
