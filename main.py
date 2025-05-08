import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Load the config from YAML
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Set up Streamlit page
st.set_page_config(page_title="StackUp - Login Debug")

# Setup authenticator
authenticator = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    key=config['cookie']['key'],
    expiry_days=config['cookie']['expiry_days']
)

# Perform login
login_result = authenticator.login(location='main', fields={'title': 'Login'})

# DEBUG: show the raw login result (only for dev)
st.write("Login result:", login_result)

# Handle result correctly
if login_result is None:
    st.warning("Please log in.")
    st.stop()
else:
    name, auth_status, username = login_result

    if auth_status is False:
        st.error("Login failed. Please check your credentials.")
        st.stop()
    elif auth_status is True:
        authenticator.logout("Logout", "sidebar")
        st.sidebar.success(f"Welcome, {name}")
        st.success("Login successful!")

        # Your app logic goes here
        st.title("StackUp Dashboard")
        st.write("Upload your investment CSV to begin...")