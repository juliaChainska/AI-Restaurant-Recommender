import streamlit as st
from workflow.meal_recommendation_workflow import MealRecommendationWorkflow
import requests
import urllib.parse

# -------------------- Page Configuration --------------------
st.set_page_config(page_title="Smart Meal Finder AI", page_icon="🍔")
st.title("🍽️ Smart Meal Finder AI")
# -------------------- Helper Functions --------------------
def geocode_location(location_name: str) -> str:
    encoded_location = urllib.parse.quote(location_name)
    url = f"https://nominatim.openstreetmap.org/search?q={encoded_location}&format=json&limit=1&addressdetails=1"
    response = requests.get(url, headers={"User-Agent": "SmartMealFinder/1.0"})
    if response.status_code == 200:
        data = response.json()
        if data:
            lat = data[0]['lat']
            lon = data[0]['lon']
            return f"{lat},{lon}"
    return ""

# Dane wejściowe
meal = st.text_input("🤔 What do you feel like eating?", placeholder="e.g. chicken burger")
location_name = st.text_input("📍 Enter your location", placeholder="e.g. Marszałkowska 1, Warsaw, Poland")

col1, col2 = st.columns(2)
with col1:
    min_rating = st.slider("Minimum rating", 0.0, 5.0, 0.0, step=0.1)
with col2:
    sort_by = st.selectbox("Sort by", ["Rating", "Number of Reviews", "Name"])

# Inicjalizacja pamięci
if "results" not in st.session_state:
    st.session_state.results = []

# Wyszukiwanie
if st.button("🍽️ Search"):
    if not meal or not location_name:
        st.warning("Please fill in both fields.")
    else:
        with st.spinner("Getting hungry..."):
            coordinates = geocode_location(location_name)
            if not coordinates:
                st.error("Couldn't find the location. Try something more specific.")
            else:
                workflow = MealRecommendationWorkflow()
                results = workflow.run(meal, coordinates)
                st.session_state.results = results  # Zapisujemy w sesji

if st.session_state.results:
    # Filtrowanie
    filtered = [r for r in st.session_state.results if r["rating"] and float(r["rating"]) >= min_rating]

    # Sortowanie
    if sort_by == "Rating":
        filtered.sort(key=lambda x: x.get("rating", 0), reverse=True)
    elif sort_by == "Number of Reviews":
        filtered.sort(key=lambda x: x.get("user_ratings_total", 0), reverse=True)
    elif sort_by == "Name":
        filtered.sort(key=lambda x: x.get("name", "").lower())

    st.markdown(f"## 🔎 Found {len(filtered)} recommendations")

    for r in filtered:
        st.markdown(f"### 🍴 {r['name']}")
        st.markdown(f"📍 **Address:** {r['address']}")
        if r.get("place_id"):
            maps_url = f"https://www.google.com/maps/place/?q=place_id:{r['place_id']}"
            st.markdown(f"[🗺️ View on Google Maps]({maps_url})", unsafe_allow_html=True)
        if r.get("lat") and r.get("lng"):
            maps_embed = f"https://www.google.com/maps/place/?q=place_id:{r['place_id']}&z=15&output=embed"
            st.components.v1.html(f'<iframe src="{maps_embed}" width="100%" height="300"></iframe>', height=300)
        st.markdown(f"⭐ **Rating:** {r['rating']} ({r['user_ratings_total']} reviews)")
        st.markdown(f"🔍 **Match Summary:** {r['match_summary']}")
        st.markdown(f"📝 **Review Summary:** {r['summary']}")

        if r.get('menu_excerpt') and r['menu_excerpt'] != 'Menu not found':
            with st.expander("📋 Menu Sample (scraped)"):
                st.code(r['menu_excerpt'], language="text")

# Brak wyników po kliknięciu
elif "results" in st.session_state and not st.session_state.results:
    st.warning("No recommendations found. Try a different meal or location.")
