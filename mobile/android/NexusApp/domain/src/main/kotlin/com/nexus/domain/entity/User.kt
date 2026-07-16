package com.nexus.domain.entity

import java.util.UUID

data class User(
    val id: UUID,
    val email: String,
    val firstName: String,
    val lastName: String,
    val tenantId: UUID,
    val role: UserRole,
    val isMfaEnabled: Boolean
)

enum class UserRole(val value: String) {
    ADMIN("Admin"),
    MANAGER("Manager"),
    EMPLOYEE("Employee"),
    CUSTOMER("Customer")
}
