package ro.wesell.nexus.data

import ro.wesell.nexus.core.constants.ApiConstants
import ro.wesell.nexus.data.remote.api.AuthApi
import ro.wesell.nexus.data.remote.interceptor.AuthInterceptor
import ro.wesell.nexus.data.remote.interceptor.TenantInterceptor
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides @Singleton
    fun provideJson(): Json = Json { ignoreUnknownKeys = true }

    @Provides @Singleton
    fun provideOkHttp(authInterceptor: AuthInterceptor, tenantInterceptor: TenantInterceptor): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(tenantInterceptor)
            .addInterceptor(authInterceptor)
            .build()
    }

    @Provides @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient, json: Json): Retrofit {
        return Retrofit.Builder()
            .baseUrl(ApiConstants.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
            .build()
    }

    @Provides @Singleton
    fun provideAuthApi(retrofit: Retrofit): AuthApi = retrofit.create(AuthApi::class.java)
}
