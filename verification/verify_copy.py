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

            # Use a context to grant permissions if needed (clipboard-write usually needs focus/permission)
            # But in headless mode, it might just work or we might need to mock navigator.clipboard
            context = browser.new_context(permissions=['clipboard-write'])
            page = context.new_page()

            # Navigate to the app
            page.goto("http://localhost:5001")

            # Wait for content
            page.wait_for_selector("#ui-layer")

            # 1. Check if elements have the right attributes
            val_z = page.locator("#val-z")
            assert val_z.get_attribute("role") == "button"
            assert val_z.get_attribute("title") == "Click to copy"
            assert "cursor-pointer" in val_z.get_attribute("class")

            # 2. Test Click-to-Copy
            # Since real clipboard access in headless might be tricky, we can check if the Toast appears
            # and if the class changes to green (text-green-400)

            val_z.click()

            # Check for toast
            toast = page.locator("#toast-container div", has_text="Altitude copied!")
            toast.wait_for(state="visible", timeout=2000)
            print("Toast notification appeared successfully.")

            # Check for class change (it flashes green)
            # We might need to check immediately after click
            assert "text-green-400" in val_z.get_attribute("class")
            print("Visual feedback (green text) verified.")

            # Take screenshot of the interaction
            page.screenshot(path="after_changes.png")
            print("Screenshot taken: after_changes.png")

            browser.close()

    finally:
        # Kill the process
        os.kill(process.pid, signal.SIGTERM)
        process.wait()

if __name__ == "__main__":
    verify_frontend()
