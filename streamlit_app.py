import streamlit as st
from workflow.meal_recommendation_workflow import MealRecommendationWorkflow
from agents.meal_suggester_agent import MealSuggesterAgent
import requests
import urllib.parse
import time
import threading
import pandas as pd
import altair as alt

# -------------------- Page Configuration --------------------
st.set_page_config(page_title="Smart Meal Finder AI", page_icon="🍔")
st.title("🍽️ Smart Meal Finder AI")

# -------------------- Init agent and state --------------------
if "suggestions" not in st.session_state:
    suggester = MealSuggesterAgent()
    st.session_state.suggestions = suggester.get_general_suggestions()

if "refined" not in st.session_state:
    st.session_state.refined = []

if "clicked_category" not in st.session_state:
    st.session_state.clicked_category = None

if "meal" not in st.session_state:
    st.session_state.meal = ""

# -------------------- Meal Suggestion --------------------
st.markdown("### 🧠 Need ideas? Tap a suggestion!")

cols = st.columns(4)
for idx, (emoji, name) in enumerate(st.session_state.suggestions):
    if cols[idx % 4].button(f"{emoji} {name}"):
        st.session_state.clicked_category = name
        st.session_state.meal = name  # ustawia wyszukiwane odrazu jako meal
        suggester = MealSuggesterAgent()
        st.session_state.refined = suggester.get_sub_suggestions(name)
        st.rerun()

if st.session_state.refined:
    st.markdown(f"#### 🔍 Variants of {st.session_state.clicked_category}")
    variant_cols = st.columns(4)
    for idx, variant in enumerate(st.session_state.refined):
        if variant_cols[idx % 4].button(f"🍽️ {variant}"):
            st.session_state.meal = variant  # ustawia wyszukiwane jako specific meal
            st.session_state.refined = []
            st.session_state.clicked_category = None
            st.rerun()

# -------------------- Inputs --------------------
meal = st.text_input("🤔 What do you feel like eating?", value=st.session_state.meal, placeholder="e.g. chicken burger")
location_name = st.text_input("📍 Enter your location", placeholder="e.g. Marszałkowska 1, Warsaw, Poland")
col1, col2, col3 = st.columns(3)
with col1:
    min_rating = st.slider("Minimum rating", 0.0, 5.0, 0.0, step=0.1)

with col2:
    sort_by = st.selectbox("Sort by", ["Rating", "Number of Reviews", "Name"])

with col3:
    radius_km = st.number_input("Max distance (km)", min_value=0.0, step=0.5, value=0.0)

# -------------------- Helper --------------------
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

# -------------------- Results state --------------------
if "results" not in st.session_state:
    st.session_state.results = None

# -------------------- Search trigger --------------------
if st.button("🍽️ Search"):
    if not meal or not location_name:
        st.warning("Please fill in both fields.")
    else:
        placeholder = st.empty()
        food_emojis = ["🍦", "🍤", "🍔", "🍕", "🥗", "🧋", "🌮", "🍟", "🥞"]

        # emoji w pętli
        loading = True
        i = 0

        # Start search thread
        def perform_search():
            coordinates = geocode_location(location_name)
            if not coordinates:
                return None, "Couldn't find the location. Try something more specific."
            workflow = MealRecommendationWorkflow()
            radius_m = int(radius_km * 1000) if radius_km > 0 else None
            results = workflow.run(meal, coordinates, radius=radius_m)
            return results, None

        search_result = [None]
        error_result = [None]

        def search_task():
            results, error = perform_search()
            search_result[0] = results
            error_result[0] = error

        t = threading.Thread(target=search_task)
        t.start()

        while t.is_alive():
            emoji = food_emojis[i % len(food_emojis)]
            placeholder.markdown(f"### {emoji} Getting hungry...")
            time.sleep(0.3)
            i += 1

        t.join()
        placeholder.empty()

        if error_result[0]:
            st.error(error_result[0])
        else:
            st.session_state.results = search_result[0] if search_result[0] else []

# -------------------- Results Display --------------------
if st.session_state.results:
    filtered = [r for r in st.session_state.results if r["rating"] and float(r["rating"]) >= min_rating]

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
            lat, lng = r["lat"], r["lng"]
            iframe_url = f"https://maps.google.com/maps?q={lat},{lng}&z=15&output=embed"
            st.markdown(
                f'<iframe src="{iframe_url}" width="100%" height="300" style="border:0;" allowfullscreen="" loading="lazy"></iframe>',
                unsafe_allow_html=True
            )
        st.markdown(f"⭐ **Rating:** {r['rating']} ({r['user_ratings_total']} reviews)")

        if r.get("price"):
            st.markdown(f"💰 **Price Range:** {r['price']}")

        if r.get("opening_hours"):
            hours = r["opening_hours"].get("weekday_text", [])
            if hours:
                with st.expander("🕒 Opening Hours"):
                    for line in hours:
                        st.markdown(f"- {line}")
            else:
                st.markdown("🕒 No opening hours info available.")


        st.markdown(f"🔍 **Match Summary:** {r['match_summary']}")
        st.markdown(f"📝 **Review Summary:** {r['summary']}")

        if r.get('menu_excerpt') and r['menu_excerpt'] != 'Menu not found':
            with st.expander("📋 Menu Sample (scraped)"):
                st.code(r['menu_excerpt'], language="text")

    df = pd.DataFrame(filtered)
    chart = alt.Chart(df).mark_bar().encode(
        x='rating:O',
        y='count():Q'
    ).properties(title="Ratings Distribution")
    st.altair_chart(chart, use_container_width=True)

elif st.session_state.results == []:
    st.warning("No recommendations found. Try a different meal or location.")
