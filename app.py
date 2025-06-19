import streamlit as st
import pandas as pd
from geopy.distance import geodesic
import pydeck as pdk
import geocoder
import os
from datetime import datetime
from urllib.parse import quote
import joblib
import numpy as np

import streamlit as st
import yaml
import streamlit_authenticator as stauth

# Load the YAML config
with open('config.yaml') as file:
    config = yaml.safe_load(file)

# Setup the authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Login block
name, authentication_status, username = authenticator.login("Login", "main")

# Handle login states
if authentication_status is False:
    st.error("❌ Username or password is incorrect.")

elif authentication_status is None:
    st.warning("🔒 Please enter your credentials.")

elif authentication_status:
    # ✅ Login success — hide login and proceed
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"✅ Welcome, {name}!")

    try:
        user_role = config['credentials']['usernames'][username]['role']
    except KeyError:
        st.error("⚠️ User not found in config.")
        st.stop()

    # 👉 Now render your actual app below this point
    if user_role == "kitchen":
        st.header("🍽️ Kitchen Dashboard")
        # (Insert full kitchen app here)

    elif user_role == "ngo":
        st.header("🏥 NGO Dashboard")
        st.info("NGO dashboard coming soon!")

    

user_role = config['credentials']['usernames'][username]['role']

if user_role == 'kitchen':
    st.header("🍽️ Kitchen Dashboard")
        # 👉 Place your kitchen waste donation + NGO matching interface here
elif user_role == 'ngo':
    st.header("🏥 NGO Dashboard")
    st.success("Welcome to the NGO dashboard!")
    st.info("🚧 This will show incoming food requests, allow accepting/rejecting them, and keep a pickup log (coming in Step 3).")


# Page configuration
st.set_page_config(page_title="Smart Food Matcher - Chennai", layout="wide")

