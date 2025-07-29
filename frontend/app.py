import streamlit as st
from datetime import date
from dotenv import load_dotenv
import os
import pandas as pd
import pydeck as pdk
import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from backend.etl import fetch_and_store_permits
from backend.db import supabase

# Load .env (optional if already done in db.py)
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Page config
st.set_page_config(page_title="NYC Permit Dashboard", layout="centered")
st.title(" NYC Permit Data Dashboard")

# --- Login ---
st.header(" Log In")
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if email and password:
    st.session_state["user_email"] = email

# --- Search Filters ---
st.header("📄 Permit Search Filters")
city = st.selectbox("City", ["New York City", "San Francisco", "Chicago"])
property_type = st.selectbox("Property Type", ["Residential", "Commercial"])
work_category = st.selectbox("Work Category", ["Building", "HVAC", "Mechanical", "Electrical"])
zip_code = st.text_input("ZIP Code (optional)")
permit_type = st.selectbox("Permit Type", ["General Construction", "Sidewalk Shed"], key="permit_type")
property_type = st.selectbox("Property Type", ["Residential", "Commercial"], key="property_type")
work_category = st.selectbox("Work Category", ["Building", "Mechanical", "HVAC", "Electrical"])
start_date = st.date_input("Start Date", value=date(2024, 1, 1))
end_date = st.date_input("End Date", value=date.today())

# --- Submit Button ---
if st.button("Submit"):
    if "user_email" not in st.session_state:
        st.warning("Please log in before submitting.")
    else:
        with st.spinner(" Fetching and processing permits..."):
            result = fetch_and_store_permits(
                permit_type,
                str(start_date),
                str(end_date),
                st.session_state["user_email"],
                city,
                zip_code,
                property_type,
                work_category
            )
            st.success(result)

        # --- Fetch results for user ---
        st.subheader(" Results for You")
        response = supabase.table("permits").select("*").eq("user_email", st.session_state["user_email"]).execute()
        data = response.data

        st.write(" Logged-in email:", st.session_state["user_email"])
        st.write(" Raw Supabase data fetched:", data)

        # --- Debug ---
        st.subheader("🛠 Latest 5 permits (debug)")
        debug = supabase.table("permits").select("*").order("issued_date", desc=True).limit(5).execute()
        st.write(debug.data)

        if not data:
            st.warning("No data found.")
        else:
            df = pd.DataFrame(data)
            st.success(f" Loaded {len(df)} permits.")

            if "latitude" in df and "longitude" in df:
                df = df.dropna(subset=["latitude", "longitude"])
                st.map(df[["latitude", "longitude"]])

            st.subheader(" Permit Table")
            st.dataframe(df)

