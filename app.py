import warnings
warnings.filterwarnings("ignore")
from workflow.meal_recommendation_workflow import MealRecommendationWorkflow
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workflow'))


import requests
import urllib.parse

def geocode_location(location_name: str) -> str:
    encoded_location = urllib.parse.quote(location_name)
    url = f"https://nominatim.openstreetmap.org/search?q={encoded_location}&format=json&limit=1"
    response = requests.get(url, headers={"User-Agent": "SmartMealFinder/1.0"})

    if response.status_code == 200:
        data = response.json()
        if data:
            lat = data[0]['lat']
            lon = data[0]['lon']
            return f"{lat},{lon}"
    print("❌ Could not geocode the location name. Please try a different one.")
    return ""

def main():
    print("\n🍔 Restaurant Recommender!\n")
    meal = input("What do you feel like eating? (e.g., chicken burger): ")
    location_name = input("Enter your city or neighborhood (e.g., Warsaw, Poland): ")

    location = geocode_location(location_name)
    if not location:
        return

    workflow = MealRecommendationWorkflow()
    results = workflow.run(meal, location)

    if not results:
        print("\n❌ No recommendations found. Try a different meal or location.")
        return

    print("\n✅ Top Recommendations:")
    for r in results:
        print(f"\n--- {r['name']} ---")
        print(f"📍 Address: {r['address']}")
        print(f"⭐  Rating: {r['rating']} ({r['user_ratings_total']} reviews)")
        print(f"🔍 Match Summary: {r['match_summary']}")
        print(f"📝 Review Summary: {r['summary']}")

        if r.get("menu_excerpt") and r["menu_excerpt"] != "Menu not found":
            print("📋 Menu Sample:\n")
            print(r["menu_excerpt"][:500])

if __name__ == "__main__":
    main()

