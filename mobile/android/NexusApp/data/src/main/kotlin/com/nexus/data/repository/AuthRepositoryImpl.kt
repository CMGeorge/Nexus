package com.nexus.data.repository

import com.nexus.data.mapper.toDomain
import com.nexus.data.remote.api.AuthApi
import com.nexus.data.remote.dto.LoginRequestDto
import com.nexus.data.remote.dto.RegisterRequestDto
import com.nexus.domain.entity.User
import com.nexus.domain.repository.AuthRepository
import com.nexus.domain.repository.AuthTokens
import com.nexus.domain.repository.MFASetup
import javax.inject.Inject

class AuthRepositoryImpl @Inject constructor(
    private val authApi: AuthApi
) : AuthRepository {
    override suspend fun login(email: String, password: String): Pair<User, AuthTokens> {
        val response = authApi.login(LoginRequestDto(email, password))
        return response.user.toDomain() to AuthTokens(
            accessToken = response.tokens.accessToken,
            refreshToken = response.tokens.refreshToken,
            expiresIn = response.tokens.expiresIn
        )
    }

    override suspend fun register(email: String, password: String, firstName: String, lastName: String, tenantName: String): User {
        return authApi.register(RegisterRequestDto(email, password, firstName, lastName, tenantName)).toDomain()
    }

    override suspend fun refreshToken(refreshToken: String): AuthTokens {
        val tokens = authApi.refresh(mapOf("refresh_token" to refreshToken))
        return AuthTokens(tokens.accessToken, tokens.refreshToken, tokens.expiresIn)
    }

    override suspend fun logout(refreshToken: String) {
        authApi.logout(mapOf("refresh_token" to refreshToken))
    }

    override suspend fun setupMFA(): MFASetup {
        throw UnsupportedOperationException("MFA not yet implemented")
    }

    override suspend fun verifyMFA(code: String, tempToken: String): Pair<User, AuthTokens> {
        throw UnsupportedOperationException("MFA not yet implemented")
    }
}
