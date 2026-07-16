package com.nexus.data.remote.api

import com.nexus.data.remote.dto.LoginRequestDto
import com.nexus.data.remote.dto.LoginResponseDto
import com.nexus.data.remote.dto.RegisterRequestDto
import com.nexus.data.remote.dto.TokensDto
import com.nexus.data.remote.dto.UserDto
import retrofit2.http.Body
import retrofit2.http.POST

interface AuthApi {
    @POST("api/v1/auth/login")
    suspend fun login(@Body request: LoginRequestDto): LoginResponseDto

    @POST("api/v1/auth/register")
    suspend fun register(@Body request: RegisterRequestDto): UserDto

    @POST("api/v1/auth/refresh")
    suspend fun refresh(@Body request: Map<String, String>): TokensDto

    @POST("api/v1/auth/logout")
    suspend fun logout(@Body request: Map<String, String>)
}
