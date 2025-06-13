from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from tools.google_places_tool import GooglePlacesTool
from managers.prompt_manager import PromptManager
from managers.config_manager import get_config

class ReviewAnalyzerAgent:
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = get_config("GOOGLE_MAPS_API_KEY")
        self.places_tool = GooglePlacesTool(api_key)
        self.llm = ChatOpenAI(temperature=0.3)
        self.prompt_manager = PromptManager()

    def analyze_reviews(self, place_id: str) -> dict:
        details = self.places_tool.get_place_details(place_id)
        reviews = details.get("reviews", [])

        if not reviews:
            return {"summary": "No reviews found."}

        review_texts = [review.get("text", "") for review in reviews[:5]]
        combined_text = "\n".join(review_texts)

        prompt_data = self.prompt_manager.load_prompt("review.yaml")
        messages = [
            SystemMessage(content=prompt_data["system"]),
            HumanMessage(content=prompt_data["template"].format(reviews=combined_text))
        ]
        response = self.llm.invoke(messages)
        price_level = details.get("price_level")
        price_description = {
            0: "Free",
            1: "$ Inexpensive",
            2: "$$ Moderate",
            3: "$$$ Expensive",
            4: "$$$$ Very Expensive"
        }.get(price_level, "Unknown")
        return {
            "summary": response.content,
            "rating": details.get("rating"),
            "user_ratings_total": details.get("user_ratings_total"),
            "address": details.get("formatted_address"),
            "name": details.get("name"),
            "price": price_description,
            "opening_hours": details.get("opening_hours")
        }
