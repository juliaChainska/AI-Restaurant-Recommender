import streamlit as st
from workflow.meal_recommendation_workflow import MealRecommendationWorkflow
import requests
import urllib.parse
import pandas as pd

st.set_page_config(page_title="Smart Meal Finder AI", page_icon="🍔")

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

# -------------------- UI Layout --------------------
st.title("🍔 Smart Meal Finder AI")

meal = st.text_input("What do you feel like eating?", placeholder="e.g. chicken burger")
location_name = st.text_input("Enter your location", placeholder="e.g. Marszałkowska 1, Warsaw, Poland")

min_rating = st.slider("Minimum Rating", 0.0, 5.0, 4.0, 0.1)

if st.button("Search"):
    if not meal or not location_name:
        st.warning("Please fill in both fields.")
    else:
        coordinates = geocode_location(location_name)
        if not coordinates:
            st.error("Couldn't find the location. Try something more specific.")
        else:
            with st.spinner("Searching for nearby places..."):
                workflow = MealRecommendationWorkflow()
                results = workflow.run(meal, coordinates)

            if not results:
                st.warning("No recommendations found.")
            else:
                # Filter results
                results = [r for r in results if r.get("rating") and r["rating"] >= min_rating]

                # Display map
                coords = []
                for r in results:
                    try:
                        lat, lon = map(float, r['address'].split(",")[-2:])
                        coords.append({"lat": lat, "lon": lon})
                    except:
                        continue
                if coords:
                    st.map(pd.DataFrame(coords))

                # Display results
                for r in results:
                    st.markdown(f"### {r['name']}")
                    st.markdown(f"📍 **Address:** {r['address']}")
                    st.markdown(f"⭐ **Rating:** {r['rating']} ({r['user_ratings_total']} reviews)")
                    st.markdown(f"🔍 **Match Summary:** {r['match_summary']}")
                    st.markdown(f"📝 **Review Summary:** {r['summary']}")

                    if r.get('menu_excerpt') and r['menu_excerpt'] != 'Menu not found':
                        with st.expander("📋 Menu Sample (scraped)"):
                            st.code(r['menu_excerpt'][:500], language="text")
