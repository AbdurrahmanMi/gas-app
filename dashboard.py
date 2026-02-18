import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import streamlit as st

DATABASE_URL = "https://house-sensor-data-9fef3-default-rtdb.firebaseio.com/"

if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": DATABASE_URL
    })

st.title("Gas Sensor Dashboard")

ref = db.reference("gas_history")
data = ref.get()

if data:
    df = pd.DataFrame.from_dict(data, orient="index")

    df.index = pd.to_datetime(df.index, format="%Y-%m-%d_%H:%M:%S")
    df = df.sort_index()

    st.line_chart(df["gas_value"])
else:
    st.warning("No data found")
