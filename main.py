import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Load YAML config
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Authenticator setup
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Login form
auth_result = authenticator.login(location='main', fields={'title': 'Login'})

# Handle login result
if auth_result is not None:
    name, auth_status, username = auth_result

    if auth_status is False:
        st.error("Invalid username or password.")
    elif auth_status is None:
        st.warning("Please log in.")
    else:
        authenticator.logout("Logout", "sidebar")
        st.sidebar.success(f"Logged in as: {name}")
        st.title("StackUp Investment Analyzer")
        st.write("Upload your CSV files here and begin analysis.")
else:
    st.warning("Please log in.")