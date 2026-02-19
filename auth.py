import streamlit as st
import os
from dotenv import load_dotenv

def initialize_auth():
    load_dotenv()
    users = {
        "sema": {"password": os.getenv("SEMA_PASSWORD"), "role": "engineer"},
        "admin": {"password": os.getenv("ADMIN_PASSWORD"), "role": "admin"},
        "eren": {"password": os.getenv("EREN_PASSWORD"), "role": "HR"}
    }
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    return users

def login_screen(users):
    if not st.session_state.get("logged_in", False):
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            st.write("<br><br>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center;'>🚂 Alstom Knowledge Assistant System</h1>", unsafe_allow_html=True)
            with st.form("login_form"):
                u_name = st.text_input("Username").lower().strip()
                u_pass = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login", type="primary", use_container_width=True):
                   
                    if not u_name or not u_pass:
                        st.error("Please enter both username and password.")
                    elif u_name in users and users[u_name]["password"] == u_pass:
                        
                        prev_user = st.session_state.get("username")
                        if prev_user and prev_user != u_name:
                            st.session_state.messages = []
                        
                        
                        st.session_state.username = u_name
                        st.session_state.role = users[u_name]["role"]
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("Invalid credentials!")
        
        st.stop()