import os
import time
import json
from pathlib import Path

DEFAULT_RULES = [
    ("Work", 30, "short_work_session"),
    ("Gaming", 20, "short_gaming_session"),
    ("Browsing", 15, "short_browsing_session"),
    ("Media", 10, "short_media_session"),
    ("Communication", 10, "short_communication_session"),
]

class RulesEngine:
    """
    Analyzes current session data to find patterns and trigger notifications.
    """

    def __init__(self, config_file="rules_config.json"):
        self.config_file = Path(__file__).parent / config_file
        # Tracks the last time a nudge was sent for a specific action
        self.last_nudged_time = {}
        self.last_modified_time = os.path.getmtime(self.config_file) if self.config_file.exists() else 0
        self.rules = self.load_rules()

    def load_rules(self):
        """
        Load rules from the JSON configuration file and check for modifications.
        Returns a list of tuples: (category, duration_seconds, action_name)
        """
        try:
            current_modified_time = os.path.getmtime(self.config_file)
            if current_modified_time > self.last_modified_time:
                print(f"Rules configuration file {self.config_file} has been modified! Reloading...")
                self.last_modified_time = current_modified_time
            
            with open(self.config_file, "r") as f:
                config = json.load(f)
                return [(rule["category"], rule["duration_seconds"], rule["action_name"]) 
                       for rule in config["rules"]]
        except FileNotFoundError:
            print(f"Warning: Rules configuration file {self.config_file} not found. Using default rules.")
            return DEFAULT_RULES
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {self.config_file}. Using default rules.")
            return DEFAULT_RULES

    def evaluate_current_session(self, category: str, duration: float) -> tuple | None:
        """
        Checks the current session's duration against the predefined rules.

        Args:
            category (str): The category of the current session.
            duration (float): The duration of the current session in seconds.

        Returns:
            A tuple for the triggered rule: (rule_name, category, duration) or None.
        """
        # Reload rules on every check to detect changes
        self.rules = self.load_rules()
        for rule_category, rule_duration, action in self.rules:
            if rule_category == category and duration >= rule_duration:
                # Check if a nudge for this action has been sent recently
                if (action not in self.last_nudged_time) or (time.time() - self.last_nudged_time[action] > rule_duration):
                    self.last_nudged_time[action] = time.time()
                    return (action, category, int(duration))
        return None

    def reset_rules(self):
        """
        Resets the state of last nudged actions.
        This could be used for a daily reset or after a long break.
        """
        self.last_nudged_time.clear()

# For testing purposes
if __name__ == "__main__":
    rulesengine = RulesEngine(config_file="test_rules_config.json")
    
    # Create a dummy config file for testing
    dummy_config = {"rules": [{"category": "Work", "duration_seconds": 5, "action_name": "short_work_session"}]}
    with open("test_rules_config.json", "w") as f:
        json.dump(dummy_config, f)
    
    print("Testing continuous session evaluation.")
    
    start_time = time.time()
    while True:
        elapsed_time = time.time() - start_time
        triggered_rule = rulesengine.evaluate_current_session("Work", elapsed_time)
        if triggered_rule:
            print(f"Rule triggered for Work: {triggered_rule[2]} seconds. Waiting for a new trigger...")
            start_time = time.time() # Reset for testing re-triggering logic
        
        time.sleep(1)
