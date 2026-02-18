import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import time

# =====================================================
# LOGIN SYSTEM
# =====================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.set_page_config(page_title="Login", layout="centered")
    st.title("🔐 Gas Dashboard Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if (
            username == st.secrets["auth"]["username"]
            and password == st.secrets["auth"]["password"]
        ):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong username or password")

    st.stop()

# =====================================================
# FIREBASE INITIALIZATION
# =====================================================

firebase_config = dict(st.secrets["firebase"])

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(
        cred,
        {"databaseURL": firebase_config["databaseURL"]}
    )

# =====================================================
# DASHBOARD UI
# =====================================================

st.set_page_config(page_title="Gas Dashboard", layout="wide")

col_title, col_logout = st.columns([8, 1])

with col_title:
    st.title("🔥 Gas Sensor Live Dashboard")

with col_logout:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# =====================================================
# READ DATA FROM FIREBASE
# =====================================================

ref = db.reference("gas_history")
data = ref.get()

if not data:
    st.warning("No data found in Firebase.")
else:
    df = pd.DataFrame.from_dict(data, orient="index")

    # Convert index to datetime
    df.index = pd.to_datetime(df.index, format="%Y-%m-%d_%H:%M:%S")
    df = df.sort_index()

    latest_value = df["gas_value"].iloc[-1]

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Current Gas Value", int(latest_value))

    with col2:
        if latest_value > 1500:
            st.error("⚠️ Gas Level HIGH!")
        else:
            st.success("Gas Level Normal")

    st.subheader("📊 Gas Level Over Time")
    st.line_chart(df["gas_value"])

    with st.expander("Show Raw Data"):
        st.dataframe(df)

# =====================================================
# AUTO REFRESH EVERY 10 SECONDS
# =====================================================

time.sleep(10)
st.rerun()
