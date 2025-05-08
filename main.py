import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# Load config
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Page config
st.set_page_config(page_title="StackUp Login Test")

# Authenticator setup
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Clear broken session cookies if present
if 'authentication_status' in st.session_state:
    del st.session_state['authentication_status']
    if 'name' in st.session_state:
        del st.session_state['name']
    if 'username' in st.session_state:
        del st.session_state['username']

# Login
name, auth_status, username = authenticator.login('Login', 'main')

# This check avoids the "name not defined" error if the session is broken
if auth_status is None and 'authentication_status' not in st.session_state:
    st.warning("Session is invalid or expired. Please refresh and login again.")
    st.stop()

# Handle login result
if auth_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.success(f"Welcome {name}!")
    st.success("You are now logged in.")
elif auth_status is False:
    st.error("Invalid username or password.")
elif auth_status is None:
    st.warning("Please log in.")