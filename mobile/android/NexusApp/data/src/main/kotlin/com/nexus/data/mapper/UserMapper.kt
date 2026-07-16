package com.nexus.data.mapper

import com.nexus.data.remote.dto.UserDto
import com.nexus.domain.entity.User
import com.nexus.domain.entity.UserRole

fun UserDto.toDomain(): User = User(
    id = id,
    email = email,
    firstName = firstName,
    lastName = lastName,
    tenantId = tenantId,
    role = try { UserRole.valueOf(role.uppercase()) } catch (_: Exception) { UserRole.CUSTOMER },
    isMfaEnabled = isMfaEnabled
)
