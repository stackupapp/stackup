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

# Login (for streamlit-authenticator v0.2.3)
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