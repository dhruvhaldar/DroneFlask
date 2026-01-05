from playwright.sync_api import sync_playwright, expect
import time
import re

def verify_throttle_bar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the app
        page.goto("http://127.0.0.1:5001")

        # Wait for the page to load
        expect(page.get_by_role("heading", name="DroneFlask")).to_be_visible()

        # Check initial state (Throttle: 0%)
        bar = page.locator("#throttle-bar")
        expect(bar).to_have_attribute("aria-valuenow", "0")

        # Click Takeoff (sets throttle to 40%)
        page.get_by_role("button", name="Takeoff").click()

        # Wait for update
        time.sleep(1.0) # Allow slight delay for socket/JS

        # Check updated state
        expect(bar).to_have_attribute("aria-valuenow", "40")
        # Just check if width attribute in style is set, checking computed style is tricky with %
        # We can check the style attribute directly
        expect(bar).to_have_attribute("style", re.compile(r"width:\s*40%;?"))

        # Take screenshot
        page.screenshot(path="verification/throttle_verification.png")
        print("Screenshot saved to verification/throttle_verification.png")

        browser.close()

if __name__ == "__main__":
    try:
        verify_throttle_bar()
        print("Verification script finished successfully.")
    except Exception as e:
        print(f"Verification failed: {e}")
        exit(1)
