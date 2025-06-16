# 🍱 Smart Food Matcher - Chennai

A modern data-driven solution to reduce food waste by intelligently matching surplus food from restaurants, hotels, and canteens with NGOs in **Chennai, Tamil Nadu** that can collect and distribute it to those in need.

---

## 🎯 Problem Statement

Millions of kilograms of edible food are wasted every day while many go hungry. This project aims to:

- **Predict daily food waste**
- **Match it with suitable NGOs** nearby
- **Auto-suggest the fastest donation path**
- **Simplify communication using WhatsApp**
- **Visualize geospatial data on a live map**

---

## 🔧 Technologies Used

- **Python 3.10+**
- **Streamlit** – UI Framework
- **Pandas** – Data processing
- **Geopy** – Location & distance calculation
- **Pydeck** – Interactive map integration
- **Joblib** *(optional)* – For ML model persistence (future scope)
- **Colab** – For initial data training (optional)

---

## 📦 Project Structure
smart-food-matcher/
├── app.py # Streamlit app with full functionality
├── waste_logs.csv # Auto-created log of donation records
├── ngos_chennai.csv # NGO dataset (uploadable by user)
├── waste_predictor.pkl # (Optional) ML model file
├── train_model.ipynb # (Optional) Colab notebook for ML
├── README.md # This documentation


---

## ✅ Features

| Module | Description |
|--------|-------------|
| 🔢 Waste Input | Enter expected food waste (kg) |
| 🧭 Location Input | Enter latitude/longitude manually or auto-detect *(future)* |
| 📥 NGO Matching | Filters NGOs by distance & capacity |
| 📲 WhatsApp Message | Auto-generate message with NGO contact |
| 🗺️ Live Map | See kitchen + NGOs on interactive map |
| 💾 Data Logging | All donations saved to `waste_logs.csv` |

---

## 🧾 NGO CSV Format

```csv
Name,Area,Latitude,Longitude,Capacity_kg,Contact
Feeding India,Anna Nagar,13.0878,80.2170,50,+919876543210
No Waste NGO,Teynampet,13.0418,80.2500,25,+918765432109

🚀 How to Run

    Install dependencies:

pip install streamlit pandas geopy pydeck

    Run the app:

streamlit run app.py

    Upload ngos_chennai.csv when prompted.
