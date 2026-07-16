package com.nexus.domain.usecase.auth

import com.nexus.domain.entity.User
import com.nexus.domain.repository.AuthRepository

class LoginUseCase(private val authRepository: AuthRepository) {
    suspend operator fun invoke(email: String, password: String): Result<User> {
        return try {
            if (email.isBlank() || password.isBlank()) {
                Result.failure(IllegalArgumentException("Email and password required"))
            } else {
                val (user, _) = authRepository.login(email, password)
                Result.success(user)
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