# Custom CSS
st.markdown("""
    <style>
        .main { background-color: #f5f5f5; }
        .block-container { padding: 2rem 2rem 2rem; }
        .stTextInput>div>div>input {
            background-color: #fff;
            border-radius: 8px;
            border: 1px solid #ddd;
        }
        .stSlider>div>div>div>div {
            background-color: #d1e8ff;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🍱 Smart Food Waste Matcher - Chennai")
st.write("Helping kitchens connect with nearby NGOs to reduce food waste and support the needy.")

# Sidebar: Upload NGO data
st.sidebar.header("📄 Upload NGO Data")
uploaded_file = st.sidebar.file_uploader("Upload 'ngos_chennai.csv'", type="csv")

# Get approximate user location
location = geocoder.ip('me')
auto_lat, auto_lon = (13.0106, 80.2336)
if location.ok and location.latlng:
    auto_lat, auto_lon = location.latlng

# Cache ML model loading
@st.cache_resource
def load_model():
    return joblib.load("waste_predictor.pkl")

model = load_model()

if uploaded_file:
    ngo_df = pd.read_csv(uploaded_file)

    st.sidebar.header("🧠 ML Waste Prediction")
    meals = st.sidebar.number_input("Meals Prepared", min_value=10, max_value=2000, value=100)
    guests = st.sidebar.number_input("Guests Served", min_value=5, max_value=2000, value=90)
    cuisine = st.sidebar.selectbox("Cuisine Type", ['Veg', 'Non-Veg', 'Mixed'])
    timeofday = st.sidebar.selectbox("Time of Day", ['Morning', 'Afternoon', 'Evening'])

    cuisine_map = {'Veg': 0, 'Non-Veg': 1, 'Mixed': 2}
    time_map = {'Morning': 0, 'Afternoon': 1, 'Evening': 2}

    input_features = np.array([[meals, guests, cuisine_map[cuisine], time_map[timeofday]]])
    predicted_waste = round(model.predict(input_features)[0], 2)
    st.sidebar.metric("Predicted Waste (kg)", f"{predicted_waste:.2f}")

    st.sidebar.header("🍽️ Additional Info")
    food_type = st.sidebar.selectbox("Type of Food", ["Vegetarian", "Non-Vegetarian", "Mixed"])

    with st.sidebar.expander("📍 Kitchen Location"):
        use_auto = st.checkbox("Auto-detect my location", value=True)
        if use_auto:
            kitchen_lat, kitchen_lon = auto_lat, auto_lon
        else:
            kitchen_lat = st.number_input("Latitude", value=13.0106, format="%.6f")
            kitchen_lon = st.number_input("Longitude", value=80.2336, format="%.6f")

    kitchen_name = st.sidebar.text_input("🏨 Kitchen/Hotel Name", value="My Kitchen")
    kitchen_contact = st.sidebar.text_input("📞 Contact Number", value="")
    ready_time = st.sidebar.time_input("⏰ Ready for Pickup At")
    food_image = st.sidebar.file_uploader("🖼️ Upload Food/Kitchen Image", type=["jpg", "jpeg", "png"])

    kitchen_loc = (kitchen_lat, kitchen_lon)

    # Filter NGOs
    filtered = ngo_df[
        (ngo_df['Capacity_kg'] >= predicted_waste) &
        (
            (ngo_df['Accepted_Food_Types'].str.lower() == food_type.lower()) |
            (ngo_df['Accepted_Food_Types'].str.lower() == "both")
        )
    ].copy()

    filtered['Distance_km'] = filtered.apply(
        lambda row: geodesic(kitchen_loc, (row['Latitude'], row['Longitude'])).km,
        axis=1
    )
    closest_ngos = filtered.sort_values('Distance_km').head(3)

    st.subheader("🏥 Recommended NGOs")
    for _, ngo in closest_ngos.iterrows():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{ngo['Name']}** - {ngo['Area']}")
            st.markdown(f"📦 Capacity: `{ngo['Capacity_kg']} kg` | 📍 Distance: `{ngo['Distance_km']:.2f} km`")
            st.markdown(f"📞 Contact: `{ngo['Contact']}`")
        with col2:
            map_url = f"https://www.google.com/maps/dir/{kitchen_lat},{kitchen_lon}/{ngo['Latitude']},{ngo['Longitude']}"
            st.markdown(f"[🗺️ Route]({map_url})")
        st.markdown("---")

    if food_image:
        st.subheader("📷 Uploaded Image")
        st.image(food_image, use_column_width=True)

    # Map Visualization
    st.subheader("🗺️ NGO Locations on Map")
    map_data = closest_ngos[['Latitude', 'Longitude', 'Name']].copy()
    map_data['Type'] = 'NGO'

    kitchen_df = pd.DataFrame([{
        'Latitude': kitchen_lat,
        'Longitude': kitchen_lon,
        'Name': kitchen_name,
        'Type': 'Kitchen'
    }])
    map_df = pd.concat([kitchen_df, map_data], ignore_index=True)

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=kitchen_lat,
            longitude=kitchen_lon,
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=map_df,
                get_position='[Longitude, Latitude]',
                get_color='[200, 30, 0, 160]',
                get_radius=400,
            ),
            pdk.Layer(
                "TextLayer",
                data=map_df,
                get_position='[Longitude, Latitude]',
                get_text='Name',
                get_size=16,
                get_color='[0, 0, 0]',
                get_angle=0,
                get_alignment_baseline="bottom"
            )
        ]
    ))

    # WhatsApp Message
    st.subheader("📲 Message NGO via WhatsApp")
    message = (
        f"🔔 {kitchen_name} has {predicted_waste}kg food ready at "
        f"({kitchen_lat}, {kitchen_lon}). Contact: {kitchen_contact}. "
        f"Suggested NGO: {closest_ngos.iloc[0]['Name']} - {closest_ngos.iloc[0]['Contact']}"
    )
    st.text_area("Preview", message, height=80)
    encoded_msg = quote(message)
    whatsapp_url = f"https://api.whatsapp.com/send?phone=&text={encoded_msg}"
    st.markdown(f"[📤 Send via WhatsApp]({whatsapp_url})")

    # Save log
    record = {
        "timestamp": datetime.now().isoformat(),
        "kitchen_name": kitchen_name,
        "contact": kitchen_contact,
        "food_type": food_type,
        "ready_time": ready_time.strftime("%H:%M"),
        "predicted_waste_kg": predicted_waste,
        "kitchen_latitude": kitchen_lat,
        "kitchen_longitude": kitchen_lon
    }

    csv_path = "waste_logs.csv"
    if os.path.exists(csv_path):
        existing = pd.read_csv(csv_path)
        full_data = pd.concat([existing, pd.DataFrame([record])], ignore_index=True)
    else:
        full_data = pd.DataFrame([record])

    full_data.to_csv(csv_path, index=False)
    st.success("✅ Waste record saved to 'waste_logs.csv'")

else:
    st.warning("⬆️ Please upload a valid NGO CSV file to begin.")

st.caption("Built with ❤️ in Chennai")


