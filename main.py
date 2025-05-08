import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# Load config.yaml
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Page config
st.set_page_config(page_title="StackUp Login")

# Authenticator setup
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Prevent KeyError by initializing session keys
for key in ['authentication_status', 'name', 'username']:
    if key not in st.session_state:
        st.session_state[key] = None

# Handle broken cookies from previous crash
if st.session_state['authentication_status'] is None and 'authentication_status' in st.session_state:
    del st.session_state['authentication_status']
    del st.session_state['name']
    del st.session_state['username']

# Show login form
name, auth_status, username = authenticator.login('Login', 'main')

# Handle login result
if auth_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.success(f"Welcome {name}!")
    st.success("You are now logged in.")
elif auth_status is False:
    st.error("Invalid username or password.")
elif auth_status is None:
    st.warning("Please log in.")