"""Streamlit UI layer for the Supabase Google login demo."""

from __future__ import annotations

import streamlit as st
from supabase import Client

from utils.auth_supabase_google import get_session,try_login,logout_user
from src.verified_ui import show_ui_base

def show_ui(client: Client) -> None:
    session = get_session()
    
    if session:
        user = session["user"]
        show_ui_base(user, user['user_metadata'])
        #st.success(f"{user['email']}")

        #with st.sidebar.expander("Session details"):
        #    st.json(session)    
    else:
        st.warning("Session expired. Please sign in again.")

    if st.sidebar.button("Log out"):
        logout_user(client)



def main() -> None:
    st.set_page_config(page_title="Supabase Google Login")
    try_login(show_ui)

if __name__ == "__main__":
    main()