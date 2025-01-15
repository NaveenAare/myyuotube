import os
import subprocess
import requests

def check_url_status(url):
    try:
        response = requests.get(url, timeout=5)  # Timeout after 5 seconds
        if response.status_code == 200:
            print(f"The URL '{url}' is up and running.")
        else:
            print(f"The URL '{url}' is reachable but returned status code {response.status_code}.")
    except requests.ConnectionError:
        print(f"The URL '{url}' is not reachable.")
        handle_unreachable_url()
    except requests.Timeout:
        print(f"The URL '{url}' timed out.")
        handle_unreachable_url()
    except Exception as e:
        print(f"An error occurred while checking the URL '{url}': {e}")
        handle_unreachable_url()

def handle_unreachable_url():
    try:
        # Remove all .mp3 and .mp4 files
        os.system("rm *.mp3")
        os.system("rm *.mp4")

        # Reload and restart the Flask application service
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        subprocess.run(["sudo", "systemctl", "restart", "flask_app"], check=True)

        print("Executed commands for unreachable URL.")
    except Exception as e:
        print(f"An error occurred while handling unreachable URL: {e}")

# URL to check
url = "https://youtubevideosdownloader.com/"
check_url_status(url)
