import streamlit as st
import pandas as pd
import plotly.express as px

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os

# User config stored in YAML format (2 test users)
user_config = {
    'credentials': {
        'usernames': {
            'jeevan': {
                'email': 'jeevan@example.com',
                'name': 'Jeevan',
                'password': '$2b$12$kVhv6eQWZwOzPln8Z1OKoeBEVWwOhVcQtVsdxmwNdqZZP75k/o2fa'
            },
            'admin': {
                'email': 'admin@example.com',
                'name': 'Admin',
                'password': '$2b$12$ncTEXq/yI/jwruRr70n9du9oY1C36P.fx29DjygKkoDZ662nKV16a'
            }
        }
    },
    'cookie': {
        'name': 'stackup_session',
        'key': 'abc123_secret_key',  # Replace with real key in prod
        'expiry_days': 1
    },
}

# Initialize the authenticator object
authenticator = stauth.Authenticate(
    user_config['credentials'],
    user_config['cookie']['name'],
    user_config['cookie']['key'],
    user_config['cookie']['expiry_days']
)

# Display login box and check result
auth_result = authenticator.login(location='main', fields={'title': 'Login'})
st.write("auth_result =", auth_result)  # DEBUG LINE

if auth_result is not None:
    name, authentication_status, username = auth_result
    if authentication_status is False:
        st.error("Invalid username or password.")
        st.stop()
    elif authentication_status is True:
        authenticator.logout("Logout", "sidebar")
        st.sidebar.success(f"Logged in as: {name}")
    else:
        st.warning("Please log in.")
        st.stop()
else:
    st.warning("Please log in.")
    st.stop()
    
combined_df = pd.DataFrame()  # Define empty DataFrame in advance
# Set page config
st.set_page_config(page_title="StackUp - Portfolio Analyzer")

st.title("StackUp: Investment Portfolio Analyzer")
st.write("Upload one or more CSV files from Thinkorswim, IBKR, or Robinhood. This app will detect, parse, and analyze your investments.")

uploaded_files = st.file_uploader("Upload one or more investment CSV files", type=["csv"], accept_multiple_files=True)

# Platform detection based on header fields
def detect_platform(columns):
    cols = set(columns)
    if {"Instrument", "Qty", "Trade Price", "Mark"}.issubset(cols):
        return "Thinkorswim"
    elif {"Symbol", "Quantity", "Price", "Market Value", "Cost Basis"}.issubset(cols):
        return "Robinhood"
    elif {"Symbol", "Buy/Sell", "Quantity", "T. Price", "Net Amount", "Market Price"}.issubset(cols):
        return "IBKR"
    else:
        return "Unknown"

# Process Thinkorswim
def process_tos(df):
    df["Qty"] = df["Qty"].astype(str).str.replace("+", "", regex=False).astype(float)
    df["Trade Price"] = df["Trade Price"].astype(str).str.replace("$", "", regex=False).astype(float)
    df["Mark"] = df["Mark"].astype(str).str.replace("$", "", regex=False).astype(float)

    df["Invested"] = df["Qty"] * df["Trade Price"]
    df["Current Value"] = df["Qty"] * df["Mark"]
    df["Profit"] = df["Current Value"] - df["Invested"]
    df["Broker"] = "Thinkorswim"

    return df[["Instrument", "Qty", "Trade Price", "Mark", "Invested", "Current Value", "Profit", "Broker"]]

# Process Robinhood
def process_robinhood(df):
    df["Invested"] = df["Cost Basis"]
    df["Current Value"] = df["Market Value"]
    df["Profit"] = df["Current Value"] - df["Invested"]
    df["Broker"] = "Robinhood"

    return df[["Symbol", "Quantity", "Price", "Invested", "Current Value", "Profit", "Broker"]]

# Process IBKR
def process_ibkr(df):
    df["T. Price"] = df["T. Price"].astype(float)
    df["Quantity"] = df["Quantity"].astype(float)
    df["Market Price"] = df["Market Price"].astype(float)

    df["Invested"] = df["Quantity"] * df["T. Price"]
    df["Current Value"] = df["Quantity"] * df["Market Price"]
    df["Profit"] = df["Current Value"] - df["Invested"]
    df["Broker"] = "IBKR"

    return df[["Symbol", "Quantity", "T. Price", "Market Price", "Invested", "Current Value", "Profit", "Broker"]]

# Main logic to handle all uploaded files
if uploaded_files:
    all_data = []

    for file in uploaded_files:
        try:
            # Create user-specific folder if it doesn't exist
            user_dir = os.path.join("data", str(username))
            os.makedirs(user_dir, exist_ok=True)

            # Save uploaded file into that user's folder
            file_path = os.path.join(user_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

            # Now read the saved file
            df = pd.read_csv(file_path)
            platform = detect_platform(df.columns)

            st.write(f"Processing file: {file.name}")
            st.write(f"Detected platform: {platform}")

            if platform == "Thinkorswim":
                cleaned = process_tos(df)
                all_data.append(cleaned)
            elif platform == "Robinhood":
                cleaned = process_robinhood(df)
                all_data.append(cleaned)
            elif platform == "IBKR":
                cleaned = process_ibkr(df)
                all_data.append(cleaned)
            else:
                st.warning(f"Unsupported CSV format in file: {file.name}")

        except Exception as e:
            st.error(f"Error while processing {file.name}: {e}")

    # Combine and display portfolio summary
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)

        st.subheader("Combined Portfolio Overview")
        st.dataframe(combined_df)

        total_invested = combined_df["Invested"].sum()
        total_value = combined_df["Current Value"].sum()
        total_profit = combined_df["Profit"].sum()

        st.subheader("Portfolio Summary")
        st.write(f"Total Invested: ${total_invested:,.2f}")
        st.write(f"Current Value: ${total_value:,.2f}")
        st.write(f"Overall Profit/Loss: ${total_profit:,.2f}")


#if not combined_df.empty:
    st.subheader("Combined Portfolio Overview")
    st.dataframe(combined_df)

    total_invested = combined_df["Invested"].sum()
    total_value = combined_df["Current Value"].sum()
    total_profit = combined_df["Profit"].sum()

    st.subheader("Portfolio Summary")
    st.write(f"Total Invested: ${total_invested:,.2f}")
    st.write(f"Current Value: ${total_value:,.2f}")
    st.write(f"Overall Profit/Loss: ${total_profit:,.2f}")

    # PIE CHART
    st.subheader("Allocation by Symbol")
    if "Symbol" in combined_df.columns:
        group_col = "Symbol"
    elif "Instrument" in combined_df.columns:
        group_col = "Instrument"
    else:
        group_col = None

    if group_col:
        allocation = combined_df.groupby(group_col)["Current Value"].sum().reset_index()
        fig = px.pie(allocation, names=group_col, values="Current Value", title="Asset Allocation by Value")
        st.plotly_chart(fig)
    else:
        st.info("Allocation pie chart not available: no recognizable symbol field.")

    # DOWNLOAD BUTTON
    st.subheader("Download Your Combined Portfolio")
    csv_export = combined_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Combined Portfolio as CSV",
        data=csv_export,
        file_name="stackup_portfolio_summary.csv",
        mime="text/csv"
    )
else:
    st.info("No valid investment data was found in the uploaded files.")