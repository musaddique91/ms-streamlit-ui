import streamlit as st
from entertain import faceart
from entertain import deepface

def show_entertainment():
    st.title("The Smiley Show. Laugh & Chill")
    # Create tabs for different analytics views
    tabs = st.tabs(["Face Details", "Face -> Ascii Art"])
    if tabs:
        with tabs[0]:
            deepface.show_deepface_page()
        with tabs[1]:
            faceart.face_to_ascii()