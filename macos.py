import subprocess
import psutil
import os
import json


class MacOSMonitor:
    """
    Specific monitor for macOS that uses platform-specific APIs to get
    detailed application and browser activity.
    """

    def __init__(self):
        # Cache for app bundle info to avoid repeated file system calls
        self._bundle_cache = {}

    def get_active_window(self) -> str:
        """
        Gets the real name of the currently active application.
        For Electron apps, returns the actual app name (e.g., "Visual Studio Code")
        instead of just "Electron".
        """
        try:
            active_window_pid = self._get_active_window_pid()
            if active_window_pid:
                process = psutil.Process(active_window_pid)
                process_name = process.name()

                # If it's an Electron app, get the real name
                if process_name in ["Electron", "electron"]:
                    real_name = self._get_real_app_name(process)
                    return real_name if real_name else process_name

                return process_name
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
        return None

    def _get_active_window_pid(self) -> int:
        """
        Helper function to find the PID of the active window on macOS.
        """
        applescript = 'tell application "System Events" to get unix id of first process whose frontmost is true'
        try:
            result = subprocess.run(
                ["osascript", "-e", applescript], capture_output=True, text=True
            )
            return int(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            return None

    def _get_real_app_name(self, process):
        """
        Get the real app name from an Electron process by checking its app bundle.
        """
        try:
            exe_path = process.exe()

            # Check if it's in an app bundle
            if ".app/" in exe_path:
                app_bundle_path = exe_path.split(".app/")[0] + ".app"

                # Use cache to avoid repeated file system calls
                if app_bundle_path in self._bundle_cache:
                    return self._bundle_cache[app_bundle_path]

                bundle_info = self._get_app_bundle_info(app_bundle_path)

                if bundle_info:
                    # Prefer display name, then bundle name
                    real_name = (
                        bundle_info.get("display_name")
                        or bundle_info.get("bundle_name")
                        or process.name()
                    )

                    # Cache the result
                    self._bundle_cache[app_bundle_path] = real_name
                    return real_name

            # Fallback: try to get name from command line arguments
            cmdline = process.cmdline()
            if cmdline:
                for arg in cmdline:
                    if ".app/" in arg:
                        app_name = os.path.basename(arg.split(".app/")[0] + ".app")
                        return app_name.replace(".app", "")

            return process.name()

        except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
            return process.name()

    def _get_app_bundle_info(self, app_path):
        """Get app bundle information from Info.plist"""
        info_plist_path = os.path.join(app_path, "Contents", "Info.plist")

        if not os.path.exists(info_plist_path):
            return None

        try:
            # Use plutil to convert plist to JSON
            result = subprocess.run(
                ["plutil", "-convert", "json", "-o", "-", info_plist_path],
                capture_output=True,
                text=True,
                check=True,
            )
            plist_data = json.loads(result.stdout)

            return {
                "bundle_name": plist_data.get("CFBundleName", ""),
                "display_name": plist_data.get("CFBundleDisplayName", ""),
                "bundle_id": plist_data.get("CFBundleIdentifier", ""),
                "executable": plist_data.get("CFBundleExecutable", ""),
            }
        except:
            return None

    def get_all_electron_apps(self):
        """Get all running Electron apps with their real names"""
        electron_apps = []

        for proc in psutil.process_iter(["pid", "name", "exe"]):
            try:
                proc_info = proc.info

                # Check if it's an Electron app
                if proc_info["name"] in ["Electron", "electron"]:
                    real_name = self._get_real_app_name(proc)

                    electron_apps.append(
                        {
                            "pid": proc_info["pid"],
                            "process_name": proc_info["name"],
                            "real_name": real_name,
                            "exe_path": proc_info["exe"],
                        }
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return electron_apps

    def get_app_name_by_pid(self, pid: int) -> str:
        """
        Get the real app name for a given PID.
        Useful for getting proper names for Electron apps.
        """
        try:
            process = psutil.Process(pid)
            process_name = process.name()

            if process_name in ["Electron", "electron"]:
                real_name = self._get_real_app_name(process)
                return real_name if real_name else process_name

            return process_name
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def get_chrome_activity(self) -> dict:
        """
        Executes AppleScript to get the title and URL of the active Chrome tab.
        Returns a dictionary with window name, active tab title, and active tab URL.
        """
        applescript = """
        tell application "Google Chrome"
            if running then
                try
                    set front_window to front window
                    set active_tab to active tab of front_window
                    set tabTitle to title of active_tab
                    set tabURL to URL of active_tab
                    return tabTitle & "|||" & tabURL
                on error
                    return "No active tab|||"
                end try
            else
                return "Not running|||"
            end if
        end tell
        """

        result = subprocess.run(
            ["osascript", "-e", applescript], capture_output=True, text=True
        )
        raw_output = result.stdout.strip()

        # Split the AppleScript return into parts
        parts = raw_output.split("|||")
        tab_title = parts[0] if len(parts) > 0 else None
        tab_url = parts[1] if len(parts) > 1 else None

        return {
            "window_name": "Google Chrome",
            "active_tab_title": tab_title,
            "active_tab_url": tab_url,
        }

    # def get_all_chrome_tabs(self) -> dict:
    #     """
    #     Executes AppleScript to get the titles and URLs of all open Chrome tabs.
    #     The result is a dictionary of windows, each containing a list of tabs.
    #     """
    #     applescript = """
    #     tell application "Google Chrome"
    #         set output to ""
    #         repeat with w from 1 to count of windows
    #             set output to output & "WINDOW:" & w & "\\n"
    #             repeat with t from 1 to count of tabs in window w
    #                 set tabTitle to title of tab t of window w
    #                 set tabURL to URL of tab t of window w
    #                 set output to output & "TAB:" & tabTitle & "|||" & tabURL & "\\n"
    #             end repeat
    #             set output to output & "ENDWINDOW\\n"
    #         end repeat
    #         return output
    #     end tell
    #     """
    #     result = subprocess.run(
    #         ["osascript", "-e", applescript], capture_output=True, text=True
    #     )
    #     raw_output = result.stdout

    #     # Parse the raw output into a structured dictionary
    #     data = {}
    #     current_window_key = None
    #     for line in raw_output.strip().split("\n"):
    #         if line.startswith("WINDOW:"):
    #             current_window_key = line.strip()
    #             data[current_window_key] = []
    #         elif line.startswith("TAB:") and current_window_key:
    #             # Remove "TAB:" prefix and split the title and URL
    #             tab_info = line[4:].strip().split("|||", 1)
    #             if len(tab_info) == 2:
    #                 data[current_window_key].append(
    #                     {"title": tab_info[0], "url": tab_info[1]}
    #                 )
    #     return data


# Example usage and testing
if __name__ == "__main__":
    monitor = MacOSMonitor()

    print("=== Current Active Window ===")
    active_app = monitor.get_active_window()
    print(f"Active app: {active_app}")

    print("\n=== All Electron Apps ===")
    electron_apps = monitor.get_all_electron_apps()
    for app in electron_apps:
        print(f"  {app['real_name']} (PID: {app['pid']})")

    print("\n=== Test PID Lookup ===")
    active_pid = monitor._get_active_window_pid()
    if active_pid:
        app_name = monitor.get_app_name_by_pid(active_pid)
        print(f"PID {active_pid}: {app_name}")
