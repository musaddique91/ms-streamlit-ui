import streamlit as st
from supabase import create_client
from st_pages.home import show_home
from st_pages.analytics import show_analytics
from st_pages.predictions import show_predictions
from st_pages.login import show_login
from st_pages.history import show_history
from st_pages.personal import show_personal
from streamlit_option_menu import option_menu
from st_pages.entertainment import show_entertainment
from st_pages.file_chat import process_chat
from st_pages.plan_trip import plan_trip
# Initialize Supabase client
#supabase = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_API_KEY'))
supabase = create_client('https://pcadpemmgbywzgywuovc.supabase.co', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBjYWRwZW1tZ2J5d3pneXd1b3ZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAzNzk1OTEsImV4cCI6MjA1NTk1NTU5MX0.I_gDj1CtMRoQ_NUBY9nTeWk3-yEo9aQenEuOBL1nSfk')

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

# Check if user is already authenticated
if 'supabase_access_token' in st.session_state:
    try:
        user = supabase.auth.get_user(st.session_state.supabase_access_token)
        st.session_state.authenticated = True
        st.session_state.user = user
    except Exception:
        st.session_state.authenticated = False
        st.session_state.user = None

# Page configuration
st.set_page_config(
    page_title="Data Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

def main():
    # Sidebar
    with st.sidebar:
        st.title("Musa-AI")
        page = option_menu("Main Menu", ["Home", "Analytics", "Predictions", "Entertainment","File Chat", "Personal", "History", "Plan My Trip"],
        icons=['house-fill', 'bar-chart-fill','globe','camera-reels-fill','chat-dots-fill','person-fill','clock-history'], menu_icon="cast", default_index=0)
       
        if not st.session_state.authenticated:
            if st.button("Login", key="nav_btn_login"):
                page = "Login"
        else:
            st.write(f"Logged in as: {st.session_state.user.email}")
            if st.button("Logout", key="nav_btn_logout"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.pop('supabase_access_token', None)
                st.rerun()
    # Main content
    if page == "Login":
        show_login()
    elif page == "Home":
        show_home()
    elif page == "Analytics":
        show_analytics()
    elif page == "Predictions":
        show_predictions()
    elif page == 'Entertainment':
        print("calling Entertainment")
        show_entertainment()
    elif page == 'File Chat':
        print("calling File Chat")
        process_chat()
    elif page == "Personal":
        if st.session_state.authenticated:
            show_personal()
        else:
            st.warning("Please log in to access your personal dashboard.")
            show_login()
    elif page == "History":
        if st.session_state.authenticated:
            show_history()
        else:
            st.warning("Please log in to view your history.")
            show_login()
    elif page == "Plan My Trip":
        print("calling Plan My Trip")
        plan_trip()
if __name__ == "__main__":
    main()