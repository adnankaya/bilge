import platform
import datetime
import time

# Import platform-specific monitors
if platform.system() == "Darwin":
    from macos import MacOSMonitor as PlatformMonitor
elif platform.system() == "Windows":
    # from monitor_windows import WindowsMonitor as PlatformMonitor
    # For now, we will use a basic placeholder
    class WindowsMonitor:
        def get_active_window(self):
            # Placeholder for Windows implementation
            return "Windows App"

    PlatformMonitor = WindowsMonitor
else:
    # Basic fallback for other systems
    class GenericMonitor:
        def get_active_window(self):
            return "Generic App"

    PlatformMonitor = GenericMonitor


class Monitor:
    """
    Main monitor class that acts as a wrapper for platform-specific implementations.
    """

    def __init__(self):
        self._platform_monitor = PlatformMonitor()
        self.last_change_time = datetime.datetime.now()

    def get_active_window(self) -> str:
        """
        Retrieves the name of the currently active application/window using the
        appropriate platform-specific method.
        """
        active_app = self._platform_monitor.get_active_window()

        # If the active app is Chrome on macOS, we can get more detailed info
        if platform.system() == "Darwin" and active_app == "Google Chrome":
            chrome_activity = self._platform_monitor.get_chrome_activity()
            return chrome_activity
        return active_app


# For testing purposes
if __name__ == "__main__":
    monitor = Monitor()
    print("Monitoring active windows. Press Ctrl+C to exit.")

    last_app = None
    while True:
        current_app = monitor.get_active_window()
        if current_app and current_app != last_app:
            print(f"Active app changed to: {current_app}")
            last_app = current_app

        time.sleep(1)
