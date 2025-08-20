import json
import os
import datetime


class DataManager:
    """
    Manages data persistence using a local JSON file, stored in a 'logs' directory.
    """

    def __init__(self, filename="2025-08-20.json"):
        self.log_dir = "logs"
        self.filepath = os.path.join(self.log_dir, filename)

        self._ensure_log_dir()
        self.data = self._load_data()

    def _ensure_log_dir(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            print(f"Created directory: {self.log_dir}")

    def _load_data(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def _save_data(self):
        with open(self.filepath, "w") as f:
            json.dump(self.data, f, indent=4)

    def save_session(
        self,
        app_name: str,
        category: str,
        start_time: datetime,
        end_time: datetime,
    ):
        """
        Adds a new session entry to the data.

        Args:
            app_name (str): The name of the application.
            category (str): The AI-categorized usage type.
            start_time (datetime): The session's start time.
            end_time (datetime): The session's end time.
        """
        entry = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "app_name": app_name,
            "category": category,
            "duration_seconds": (end_time - start_time).total_seconds(),
        }
        self.data.append(entry)
        self._save_data()
    
    # This method is no longer used by the main loop for real-time checks,
    # but it is kept for potential future use cases like data analysis or reports.
    def get_latest_sessions(self) -> dict:
        """
        Aggregates usage data by category.

        Returns:
            A dictionary mapping each category to its latest session.
        """
        latest_sessions = {}
        for entry in reversed(self.data):
            category = entry.get("category")
            if category not in latest_sessions:
                latest_sessions[category] = {
                    "duration_seconds": entry.get("duration_seconds", 0),
                    "start_time": entry.get("start_time"),
                }
        return latest_sessions

if __name__ == "__main__":
    dm = DataManager()

    print("Saving example entries...")
    dm.save_entry("Visual Studio Code", "Work", 3600)
    dm.save_entry("Steam", "Gaming", 1800)
    dm.save_entry("Google Chrome", "Browsing", 7200)

    print("\nAggregated data:")
    aggregated_data = dm.get_aggregated_data()
    for category, duration in aggregated_data.items():
        print(f"Category: {category}, Duration: {duration:.2f} minutes")
