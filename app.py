import streamlit as st
import pandas as pd
from geopy.distance import geodesic
import pydeck as pdk
import geocoder
import os
from datetime import datetime


st.set_page_config(page_title="Smart Food Matcher - Chennai", layout="wide")

st.markdown("""
    <style>
        .main {
            background-color: #f5f5f5;
        }
        .block-container {
            padding: 2rem 2rem 2rem;
        }
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

st.sidebar.header("📄 Upload NGO Data")
uploaded_file = st.sidebar.file_uploader("Upload 'ngos_chennai.csv'", type="csv")

# Try auto-detecting user's location
location = geocoder.ip('me')
auto_lat = location.latlng[0] if location.ok else 13.0106
auto_lon = location.latlng[1] if location.ok else 80.2336

if uploaded_file:
    ngo_df = pd.read_csv(uploaded_file)

    st.sidebar.header("📊 Input Details")  
    predicted_waste = st.sidebar.slider("Predicted Food Waste (kg)", 1, 100, 10)

    with st.sidebar.expander("📍 Kitchen Location"):
        use_auto = st.checkbox("Auto-detect my location", value=True)
        if use_auto:
            kitchen_lat = auto_lat
            kitchen_lon = auto_lon
        else:
            kitchen_lat = st.number_input("Your Latitude", value=13.0106, format="%f")
            kitchen_lon = st.number_input("Your Longitude", value=80.2336, format="%f")

    kitchen_name = st.sidebar.text_input("🏨 Kitchen/Hotel Name", value="My Kitchen")
    kitchen_contact = st.sidebar.text_input("📞 Contact Number", value="")

    kitchen_loc = (kitchen_lat, kitchen_lon)

    filtered = ngo_df[ngo_df['Capacity_kg'] >= predicted_waste].copy()
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

    st.subheader("🗺️ NGO Locations on Map")
    map_data = closest_ngos[['Latitude', 'Longitude']]
    map_data['Name'] = closest_ngos['Name']
    map_data['Type'] = 'NGO'
    kitchen_df = pd.DataFrame([{'Latitude': kitchen_lat, 'Longitude': kitchen_lon, 'Name': kitchen_name, 'Type': 'Kitchen'}])
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

    st.subheader("📲 Message NGO via WhatsApp")
    message = f"🔔 {kitchen_name} has {predicted_waste}kg food ready at ({kitchen_lat}, {kitchen_lon}). Contact: {kitchen_contact}. Suggested NGO: {closest_ngos.iloc[0]['Name']} - {closest_ngos.iloc[0]['Contact']}"
    st.text_area("Preview", message, height=80)
    whatsapp_url = f"https://api.whatsapp.com/send?phone=&text={message.replace(' ', '%20')}"
    st.markdown(f"[📤 Send via WhatsApp]({whatsapp_url})")

record = {
    "timestamp": datetime.now().isoformat(),
    "predicted_waste_kg": predicted_waste,
    "kitchen_latitude": kitchen_lat,
    "kitchen_longitude": kitchen_lon
}

# Convert to DataFrame
new_data = pd.DataFrame([record])

# Save or append to 'waste_logs.csv'
csv_path = "waste_logs.csv"
if os.path.exists(csv_path):
    existing = pd.read_csv(csv_path)
    full_data = pd.concat([existing, new_data], ignore_index=True)
else:
    full_data = new_data

full_data.to_csv(csv_path, index=False)
st.success("✅ Waste record saved to 'waste_logs.csv'")

else:
    st.warning("⬆️ Please upload a valid CSV file to begin.")

st.caption("Built with ❤️ in Chennai")
