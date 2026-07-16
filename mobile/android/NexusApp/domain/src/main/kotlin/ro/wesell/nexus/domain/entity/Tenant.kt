package ro.wesell.nexus.domain.entity

import java.util.UUID

data class Tenant(
    val id: UUID,
    val name: String,
    val subdomain: String,
    val isActive: Boolean
)
