"""Utility helpers for Supabase Google OAuth in Streamlit."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Tuple

import streamlit as st
from supabase import Client, create_client


class SupabaseAuthConfigError(RuntimeError):
    """Raised when required Supabase credentials are missing."""


@dataclass(frozen=True)
class SupabaseAuthConfig:
    url: str
    anon_key: str
    redirect_url: str


def _get_setting(key: str) -> str | None:
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key)


def load_supabase_config() -> SupabaseAuthConfig:
    url = _get_setting("SUPABASE_URL")
    anon_key = _get_setting("SUPABASE_ANON_KEY")
    redirect_url = _get_setting("SUPABASE_REDIRECT_URL") or "http://localhost:8501"

    missing = [
        name
        for name, value in {
            "SUPABASE_URL": url,
            "SUPABASE_ANON_KEY": anon_key,
        }.items()
        if not value
    ]

    if missing:
        raise SupabaseAuthConfigError(
            "Missing configuration: "
            + ", ".join(missing)
            + ". Add them to .streamlit/secrets.toml or environment variables."
        )

    return SupabaseAuthConfig(url=url, anon_key=anon_key, redirect_url=redirect_url)


@st.cache_resource(show_spinner=False)
def _supabase_client(url: str, anon_key: str) -> Client:
    return create_client(url, anon_key)


def init_supabase_google_auth() -> Tuple[Client, SupabaseAuthConfig]:
    """Return a cached Supabase client and config, after handling the OAuth callback."""

    config = load_supabase_config()
    client = _supabase_client(config.url, config.anon_key)
    handle_oauth_callback(client)
    return client, config


def build_google_login_url(client: Client, redirect_url: str) -> str:
    response = client.auth.sign_in_with_oauth(
        {
            "provider": "google",
            "options": {
                "redirect_to": redirect_url,
            },
        }
    )
    return response.url


def _first_value(value):
    if isinstance(value, list):
        return value[0]
    return value


def handle_oauth_callback(client: Client) -> None:
    params = st.query_params

    error_description = _first_value(params.get("error_description"))
    if error_description:
        st.error(error_description)
        return

    auth_code = _first_value(params.get("code"))
    if not auth_code or "supabase_session" in st.session_state:
        return

    with st.spinner("Signing you in..."):
        try:
            response = client.auth.exchange_code_for_session({"auth_code": auth_code})
        except Exception as exc:  # pragma: no cover - surface unexpected auth issues
            st.error(f"Could not exchange auth code: {exc}")
            return

    if response.session:
        store_session(response.session)
        params.clear()


def store_session(session) -> None:
    st.session_state["supabase_session"] = {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "expires_in": session.expires_in,
        "token_type": session.token_type,
        "user": {
            "id": session.user.id,
            "email": session.user.email,
            "user_metadata": session.user.user_metadata,
        },
    }


def get_session() -> Dict[str, Any] | None:
    return st.session_state.get("supabase_session")


def is_authenticated() -> bool:
    return "supabase_session" in st.session_state


def logout_user(client: Client) -> None:
    try:
        client.auth.sign_out()
    finally:
        st.session_state.pop("supabase_session", None)
        st.query_params.clear()


__all__ = [
    "SupabaseAuthConfig",
    "SupabaseAuthConfigError",
    "build_google_login_url",
    "get_session",
    "init_supabase_google_auth",
    "is_authenticated",
    "logout_user",
]