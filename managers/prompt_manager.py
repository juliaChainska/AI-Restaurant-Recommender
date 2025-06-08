
import yaml
import os

class PromptManager:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
        self.base_dir = os.path.abspath(base_dir)

    def load_prompt(self, file_name: str) -> dict:
        path = os.path.join(self.base_dir, file_name)
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
