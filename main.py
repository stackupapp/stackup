import streamlit as st
import bcrypt

# --- Hardcoded users with hashed passwords ---
credentials = {
    "usernames": {
        "jeevan": {
            "email": "jeevan@example.com",
            "name": "Jeevan",
            "password": "$2b$12$Pkeip3gvqSqFSPWhBqqZBOGtAIDSzrrb0m/iwATtBpPc8ha7.NH8u"
        },
        "admin": {
            "email": "admin@example.com",
            "name": "Admin",
            "password": "$2b$12$DtVoayZDXOoWcx3xEeYMXecQokGF2Yohmv4tps235cJBfebaRXxma"
        }
    }
}

# --- Initialize session state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- Logged-in UI ---
if st.session_state.logged_in:
    st.sidebar.success(f"Welcome, {st.session_state.username}!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()
    st.title("StackUp Portfolio Dashboard")
    st.write("Upload your CSVs and view analysis here.")

# --- Login UI ---
else:
    st.title("Login to StackUp")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user_record = credentials["usernames"].get(username)
        if user_record and bcrypt.checkpw(password.encode(), user_record["password"].encode()):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")