import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# Load config
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Set page title
st.set_page_config(page_title="StackUp Login Test")

# Authenticator setup
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Login
auth_result = authenticator.login(location='main', fields={'title': 'Login'})

# Result check
if auth_result:
    name, auth_status, username = auth_result

    if auth_status:
        authenticator.logout("Logout", "sidebar")
        st.sidebar.success(f"Logged in as {name}")
        st.success("You are now logged in!")
        st.write("Welcome to StackUp 🚀")
    elif auth_status is False:
        st.error("Invalid credentials. Try again.")
    elif auth_status is None:
        st.warning("Please enter your credentials.")
else:
    st.warning("Please log in.")