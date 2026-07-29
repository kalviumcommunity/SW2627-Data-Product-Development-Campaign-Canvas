import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
import os

from src.utils.clerk_auth import (
    get_clerk_credentials,
    get_clerk_endpoints,
    handle_clerk_callback
)

class MockSessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

def test_get_clerk_credentials_env():
    # Test credentials from environment variables
    env_mock = {
        "CLERK_CLIENT_ID": "env_id",
        "CLERK_CLIENT_SECRET": "env_secret",
        "CLERK_DOMAIN": "env.clerk.accounts.dev",
        "CLERK_REDIRECT_URI": "http://localhost:8501/auth"
    }
    with patch("src.utils.clerk_auth.load_dotenv"), patch.dict(os.environ, env_mock), patch.object(st, "secrets", {}):
        client_id, client_secret, domain, redirect_uri = get_clerk_credentials()
        assert client_id == "env_id"
        assert client_secret == "env_secret"
        assert domain == "env.clerk.accounts.dev"
        assert redirect_uri == "http://localhost:8501/auth"

def test_get_clerk_credentials_render_fallback():
    # Test auto-detection when running on Render platform
    env_mock = {
        "CLERK_CLIENT_ID": "render_id",
        "CLERK_CLIENT_SECRET": "render_secret",
        "CLERK_DOMAIN": "render.clerk.accounts.dev",
        "CLERK_REDIRECT_URI": "http://localhost:8501/",
        "RENDER_EXTERNAL_URL": "https://my-app.onrender.com"
    }
    with patch("src.utils.clerk_auth.load_dotenv"), patch.dict(os.environ, env_mock), patch.object(st, "secrets", {}):
        client_id, client_secret, domain, redirect_uri = get_clerk_credentials()
        assert redirect_uri == "https://my-app.onrender.com/"

def test_get_clerk_credentials_secrets():
    # Test credentials from st.secrets
    secrets_mock = {
        "clerk": {
            "client_id": "secret_id",
            "client_secret": "secret_secret",
            "domain": "https://secret.clerk.accounts.dev/",
            "redirect_uri": "http://localhost:8501/"
        }
    }
    with patch("src.utils.clerk_auth.load_dotenv"), patch.object(st, "secrets", secrets_mock), patch.dict(os.environ, {}, clear=True):
        client_id, client_secret, domain, redirect_uri = get_clerk_credentials()
        assert client_id == "secret_id"
        assert client_secret == "secret_secret"
        assert domain == "secret.clerk.accounts.dev"  # protocol and trailing slash should be cleaned
        assert redirect_uri == "http://localhost:8501/"

def test_get_clerk_credentials_secrets_missing():
    # Test fallback to env vars when st.secrets raises an exception (e.g. StreamlitSecretNotFoundError)
    from streamlit.errors import StreamlitSecretNotFoundError
    
    env_mock = {
        "CLERK_CLIENT_ID": "fallback_id",
        "CLERK_CLIENT_SECRET": "fallback_secret",
        "CLERK_DOMAIN": "fallback.clerk.accounts.dev",
        "CLERK_REDIRECT_URI": "http://localhost:8501/"
    }
    
    # Mocking st.secrets property to raise StreamlitSecretNotFoundError when accessed
    mock_secrets = MagicMock()
    mock_secrets.__contains__.side_effect = StreamlitSecretNotFoundError("Missing secrets file")
    
    with patch("src.utils.clerk_auth.load_dotenv"), patch.dict(os.environ, env_mock), patch.object(st, "secrets", mock_secrets):
        client_id, client_secret, domain, redirect_uri = get_clerk_credentials()
        assert client_id == "fallback_id"
        assert client_secret == "fallback_secret"
        assert domain == "fallback.clerk.accounts.dev"
        assert redirect_uri == "http://localhost:8501/"

def test_get_clerk_endpoints_fallback():
    domain = "my-app.clerk.accounts.dev"
    # When requests fail
    with patch("requests.get", side_effect=Exception("network error")):
        endpoints = get_clerk_endpoints(domain)
        assert endpoints["authorization_endpoint"] == f"https://{domain}/oauth/authorize"
        assert endpoints["token_endpoint"] == f"https://{domain}/oauth/token"
        assert endpoints["userinfo_endpoint"] == f"https://{domain}/oauth/userinfo"

def test_get_clerk_endpoints_success():
    domain = "my-app.clerk.accounts.dev"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "authorization_endpoint": "https://custom/auth",
        "token_endpoint": "https://custom/token",
        "userinfo_endpoint": "https://custom/userinfo"
    }
    
    with patch("requests.get", return_value=mock_response):
        endpoints = get_clerk_endpoints(domain)
        assert endpoints["authorization_endpoint"] == "https://custom/auth"
        assert endpoints["token_endpoint"] == "https://custom/token"
        assert endpoints["userinfo_endpoint"] == "https://custom/userinfo"

def test_handle_clerk_callback_no_code():
    with patch.object(st, "query_params", {}):
        # Should not crash and do nothing
        handle_clerk_callback()

def test_handle_clerk_callback_success():
    # Simulate code present in query_params
    query_params_mock = MagicMock()
    query_params_mock.__contains__.return_value = True
    query_params_mock.__getitem__.return_value = "test_auth_code"
    
    # Configure Clerk credentials
    env_mock = {
        "CLERK_CLIENT_ID": "client123",
        "CLERK_CLIENT_SECRET": "secret123",
        "CLERK_DOMAIN": "test.clerk.accounts.dev",
        "CLERK_REDIRECT_URI": "http://localhost:8501/"
    }
    
    # Mock token exchange response
    token_response = MagicMock()
    token_response.status_code = 200
    token_response.json.return_value = {"access_token": "access_token_123"}
    
    # Mock userinfo response
    userinfo_response = MagicMock()
    userinfo_response.status_code = 200
    userinfo_response.json.return_value = {"email": "test.user@clerk.dev"}
    
    # Mock OIDC configuration discovery
    discovery_response = MagicMock()
    discovery_response.status_code = 200
    discovery_response.json.return_value = {
        "authorization_endpoint": "https://test.clerk.accounts.dev/oauth/authorize",
        "token_endpoint": "https://test.clerk.accounts.dev/oauth/token",
        "userinfo_endpoint": "https://test.clerk.accounts.dev/oauth/userinfo"
    }

    session_state_mock = MockSessionState()
    
    def mock_requests_get(url, *args, **kwargs):
        if ".well-known/openid-configuration" in url:
            return discovery_response
        elif "oauth/userinfo" in url:
            return userinfo_response
        return MagicMock(status_code=404)

    with patch.dict(os.environ, env_mock), \
         patch.object(st, "secrets", {}), \
         patch.object(st, "query_params", query_params_mock), \
         patch.object(st, "session_state", session_state_mock), \
         patch("requests.post", return_value=token_response), \
         patch("requests.get", side_effect=mock_requests_get), \
         patch("streamlit.switch_page") as mock_switch_page:
         
        handle_clerk_callback()
        
        assert session_state_mock.get("logged_in") is True
        assert session_state_mock.get("email") == "test.user@clerk.dev"
        query_params_mock.clear.assert_called_once()  # query_params.clear should be called
        mock_switch_page.assert_called_once_with("pages/dashboard.py")
