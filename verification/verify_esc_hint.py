import time
from playwright.sync_api import sync_playwright, expect

def verify_esc_hint():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        print("Navigating to app...")
        try:
            page.goto("http://localhost:5001", timeout=5000)
        except Exception as e:
            print(f"Error navigating: {e}")
            return

        # 1. Verify Hint Visibility via Opacity
        print("Checking Hint Visibility...")
        btn = page.locator("#btn-reset")
        expect(btn).to_be_visible()

        hint = page.locator("kbd", has_text="Esc")

        # Initial Opacity
        opacity_initial = float(hint.evaluate("el => getComputedStyle(el).opacity"))
        print(f"Initial Opacity: {opacity_initial}")

        if opacity_initial > 0.1:
             print("FAILURE: Hint should be hidden (opacity 0) initially.")
        else:
             print("SUCCESS: Hint is hidden initially.")


        # Hover
        print("Hovering over button...")
        btn.hover()
        # Wait for transition (500ms should be enough for 200ms transition)
        time.sleep(0.5)

        # Screenshot
        page.screenshot(path="verification/esc_hint_visible.png")
        print("Screenshot saved to verification/esc_hint_visible.png")

        # Hover Opacity
        opacity_hover = float(hint.evaluate("el => getComputedStyle(el).opacity"))
        print(f"Hover Opacity: {opacity_hover}")

        if opacity_hover > 0.9:
            print("SUCCESS: Hint is visible on hover.")
        else:
            print("FAILURE: Hint is NOT visible on hover.")

        # 2. Verify Escape Key Functionality
        print("Checking Escape Key Functionality...")

        # Press Escape
        page.keyboard.press("Escape")

        # Check for toast
        toast = page.locator("div#toast-container >> text=Engines Cut")
        try:
            expect(toast).to_be_visible(timeout=2000)
            print("SUCCESS: Escape key triggered 'Engines Cut' toast.")
        except AssertionError:
            print("FAILURE: Toast not found after pressing Escape.")
            page.screenshot(path="verification/failure_esc.png")

        browser.close()

if __name__ == "__main__":
    verify_esc_hint()
