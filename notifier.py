from plyer import notification

class Notifier:
    """
    Handles sending cross-platform desktop notifications.
    """

    def send_notification(self, title: str, message: str, timeout: int = 10):
        """
        Displays a desktop notification with a given title and message.

        Args:
            title (str): The title of the notification.
            message (str): The main message content.
            timeout (int): The duration in seconds the notification should be displayed.
        """
        # app_icon = join(dirname(realpath(__file__)),'assets/favicon.ico')
        kwargs = {
            "title": title,
            "message": message,
            # 'app_icon': app_icon,  # Not supported on macOS
            # 'timeout': timeout,  # Not supported on macOS
        }
        try:
            notification.notify(**kwargs)
        except Exception as e:
            # Fallback for platforms where plyer may not work or is not configured
            print(f"Failed to send notification: {e}")
            print(f"Title: {title}\nMessage: {message}")


# For testing purposes
if __name__ == "__main__":
    notifier = Notifier()
    print("Sending a test notification...")
    test_title = "Bilge Test"
    test_message = "This is a test notification from your Bilge app."
    notifier.send_notification(test_title, test_message, timeout=5)
    print("Test notification sent. Check your desktop.")
