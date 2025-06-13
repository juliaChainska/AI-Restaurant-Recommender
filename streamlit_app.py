import streamlit as st
from workflow.meal_recommendation_workflow import MealRecommendationWorkflow
from agents.meal_suggester_agent import MealSuggesterAgent
from streamlit_geolocation import streamlit_geolocation
import requests
import urllib.parse
import pandas as pd
import altair as alt

# -------------------- Page Configuration --------------------
st.set_page_config(page_title="Smart Meal Finder AI", page_icon="🍔", layout="wide")
st.title("🍽️ Smart Meal Finder AI")


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


def reverse_geocode(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    res = requests.get(url, headers={"User-Agent": "SmartMealFinder/1.0"})
    if res.status_code == 200:
        return res.json().get("display_name", "")
    return ""


# -------------------- Init agent and state --------------------
if "suggester" not in st.session_state:
    st.session_state.suggester = MealSuggesterAgent()

if "suggestions" not in st.session_state:
    st.session_state.suggestions = st.session_state.suggester.get_general_suggestions() or []

if "refined" not in st.session_state:
    st.session_state.refined = []

if "clicked_category" not in st.session_state:
    st.session_state.clicked_category = None

if "meal" not in st.session_state:
    st.session_state.meal = ""

if "user_location" not in st.session_state:
    st.session_state.user_location = ""

if "results" not in st.session_state:
    st.session_state.results = None

# -------------------- Layout: Two Columns Full Width --------------------
with st.container():
    left_col, right_col = st.columns([1, 2], gap="large")

    # --------------- Left Column: Search Inputs ---------------
    with left_col:
        st.markdown("### 🧠 Need ideas? Tap a suggestion!")
        cols = st.columns(4)
        for idx, (emoji, name) in enumerate(st.session_state.suggestions):
            if cols[idx % 4].button(f"{emoji} {name}"):
                st.session_state.clicked_category = name
                st.session_state.meal = name
                st.session_state.refined = st.session_state.suggester.get_sub_suggestions(name) or []

        if st.session_state.refined:
            st.markdown(f"#### 🔍 Variants of {st.session_state.clicked_category}")
            variant_cols = st.columns(4)
            for idx, variant in enumerate(st.session_state.refined):
                if variant_cols[idx % 4].button(f"🍽️ {variant}"):
                    st.session_state.meal = variant
                    st.session_state.refined = []
                    st.session_state.clicked_category = None

        meal = st.text_input("🤔 What do you feel like eating?", value=st.session_state.meal,
                             placeholder="e.g. chicken burger")

        # Get geolocation
        location = streamlit_geolocation()

        # Update user_location if geolocation available and changed
        if location and location.get("latitude") and location.get("longitude"):
            new_location_str = reverse_geocode(location["latitude"], location["longitude"])
            if new_location_str and new_location_str != st.session_state.user_location:
                st.session_state.user_location = new_location_str

        location_name = st.text_input(
            "📍 Your location",
            value=st.session_state.user_location,
            placeholder="e.g. Marszałkowska 1, Warsaw, Poland"
        )

        language = st.selectbox(
            "🌐 In which language should we show the results?",
            ["English", "Polish", "German", "French"]
        )

        col1, col2 = st.columns(2)
        with col1:
            min_rating = st.slider("Minimum rating", 0.0, 5.0, 0.0, step=0.1)
        with col2:
            sort_by = st.selectbox("Sort by", ["Rating", "Number of Reviews", "Name"])

        if st.button("🍽️ Search"):
            if not meal.strip() or not location_name.strip():
                st.warning("Please fill in both fields.")
            else:
                with st.spinner("🍽️ Searching for delicious meals..."):
                    coordinates = geocode_location(location_name)
                    if not coordinates:
                        st.error("Couldn't find the location. Try something more specific.")
                    else:
                        workflow = MealRecommendationWorkflow(language=language)
                        results = workflow.run(meal, coordinates)
                        st.session_state.results = results or []

    # --------------- Right Column: Display Results or Welcome Message ---------------
    with right_col:
        if st.session_state.results is None:
            # Display welcome message when no results yet
            st.markdown("## 👋 Welcome to Smart Meal Finder AI!")
            st.markdown("""
            ### Use the search panel on the left to find amazing restaurants and meals near you.
            """)

        else:
            # Display search results
            filtered = [
                r for r in st.session_state.results
                if r.get("rating") and float(r.get("rating", 0)) >= min_rating
            ]

            if sort_by == "Rating":
                filtered.sort(key=lambda x: float(x.get("rating", 0)), reverse=True)
            elif sort_by == "Number of Reviews":
                filtered.sort(key=lambda x: int(x.get("user_ratings_total", 0)), reverse=True)
            elif sort_by == "Name":
                filtered.sort(key=lambda x: x.get("name", "").lower())

            if filtered:
                st.markdown(f"## 🔎 Found {len(filtered)} recommendations")

                for r in filtered:
                    st.markdown(f"### 🍴 {r.get('name', 'Unknown')}")
                    st.markdown(f"📍 **Address:** {r.get('address', 'N/A')}")
                    place_id = r.get("place_id")
                    if place_id:
                        maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
                        st.markdown(f"[🗺️ View on Google Maps]({maps_url})", unsafe_allow_html=True)

                    lat = r.get("lat")
                    lng = r.get("lng")
                    if lat and lng:
                        iframe_url = f"https://maps.google.com/maps?q={lat},{lng}&z=15&output=embed"
                        st.markdown(
                            f'<iframe src="{iframe_url}" width="100%" height="300" style="border:0;" allowfullscreen="" loading="lazy"></iframe>',
                            unsafe_allow_html=True
                        )

                    st.markdown(f"⭐ **Rating:** {r.get('rating', 'N/A')} ({r.get('user_ratings_total', 0)} reviews)")
                    st.markdown(f"🔍 **Match Summary:** {r.get('match_summary', 'N/A')}")
                    st.markdown(f"📝 **Review Summary:** {r.get('summary', 'N/A')}")

                    if r.get('menu_excerpt') and r['menu_excerpt'] != 'Menu not found':
                        with st.expander("📋 Menu Sample (scraped)"):
                            st.code(r['menu_excerpt'], language="text")

                df = pd.DataFrame(filtered)
                if not df.empty:
                    chart = alt.Chart(df).mark_bar().encode(
                        x=alt.X('rating:O', title='Rating'),
                        y=alt.Y('count()', title='Count')
                    ).properties(title="Ratings Distribution")
                    st.altair_chart(chart, use_container_width=True)

            else:
                st.warning("No recommendations found. Try a different meal or location.")