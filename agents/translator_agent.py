from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from managers.prompt_manager import PromptManager

class TranslationAgent:
    def __init__(self, target_language: str):
        self.llm = ChatOpenAI(temperature=0)
        self.target_language = target_language
        self.prompt_manager = PromptManager()

    def translate(self, text: str) -> str:
        if not text or self.target_language.lower() in ["english", "en"]:
            return text  # no need to translate

        prompt = self.prompt_manager.load_prompt("translator.yaml")

        messages = [
            SystemMessage(content=prompt["system"]),
            HumanMessage(content=prompt["template"].format(text=text, language=self.target_language))
        ]
        response = self.llm.invoke(messages)
        return response.content
