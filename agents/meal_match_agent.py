import warnings
warnings.filterwarnings("ignore")

from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from tools.google_places_tool import GooglePlacesTool
from managers.prompt_manager import PromptManager
from managers.config_manager import get_config

import requests
from bs4 import BeautifulSoup

class MealMatchAgent:
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = get_config("GOOGLE_MAPS_API_KEY")
        self.places_tool = GooglePlacesTool(api_key)
        self.llm = ChatOpenAI(temperature=0.2)
        self.prompt_manager = PromptManager()

    def find_meals(self, user_input: str, location: str, radius: int = 1500) -> list:
        raw_results = self.places_tool.search_places(user_input, location, radius=radius)
        recommendations = []

        for place in raw_results[:10]:
            menu_text = self._try_fetch_menu_from_website(place)
            summary = self._summarize_match(user_input, place, menu_text)
            recommendations.append({
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "lat": place.get("geometry", {}).get("location", {}).get("lat"),
                "lng": place.get("geometry", {}).get("location", {}).get("lng"),
                "place_id": place.get("place_id"),
                "match_summary": summary,
                "rating": place.get("rating"),
                "user_ratings_total": place.get("user_ratings_total"),
                "menu_excerpt": menu_text[:500] if menu_text else "Menu not found"
            }) 

        return recommendations

    def _summarize_match(self, query: str, place: dict, menu: str = "") -> str:
        name = place.get("name", "")
        types = ", ".join(place.get("types", []))
        prompt_data = self.prompt_manager.load_prompt("matcher.yaml")

        messages = [
            SystemMessage(content=prompt_data["system"]),
            HumanMessage(content=prompt_data["template"].format(query=query, name=name, types=types))
        ]

        if menu:
            try:
                menu_prompt = self.prompt_manager.load_prompt("menu_match.yaml")
                messages.append(HumanMessage(content=menu_prompt["template"].format(
                    query=query, name=name, menu_items=menu[:1000]
                )))
            except Exception as e:
                print(f"⚠️ Error loading menu prompt: {e}")

        response = self.llm.invoke(messages)
        return response.content

    def _try_fetch_menu_from_website(self, place: dict) -> str:
        url = place.get("website") or place.get("url")
        if not url:
            return ""
        try:
            headers = {"User-Agent": "SmartMealFinder/1.0"}
            res = requests.get(url, timeout=5, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            texts = soup.stripped_strings
            full_text = " ".join(texts)
            return full_text
        except Exception as e:
            print(f"⚠️ Failed to fetch menu from {url}: {e}")
            return ""
