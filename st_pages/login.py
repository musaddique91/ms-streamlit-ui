import streamlit as st
from supabase import create_client
import os

#supabase = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_API_KEY'))
supabase = create_client('https://pcadpemmgbywzgywuovc.supabase.co', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBjYWRwZW1tZ2J5d3pneXd1b3ZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAzNzk1OTEsImV4cCI6MjA1NTk1NTU5MX0.I_gDj1CtMRoQ_NUBY9nTeWk3-yEo9aQenEuOBL1nSfk')

def is_authenticated():
    return st.session_state.authenticated
def show_login():
    st.title("Login")
    st.write("Log in to access your personal dashboard and view your analysis history.")
    
    # Create tabs for login and signup
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        email = st.text_input("👤 Email", placeholder="Enter your Username/Email", key="login_email")
        password = st.text_input("🔑 Password",placeholder="Enter your password", type="password", key="login_password")
        
        if st.button("Login", key="btn_login"):
            try:
                response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state.authenticated = True
                st.session_state.user = response.user
                st.session_state.supabase_access_token = response.session.access_token
                st.success("✅ Successfully logged in!")
                st.rerun()
            except Exception as e:
                st.error("⚠️ Login failed. Please check your credentials.")
    
    with tab2:
        new_email = st.text_input("👤 Email", key="signup_email")
        new_password = st.text_input("🔑 Password", type="password", key="signup_password")
        confirm_password = st.text_input("🔑 Confirm Password", type="password")
        
        if st.button("Sign Up", key="btn_logout"):
            if new_password != confirm_password:
                st.error("Passwords do not match!")
            else:
                try:
                    response = supabase.auth.sign_up({
                        "email": new_email,
                        "password": new_password
                    })
                    st.success("Account created successfully! Please check your email for verification.")
                except Exception as e:
                    st.error(f"Sign up failed: {str(e)}")

