import os
import warnings
warnings.filterwarnings("ignore")
from agents.meal_match_agent import MealMatchAgent
from agents.review_analyzer_agent import ReviewAnalyzerAgent
from dotenv import load_dotenv

load_dotenv()

class MealRecommendationWorkflow:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.meal_agent = MealMatchAgent(self.api_key)
        self.review_agent = ReviewAnalyzerAgent(self.api_key)

    def run(self, user_meal: str, user_location: str, radius: int = 1500) -> list:
        print(f"Searching for: {user_meal} near {user_location}...\n")
        meals = self.meal_agent.find_meals(user_meal, user_location, radius=radius)

        final_recommendations = []

        for meal in meals:
            place_id = meal.get("place_id") or self._get_place_id_by_name(meal["name"], user_location)
            if place_id:
                review_summary = self.review_agent.analyze_reviews(place_id)
                combined = {
                    **meal,
                    **review_summary
                }
                final_recommendations.append(combined)

        return final_recommendations

    def _get_place_id_by_name(self, name: str, location: str) -> str:
        """Fallback if place_id is missing. Attempts to retrieve a place ID by name search."""
        results = self.meal_agent.places_tool.search_places(name, location)
        if results:
            return results[0].get("place_id")
        return None

# Example use
if __name__ == "__main__":
    workflow = MealRecommendationWorkflow()
    user_input = "chicken burger"
    user_location = "52.237049,21.017532"  # Warsaw (lat,lng)
    results = workflow.run(user_input, user_location)

    for r in results:
        print(f"\n--- {r['name']} ---\nAddress: {r['address']}\nRating: {r['rating']} ({r['user_ratings_total']} reviews)\nMatch: {r['match_summary']}\nReview Summary: {r['summary']}")
