import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
from datetime import datetime
import time

# ---------------- Firebase ----------------

firebase_config = dict(st.secrets["firebase"])

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(
        cred,
        {"databaseURL": firebase_config["databaseURL"]}
    )

# ---------------- Page Config ----------------

st.set_page_config(page_title="Gas Dashboard", layout="wide")
st.title("🔥 Gas Sensor Live Dashboard")

# ---------------- Read Data ----------------

ref = db.reference("gas_history")
data = ref.get()

if not data:
    st.warning("No data found.")
else:
    df = pd.DataFrame.from_dict(data, orient="index")

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

    st.subheader("Gas Level Over Time")
    st.line_chart(df["gas_value"])

    with st.expander("Show Raw Data"):
        st.dataframe(df)

# ---------------- Auto Refresh ----------------

time.sleep(10)
st.rerun()
