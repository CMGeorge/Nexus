package com.nexus.domain.repository

import com.nexus.domain.entity.User

data class AuthTokens(
    val accessToken: String,
    val refreshToken: String,
    val expiresIn: Int
)

data class MFASetup(
    val secret: String,
    val qrCodeURL: String,
    val backupCodes: List<String>,
    val tempToken: String
)

interface AuthRepository {
    suspend fun login(email: String, password: String): Pair<User, AuthTokens>
    suspend fun register(email: String, password: String, firstName: String, lastName: String, tenantName: String): User
    suspend fun refreshToken(refreshToken: String): AuthTokens
    suspend fun logout(refreshToken: String)
    suspend fun setupMFA(): MFASetup
    suspend fun verifyMFA(code: String, tempToken: String): Pair<User, AuthTokens>
}
