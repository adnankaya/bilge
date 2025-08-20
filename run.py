import time
import datetime
import os
import sys
import argparse

from data_manager import DataManager
from monitor import Monitor
from rules_engine import RulesEngine
from notifier import Notifier
from ai import AIAgent
from utils import get_date, get_date_time


class BilgeApp:
    """
    Main application class to run the app.
    It encapsulates the state and logic for session tracking.
    """

    TEN_SECONDS = 10

    def __init__(self, date: str, model_name: str | None = None):
        self.data_manager = DataManager(filename=f"{date}.json")
        self.monitor = Monitor()
        self.rules_engine = RulesEngine()
        self.notifier = Notifier()
        self.ai_agent = AIAgent(model_name=model_name)

        # State variables for the current session
        self.current_session_start_time = datetime.datetime.now()
        self.current_session_category = None
        self.current_session_app_name = None
        self.last_app_data = None
        # State variable for managing in-session nudges
        self.nudged_for_session = False

    def _get_app_info(self, app_data):
        if isinstance(app_data, dict):
            categorization_string = (
                f"{app_data['active_tab_title']} | {app_data['active_tab_url']}"
            )
            app_name_for_log = (
                f"{app_data['window_name']} | {app_data['active_tab_title']}"
            )
        else:
            categorization_string = app_data
            app_name_for_log = app_data
        return categorization_string, app_name_for_log

    def run(self):
        while True:
            try:
                # 1. Continuous monitoring of the active window
                current_app_data = self.monitor.get_active_window()

                if current_app_data:
                    categorization_string, app_name_for_log = self._get_app_info(
                        current_app_data
                    )
                    current_category = self.ai_agent.categorize_app(
                        categorization_string
                    )

                    # 2. Check for an app or category switch to end the previous session
                    if (current_app_data != self.last_app_data) or (
                        current_category != self.current_session_category
                    ):
                        if self.current_session_app_name:
                            print(
                                f"{get_date_time()} Session ended. Logging {self.current_session_app_name} | {self.current_session_category}"
                            )
                            self.data_manager.save_session(
                                app_name=self.current_session_app_name,
                                category=self.current_session_category,
                                start_time=self.current_session_start_time,
                                end_time=datetime.datetime.now(),
                            )

                        # Start a new session
                        self.current_session_start_time = datetime.datetime.now()
                        self.current_session_category = current_category
                        self.current_session_app_name = app_name_for_log
                        self.last_app_data = current_app_data
                        print(
                            f"{get_date_time()} Session started. Tracking {self.current_session_app_name} | {self.current_session_category}"
                        )

                        # Reset the nudge flag for the new session
                        self.nudged_for_session = False

                    # 3. Continuous rule evaluation for the CURRENT session
                    current_session_duration = (
                        datetime.datetime.now() - self.current_session_start_time
                    ).total_seconds()

                    if not self.nudged_for_session:
                        triggered_rule = self.rules_engine.evaluate_current_session(
                            self.current_session_category, current_session_duration
                        )

                        if triggered_rule:
                            # If a rule is triggered for the first time in this session
                            rule_name, category, duration = triggered_rule
                            print(
                                f"{get_date_time()} Triggered rule: {rule_name} for category: {category} with duration: {int(duration)} seconds."
                            )
                            message = self.ai_agent.generate_nudge(category, duration)
                            self.notifier.send_notification("bilge", message)
                            # Set the flag to prevent re-querying for this session
                            self.nudged_for_session = True

                time.sleep(1)

            except KeyboardInterrupt:
                print("Exiting from bilge... \n")
                if self.current_session_app_name:
                    self.data_manager.save_session(
                        self.current_session_app_name,
                        self.current_session_category,
                        self.current_session_start_time,
                        datetime.datetime.now(),
                    )
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                time.sleep(5)


def check_ollama_model(model_name: str) -> bool:
    import requests

    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return any(model["name"] == model_name for model in models)
        return False
    except requests.RequestException:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Bilge with specified LLM model")
    parser.add_argument(
        "model", nargs="?", help="Ollama model name (e.g., gemma3:4b)", default=None
    )
    args = parser.parse_args()

    date = get_date()

    if args.model:
        if not check_ollama_model(args.model):
            print(f"Error: Model '{args.model}' is not available in Ollama.")
            print("Please make sure Ollama is running and the model is pulled.")
            sys.exit(1)

    app = BilgeApp(date, model_name=args.model)
    app.run()
