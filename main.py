import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Load config from config.yaml
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Page config
st.set_page_config(page_title="StackUp Login Test")

# Setup authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Display login form
name, auth_status, username = authenticator.login(form_name='Login', location='main')
# Handle login outcome
if auth_status is True:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.success(f"Welcome {name}!")
    st.success("You are now logged in.")
elif auth_status is False:
    st.error("Invalid username or password.")
elif auth_status is None:
    st.warning("Please log in.")