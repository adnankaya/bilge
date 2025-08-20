import os
import json
import logging
from pydantic import BaseModel
from ollama import chat
from utils import get_date_time

# Configure logging for the AIAgent module
logger = logging.getLogger("AIAgent")


# Pydantic models to define the expected structured output from the AI
class CategoryResponse(BaseModel):
    """Defines the expected format for app categorization."""

    category: str


class NudgeResponse(BaseModel):
    """Defines the expected format for a nudge message."""

    message: str


class AIAgent:
    """
    Handles communication with a local AI server for AI tasks.
    It categorizes applications and generates context-aware messages.
    """

    def __init__(
        self,
        ollama_url="http://localhost:11434",
        model_name="gemma:3b",
        filename="app_categories.json",
    ):
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.cache_dir = "cache"
        self.filepath = os.path.join(self.cache_dir, filename)

        self._ensure_cache_dir()
        self.category_cache = self._load_cache()

    def _ensure_cache_dir(self):
        """
        Checks if the 'cache' directory exists and creates it if not.
        """
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            logger.info(f"Created directory: {self.cache_dir}")

    def _load_cache(self):
        """
        Loads the application category cache from a local JSON file.
        """
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Error loading cache file: {e}")
                return {}
        return {}

    def _save_cache(self):
        """
        Saves the current application category cache to a local JSON file.
        """
        with open(self.filepath, "w") as f:
            json.dump(self.category_cache, f, indent=4)

    def categorize_app(self, app_data: str | dict) -> str:
        """
        Categorizes an application using the LLM.
        Checks the local cache first before querying the model.
        """
        cache_key = (
            app_data
            if isinstance(app_data, str)
            else f"chrome|{app_data['active_tab_title']}|{app_data['active_tab_url']}"
        )

        if cache_key in self.category_cache:
            return self.category_cache[cache_key]

        if isinstance(app_data, dict):
            prompt = (
                f"Categorize this web page with title '{app_data['active_tab_title']}' "
                f"and URL '{app_data['active_tab_url']}' into one of the following "
                "categories: Work, Gaming, Browsing, Communication, Media, or Other. "
                "Respond with only the category name."
            )
        else:
            prompt = (
                f"Categorize the application '{app_data}' into one of the following "
                "categories: Work, Gaming, Browsing, Communication, Media, or Other. "
                "Respond with only the category name."
            )

        try:
            print(
                get_date_time(),
                f"[AI] Categorizing app: {cache_key}",
            )
            category_response = self._query_llm(
                prompt=prompt, response_schema=CategoryResponse.model_json_schema()
            )
            category = category_response.category
        except Exception as e:
            logger.error(f"Failed to categorize app with structured response: {e}")
            category = "Other"  # Fallback

        valid_categories = {
            "Work",
            "Gaming",
            "Browsing",
            "Communication",
            "Media",
            "Other",
        }
        if category not in valid_categories:
            category = "Other"

        self.category_cache[cache_key] = category
        self._save_cache()
        return category

    def generate_nudge(self, category: str, duration: float) -> str:
        """
        Generates a friendly notification message based on the category and duration.
        """
        prompt = (
            f"The user has been in the '{category}' category for {int(duration)} seconds. "
            "Write a short, friendly, and encouraging message that includes the category and duration. "
            "Suggest one of the following healthy break activities: taking a walk, stretching, light exercise, resting eyes, drinking water, or getting some fresh air. "
            "Keep it light and non-judgmental. Choose only one activity to suggest."
        )

        try:
            print(
                get_date_time(),
                f"[AI] Generating nudge for category: {category}, duration: {duration} seconds",
            )
            nudge_response = self._query_llm(
                prompt=prompt, response_schema=NudgeResponse.model_json_schema()
            )
            return nudge_response.message
        except Exception as e:
            logger.error(f"Failed to generate nudge with structured response: {e}")
            return "Consider taking a break from your screen."  # Fallback

    def _query_llm(self, prompt: str, response_schema: dict) -> BaseModel:
        """
        Sends a prompt to the local Ollama server and returns a structured response.
        """
        try:
            response = chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                format=response_schema,
            )
            json_response = response["message"]["content"]
            print(get_date_time(), "[AI] Received response. Notifying user...")
            # Use the Pydantic model's validation method to parse the JSON
            if response_schema["title"] == "CategoryResponse":
                return CategoryResponse.model_validate_json(json_response)
            else:
                return NudgeResponse.model_validate_json(json_response)

        except Exception as e:
            logger.error(f"Error querying Ollama: {e}")
            raise  # Re-raise the exception for the caller to handle
