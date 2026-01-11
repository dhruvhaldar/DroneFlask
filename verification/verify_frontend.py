from playwright.sync_api import sync_playwright
import time
import subprocess
import os
import signal

def verify_frontend():
    # Start the app in a subprocess
    env = os.environ.copy()
    process = subprocess.Popen(["python", "app.py"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        # Give it time to start
        time.sleep(3)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Navigate to the app
            page.goto("http://localhost:5001")

            # Wait for content
            page.wait_for_selector("#ui-layer")

            # Take screenshot of initial state
            page.screenshot(path="before_changes.png")
            print("Screenshot taken: before_changes.png")

            # Check for key elements
            assert page.is_visible("#toast-container")
            assert page.is_visible("#val-z")

            browser.close()

    finally:
        # Kill the process
        os.kill(process.pid, signal.SIGTERM)
        process.wait()

if __name__ == "__main__":
    verify_frontend()
