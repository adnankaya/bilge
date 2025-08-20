import datetime
import subprocess


def get_date():
    """Returns the current date in YYYY-MM-DD format.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_date_time():
    """Returns the current date and time in YYYY-MM-DD HH:MM:SS format.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def debug_applescript_output():
    """Debug function to see raw AppleScript output"""
    applescript = '''
    tell application "Google Chrome"
        set output to ""
        repeat with w from 1 to count of windows
            set output to output & "WINDOW:" & w & "\\n"
            repeat with t from 1 to count of tabs in window w
                set tabTitle to title of tab t of window w
                set tabURL to URL of tab t of window w
                set output to output & "TAB:" & tabTitle & "|||" & tabURL & "\\n"
            end repeat
            set output to output & "ENDWINDOW\\n"
        end repeat
        return output
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', applescript], 
                          capture_output=True, text=True)
    print("Raw output:")
    print(result.stdout)
    print("Error (if any):")
    print(result.stderr)

if __name__ == "__main__":
    debug_applescript_output()
