import streamlit as st
import os
from streamlit.runtime.scriptrunner_utils.exceptions import StopException

from langsmith import traceable

st.set_page_config(layout="wide")

from utils.supabase_integration import SupabaseClient
import pandas as pd

#from src.show_students_page import show_students_page
#from src.show_student_email_calendar import show_student_email_calendar
#from src.show_gmail_creds_page import show_gmail_creds_page
#from src.show_search_page import show_search_page
#from src.show_zoom_session_page import show_zoom_session_page, show_zoom_detail_page
#from src.show_instructors_page import show_instructors_page
#from src.show_gmail_fetch_control import show_gmail_fetch_control
#from src.show_fetch_zoom_aws import show_fetch_zoom_aws
    
def show_events_all():
    st.title("Events all page")
    
def page1():
    st.title("Page 1")
    
def page2():
    st.title("Page 2")
    
def page3():
    st.title("Page 3")
    
def page4():
    st.title("Page 4")
    
def page5():
    st.title("Page 5")

def show_sidebar_ui(user):
    name = user.get("name", "Unknown User")
    email = user.get("email", "Unknown Email")
    picture = user.get("picture", "")
    email_verified = user.get("email_verified", False)
    with st.sidebar:
        st.text(f"Welcome {name}\n {email}")
        if email_verified:
            st.success("Email is verified.")
        else:
            st.warning("Email is not verified.")
        if picture:
            st.image(picture, width=100)

def show_ui_core(user):
    show_sidebar_ui(user)
    
    pages = {
        "Core - Group 1": [
            st.Page(page1, title="Page 1"),
        ],
        "Core - Group 2": [
            st.Page(page2, title="Page 2"),
        ],
        "Core - Group 3": [
            st.Page(page3, title="Page 3"),
        ],
        "Core - Group 4": [
            st.Page(page4, title="Page 4"),
            st.Page(page5, title="Page 5"),
        ],

    }

    pg = st.navigation(pages, position="top")
    try:
        pg.run()
    except StopException:
        # Streamlit uses StopException internally to control reruns/navigation
        # Swallow it so it doesn't get surfaced to external tracers/loggers
        return
  
def show_ui_superadmin(user):
    show_sidebar_ui(user)
    #st.title("Admin Panel")
    #st.write("This is the admin panel. More features coming soon!")
    pages = {
        "Super-1": [
            st.Page(page1, title="Page 1"),
        ],
        "Super-2": [
            st.Page(page2, title="Page 2"),
        ],
        "Super-3": [
            st.Page(page3, title="Page 3"),
        ],
        "Super-4": [
            st.Page(page4, title="Page 4"),
            st.Page(page5, title="Page 5"),
        ],
    }
    pg = st.navigation(pages, position="top")
    try:
        pg.run()
    except StopException:
        return
   
def show_ui_admin(user):
    show_sidebar_ui(user)
    
    pages = {
        "Admin-Group 1": [
            st.Page(page1, title="Page 1"),
        ],
        "Admin-Group 2": [
            st.Page(page2, title="Page 2"),
        ],
        "Admin-Group 3": [
            st.Page(page3, title="Page 3"),
            #st.Page(show_instructors_page, title="Instructors"),
            #st.Page(page1, title="GMail Fetch"),
        ],
        "Admin - Group 4": [
            st.Page(page4, title="Page 4"),
            st.Page(page5, title="Page 5"),
            #st.Page(page3, title="Fetch AWS"),
        ],

    }

    pg = st.navigation(pages, position="top")
    try:
        pg.run()
    except StopException:
        return

def show_ui_guest(user):
    st.title("Guest Access")
    st.write(f"You do not have access. Please reach out to System Administrator with your information\n Email: {user.get("email", "Unknown Email")}.")

@traceable(run_type="tool")
def show_ui_user(user):
    #st.title("User Access")
    #st.write("Welcome to the user panel. More features coming soon!")
    show_ui_core(user)

def show_ui_base(user_orig,user_meta):
    user=user_meta
    if user and user.get("email_verified", False):
        supabase = SupabaseClient(url=os.environ["SUPABASE_URL"], key=os.environ['SUPABASE_ANON_KEY'])
        if supabase:
            user_record = supabase.get_user_from_db(user['email'])
            #st.write(user_record)
            #print(f"{user_record=}")
            if not user_record:
                role = "guest"
                show_ui_guest(user)
                return
            role= user_record.get("role", "guest")
            if role == "superadmin":
                show_ui_superadmin(user)
            elif role == "admin":
                show_ui_admin(user)
            elif role == "user":
                show_ui_user(user)
            elif role == "guest":
                show_ui_guest(user)
            else:
                st.error(f"Unknown role: {role}. Please contact the administrator.")
        else:
            st.error("Could not connect to Supabase.")
    else:
        st.warning("Please log in with a verified email to access the app.")
        st.sidebar.json(user)