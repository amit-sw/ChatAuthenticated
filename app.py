"""Streamlit UI layer for the Supabase Google login demo."""

from __future__ import annotations

import streamlit as st
from supabase import Client

from utils.auth_supabase_google import (
    SupabaseAuthConfigError,
    build_google_login_url,
    get_session,
    init_supabase_google_auth,
    is_authenticated,
    logout_user,
)


def show_login_screen(client: Client, redirect_url: str) -> None:
    st.header("Supabase + Google Login")
    st.write("Sign in to unlock the rest of the app.")

    try:
        login_url = build_google_login_url(client, redirect_url)
    except Exception as exc:  # pragma: no cover - surfacing Supabase config issues
        st.error(f"Unable to create Google login link: {exc}")
        return

    st.link_button("Continue with Google", url=login_url, type="primary")
    st.caption("The button opens the Supabase hosted Google consent screen.")


def show_profile(client: Client) -> None:
    session = get_session()
    if not session:
        st.warning("Session expired. Please sign in again.")
        return

    user = session["user"]
    st.success(f"Signed in as {user['email']}")

    with st.expander("Session details"):
        st.json(session)

    if st.button("Log out"):
        logout_user(client)


def main() -> None:
    st.set_page_config(page_title="Supabase Google Login")

    try:
        client, config = init_supabase_google_auth()
    except SupabaseAuthConfigError as exc:
        st.error(str(exc))
        st.stop()

    if is_authenticated():
        show_profile(client)
    else:
        show_login_screen(client, config.redirect_url)


if __name__ == "__main__":
    main()