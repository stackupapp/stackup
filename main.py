import streamlit as st
import bcrypt
import pandas as pd
from parsers import parse_tos, parse_ibkr, parse_robinhood
import yaml
from yaml.loader import SafeLoader
import matplotlib.pyplot as plt

# --- Fuzzy matching support without pip installs ---
try:
    from fuzzywuzzy import fuzz
    def fuzzy_score(a, b):
        return fuzz.ratio(a.lower(), b.lower())
except ImportError:
    from difflib import SequenceMatcher
    def fuzzy_score(a, b):
        return int(SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100)

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
# --- Load platform config ---
with open("platform_config.yaml", "r") as file:
    platform_config = yaml.load(file, Loader=SafeLoader)

# --- Custom Fuzzy Column Matcher ---
from difflib import SequenceMatcher

def fuzzy_column_match(df_columns, expected_to_final_map, threshold=0.7):
    """
    expected_to_final_map: Dict[str, str] -> keys are possible aliases, values are final unified column names
    """
    mapping = {}
    for alias, final_col in expected_to_final_map.items():
        best_match = None
        best_ratio = 0
        for actual_col in df_columns:
            ratio = SequenceMatcher(None, alias.lower(), actual_col.lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = actual_col
        if best_ratio >= threshold:
            mapping[best_match] = final_col
    return mapping

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

    # -------------------- Portfolio Upload & Processing --------------------
    
    # -- Utility: Try loading CSV even if it has some malformed header rows --
    def load_csv_with_fallback(file):
        from difflib import SequenceMatcher

        def fuzzy_ratio(a, b):
            return SequenceMatcher(None, a.lower(), b.lower()).ratio()

        for skip in range(0, 11):  # Try skipping 0 to 10 rows
            file.seek(0)
            try:
                df = pd.read_csv(file, skiprows=skip)
                df.columns = df.columns.str.strip()

                actual_cols = list(df.columns)
                for platform, config in platform_config['platforms'].items():
                    expected_cols = config['detection_columns']
                    match_count = 0

                    for expected_col in expected_cols:
                        for actual_col in actual_cols:
                            ratio = fuzzy_ratio(expected_col, actual_col)
                            if ratio >= 0.7:  # 70% match is good enough
                                match_count += 1
                                break

                    if match_count == len(expected_cols):
                        return df  # Valid header match

            except Exception:
                continue

        raise ValueError("Could not detect valid headers in CSV after skipping rows.")

    # -- Utility: Detect which platform the file came from --
    def detect_platform(df):
        detected_cols = df.columns

        for platform, config in platform_config['platforms'].items():
            required_cols = config['detection_columns']
            match_count = 0

            for req_col in required_cols:
                for actual_col in detected_cols:
                    score = fuzzy_score(req_col, actual_col)
                    if score >= 70:
                        match_count += 1
                        break

            if match_count == len(required_cols):
                return platform

        return "Unknown"
        
    # -- Utility: Normalize to a common structure --
    def normalize_dataframe(df, platform):
        if platform not in platform_config['platforms']:
            return pd.DataFrame()

        config = platform_config['platforms'][platform]
        column_mapping = config['column_mapping']  # alias → final_column_name
        actual_headers = list(df.columns)

        matched = fuzzy_column_match(actual_headers, column_mapping, threshold=0.7)

        if not matched:
            raise ValueError(f"Could not fuzzy match required headers for platform: {platform}")

        rename_map = matched  # already in {actual_col_in_csv: final_col} format
        st.info(f"🔍 Header mapping: {rename_map}")  # Optional for debug

        # Filter to required unified columns only (symbol, quantity, cost_basis, current_price)
        final_cols = ['symbol', 'quantity', 'cost_basis', 'current_price']
        return df.rename(columns=rename_map)[final_cols]

    def calculate_metrics(df):
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
        df['cost_basis'] = pd.to_numeric(df['cost_basis'], errors='coerce')
        df['current_price'] = pd.to_numeric(df['current_price'], errors='coerce')

        df['investment'] = df['quantity'] * df['cost_basis']
        df['current_value'] = df['quantity'] * df['current_price']
        df['pnl'] = df['current_value'] - df['investment']

        return df

    uploaded_files = st.file_uploader("Upload CSV Files", type=['csv'], accept_multiple_files=True)

    if uploaded_files:
        all_data = []

        for file in uploaded_files:
            try:
                df_raw = load_csv_with_fallback(file)
                platform = detect_platform(df_raw)

                if platform == 'Unknown':
                    st.warning(f"{file.name}: Unknown format. Skipping.")
                    continue
                st.warning(f"{file.name}: Detected columns: {list(df_raw.columns)}")
                normalized_df = normalize_dataframe(df_raw, platform)
                parsed_df = calculate_metrics(normalized_df)

                st.success(f"{file.name} ({platform}) - {len(parsed_df)} rows parsed successfully.")
                st.dataframe(parsed_df.head())

                all_data.append(parsed_df)

            except Exception as e:
                st.error(f"Failed to process {file.name}: {e}")

        if all_data:
            final_df = pd.concat(all_data, ignore_index=True)
            st.subheader("Combined Portfolio Overview")
            st.dataframe(final_df)

            total_investment = final_df['investment'].sum()
            total_value = final_df['current_value'].sum()
            total_pnl = final_df['pnl'].sum()

            st.metric("Total Investment", f"${total_investment:,.2f}")
            st.metric("Current Value", f"${total_value:,.2f}")
            st.metric("Total P&L", f"${total_pnl:,.2f}", delta_color="normal" if total_pnl >= 0 else "inverse")
            # --- Asset Allocation Pie Chart ---
            st.subheader("Asset Allocation by Symbol")

            allocation = final_df.groupby('symbol')['current_value'].sum()

            fig, ax = plt.subplots()
            ax.pie(
                allocation,
                labels=allocation.index,
                autopct='%1.1f%%',
                startangle=90
            )
            ax.axis('equal')
            st.pyplot(fig)
            st.download_button("⬇️ Download Combined CSV", data=final_df.to_csv(index=False), file_name="combined_portfolio.csv", mime='text/csv')

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