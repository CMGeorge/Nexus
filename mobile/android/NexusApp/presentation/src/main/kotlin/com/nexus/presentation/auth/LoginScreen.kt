package com.nexus.presentation.auth

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Business
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.nexus.domain.entity.User
import com.nexus.presentation.components.ErrorBanner
import com.nexus.presentation.components.LoadingIndicator
import com.nexus.presentation.components.NexusButton
import com.nexus.presentation.components.NexusTextField

@Composable
fun LoginScreen(
    viewModel: AuthViewModel = hiltViewModel(),
    onLoginSuccess: (User) -> Unit = {}
) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Column(
        modifier = Modifier.fillMaxSize().padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(Icons.Default.Business, contentDescription = null, modifier = Modifier.size(60.dp), tint = MaterialTheme.colorScheme.primary)
        Spacer(Modifier.height(16.dp))
        Text("Nexus", style = MaterialTheme.typography.headlineLarge)
        Text("Multi-Tenant Business Management", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(Modifier.height(32.dp))

        NexusTextField(placeholder = "Email", value = email, onValueChange = { email = it })
        Spacer(Modifier.height(12.dp))
        NexusTextField(placeholder = "Password", value = password, onValueChange = { password = it }, isPassword = true)

        Spacer(Modifier.height(16.dp))

        when (val state = uiState) {
            is AuthViewModel.UiState.Loading -> LoadingIndicator()
            is AuthViewModel.UiState.Error -> ErrorBanner(state.message)
            is AuthViewModel.UiState.Success -> onLoginSuccess(state.user)
            else -> {}
        }

        Spacer(Modifier.height(12.dp))
        NexusButton(title = "Sign In", onClick = { viewModel.login(email, password) })
        Spacer(Modifier.height(8.dp))
        TextButton(onClick = { /* TODO: navigate to register */ }) {
            Text("Create Account")
        }
    }
}
