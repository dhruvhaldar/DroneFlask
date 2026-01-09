
from playwright.sync_api import sync_playwright, expect
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Start app first (assuming it runs on 5001)
        # Note: I need to start the app in background in the bash session first

        try:
            page.goto("http://127.0.0.1:5001")

            # Verify basic elements load
            expect(page.get_by_role("heading", name="DroneFlask")).to_be_visible()

            # Press W to increase throttle
            page.keyboard.down("w")
            time.sleep(0.5) # Hold for 500ms
            page.keyboard.up("w")

            # Check if throttle bar updated (meaning controls work)
            throttle_bar = page.locator("#throttle-bar")
            expect(throttle_bar).not_to_have_attribute("aria-valuenow", "0")

            # Take screenshot
            page.screenshot(path="verification/verification.png")
            print("Verification successful")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
