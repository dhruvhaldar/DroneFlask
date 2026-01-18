from playwright.sync_api import sync_playwright
import os
import sys

def run():
    print("Verifying Initial System Status UX...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load local file
        cwd = os.getcwd()
        file_url = f"file://{cwd}/templates/index.html"
        print(f"Loading {file_url}")

        try:
            page.goto(file_url)
        except Exception as e:
            print(f"Error loading page: {e}")
            pass

        # Check initial status text
        status_text_locator = page.locator("#status-text")
        status_text = status_text_locator.inner_text()
        print(f"Initial Status Text: '{status_text}'")

        # Check initial status color (Yellow-400 is text-yellow-400)
        class_attr = status_text_locator.get_attribute("class")
        print(f"Initial Status Classes: '{class_attr}'")

        # Validation
        if "Connecting..." not in status_text:
             print("❌ FAIL: Status text should be 'Connecting...'. Found: " + status_text)
             sys.exit(1)

        if "text-yellow-400" not in class_attr:
             print("❌ FAIL: Status text should have 'text-yellow-400' class.")
             sys.exit(1)

        # Check Ping is hidden
        ping_locator = page.locator("#status-ping")
        ping_class = ping_locator.get_attribute("class")
        if "hidden" not in ping_class:
             print("❌ FAIL: Ping animation should be hidden by default.")
             sys.exit(1)

        # Take Screenshot
        screenshot_path = "verification/status_ux.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 Screenshot saved to {screenshot_path}")

        print("✅ PASS: Initial status UX is correct.")
        browser.close()

if __name__ == "__main__":
    run()
