package ro.wesell.nexus.data.mapper

import ro.wesell.nexus.data.remote.dto.UserDto
import ro.wesell.nexus.domain.entity.User
import ro.wesell.nexus.domain.entity.UserRole

fun UserDto.toDomain(): User = User(
    id = id,
    email = email,
    firstName = firstName,
    lastName = lastName,
    tenantId = tenantId,
    role = try { UserRole.valueOf(role.uppercase()) } catch (_: Exception) { UserRole.CUSTOMER },
    isMfaEnabled = isMfaEnabled
)
