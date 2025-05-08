import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# --- Load config.yaml ---
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# --- Set page config ---
st.set_page_config(page_title="StackUp - Portfolio Analyzer")

# --- Setup Authenticator ---
authenticator = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    key=config['cookie']['key'],
    expiry_days=config['cookie']['expiry_days']
)

# --- Render Login Form ---
login_result = authenticator.login(location='main', fields={'title': 'Login'})

# --- Handle Login Output ---
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
        st.sidebar.success(f"Welcome, {name} 👋")
        st.success("You are now logged in!")

        # 👇 App content here after login
        st.title("Welcome to StackUp 🚀")
        st.write("This is your investment analysis dashboard.")