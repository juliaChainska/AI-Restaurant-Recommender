import json
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

class MealSuggesterAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.2)

    def get_category_suggestions(self):
        prompt = (
            "Return a JSON list of 4 popular general meal categories, each with an emoji and short label. "
            "Example format: [[\"🍗\", \"Meat\"], [\"🥦\", \"Vege\"], [\"🍭\", \"Sweets\"]]"
        )
        response = self.llm.invoke([HumanMessage(content=prompt)])

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            print("⚠️ Could not parse LLM response:", response.content)
            return []


    def get_general_suggestions(self, category: str):
        prompt = (
            f"Return a JSON list of 8 popular meals based on category {category.lower()}, each with an emoji and short label. "
            "Example format: [[\"🍔\", \"Burger\"], [\"🍕\", \"Pizza\"], [\"🍣\", \"Sushi\"]]"
        )
        response = self.llm.invoke([HumanMessage(content=prompt)])

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            print("⚠️ Could not parse LLM response:", response.content)
            return []

    def get_sub_suggestions(self, meal: str):
        prompt = (
            f"Return a JSON list of 4 specific types of {meal.lower()} someone might want to eat. "
            f"Example for 'Burger': [\"Chicken Burger\", \"Cheeseburger\", \"Vegan Burger\"]"
        )
        response = self.llm.invoke([HumanMessage(content=prompt)])

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            print("⚠️ Could not parse sub-suggestions for", meal, ":", response.content)
            return []
