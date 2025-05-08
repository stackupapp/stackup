import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os

# --- Load credentials from YAML config ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# --- Page config ---
st.set_page_config(page_title="StackUp - Portfolio Analyzer")

# --- Authenticator setup ---
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# --- Login form ---
result = authenticator.login(location='main', fields={'title': 'Login'})
if result is None:
    st.error("Login failed. Please check your credentials.")
    st.stop()
else:
    name, auth_status, username = result

# --- Authentication logic ---
if auth_status is False:
    st.error("Invalid username or password.")
    st.stop()
elif auth_status is None:
    st.warning("Please log in.")
    st.stop()
else:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Logged in as: {name}")

# --- Main app content ---
st.title("StackUp: Investment Portfolio Analyzer")
st.write("Upload one or more CSV files from Thinkorswim, IBKR, or Robinhood. This app will detect, parse, and analyze your investments.")

uploaded_files = st.file_uploader("Upload one or more investment CSV files", type=["csv"], accept_multiple_files=True)
combined_df = pd.DataFrame()

def detect_platform(columns):
    cols = set(columns)
    if {"Instrument", "Qty", "Trade Price", "Mark"}.issubset(cols):
        return "Thinkorswim"
    elif {"Symbol", "Quantity", "Price", "Market Value", "Cost Basis"}.issubset(cols):
        return "Robinhood"
    elif {"Symbol", "Buy/Sell", "Quantity", "T. Price", "Net Amount", "Market Price"}.issubset(cols):
        return "IBKR"
    return "Unknown"

def process_tos(df):
    df["Qty"] = df["Qty"].astype(str).str.replace("+", "", regex=False).astype(float)
    df["Trade Price"] = df["Trade Price"].astype(str).str.replace("$", "", regex=False).astype(float)
    df["Mark"] = df["Mark"].astype(str).str.replace("$", "", regex=False).astype(float)
    df["Invested"] = df["Qty"] * df["Trade Price"]
    df["Current Value"] = df["Qty"] * df["Mark"]
    df["Profit"] = df["Current Value"] - df["Invested"]
    df["Broker"] = "Thinkorswim"
    return df[["Instrument", "Qty", "Trade Price", "Mark", "Invested", "Current Value", "Profit", "Broker"]]

def process_robinhood(df):
    df["Invested"] = df["Cost Basis"]
    df["Current Value"] = df["Market Value"]
    df["Profit"] = df["Current Value"] - df["Invested"]
    df["Broker"] = "Robinhood"
    return df[["Symbol", "Quantity", "Price", "Invested", "Current Value", "Profit", "Broker"]]

def process_ibkr(df):
    df["T. Price"] = df["T. Price"].astype(float)
    df["Quantity"] = df["Quantity"].astype(float)
    df["Market Price"] = df["Market Price"].astype(float)
    df["Invested"] = df["Quantity"] * df["T. Price"]
    df["Current Value"] = df["Quantity"] * df["Market Price"]
    df["Profit"] = df["Current Value"] - df["Invested"]
    df["Broker"] = "IBKR"
    return df[["Symbol", "Quantity", "T. Price", "Market Price", "Invested", "Current Value", "Profit", "Broker"]]

if uploaded_files:
    all_data = []
    for file in uploaded_files:
        try:
            user_dir = os.path.join("data", str(username))
            os.makedirs(user_dir, exist_ok=True)
            file_path = os.path.join(user_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            df = pd.read_csv(file_path)
            platform = detect_platform(df.columns)
            if platform == "Thinkorswim":
                all_data.append(process_tos(df))
            elif platform == "Robinhood":
                all_data.append(process_robinhood(df))
            elif platform == "IBKR":
                all_data.append(process_ibkr(df))
            else:
                st.warning(f"Unsupported format in file: {file.name}")
        except Exception as e:
            st.error(f"Error processing {file.name}: {e}")

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
        st.write(f"Profit/Loss: ${total_profit:,.2f}")

        # Pie chart
        symbol_col = "Symbol" if "Symbol" in combined_df.columns else "Instrument"
        allocation = combined_df.groupby(symbol_col)["Current Value"].sum().reset_index()
        fig = px.pie(allocation, names=symbol_col, values="Current Value", title="Asset Allocation by Value")
        st.plotly_chart(fig)

        # Download CSV
        csv_data = combined_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Combined Portfolio", data=csv_data, file_name="portfolio_summary.csv", mime="text/csv")
else:
    st.info("No valid investment data uploaded.")