import time
from playwright.sync_api import sync_playwright, expect

def verify_takeoff_shortcut():
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

        # 1. Verify 'T' Hint Visibility
        print("Checking 'T' Hint Visibility...")
        btn = page.locator("#btn-takeoff")
        expect(btn).to_be_visible()

        # Check aria-keyshortcuts
        keyshortcuts = btn.get_attribute("aria-keyshortcuts")
        if keyshortcuts == "t":
             print("SUCCESS: Takeoff button has aria-keyshortcuts='t'")
        else:
             print(f"FAILURE: Expected aria-keyshortcuts='t', got '{keyshortcuts}'")

        # Locate the hint (sibling kbd)
        # Playwright CSS selector for adjacent sibling is +
        hint = page.locator("#btn-takeoff + kbd")
        if not hint.count():
             print("Warning: Sibling selector failed, trying parent lookup")
             hint = page.locator("div.relative.group:has(#btn-takeoff) >> kbd")

        expect(hint).to_have_text("T")

        # Initial Opacity
        opacity_initial = float(hint.evaluate("el => getComputedStyle(el).opacity"))
        print(f"Initial Opacity: {opacity_initial}")

        if opacity_initial < 0.1:
             print("SUCCESS: Hint is hidden initially.")
        else:
             print("FAILURE: Hint should be hidden initially.")

        # Hover
        print("Hovering over Takeoff button...")
        btn.hover()
        time.sleep(0.5)

        # Screenshot of Hint
        page.screenshot(path="verification/hint_visible.png")
        print("Screenshot saved to verification/hint_visible.png")

        # Hover Opacity
        opacity_hover = float(hint.evaluate("el => getComputedStyle(el).opacity"))
        print(f"Hover Opacity: {opacity_hover}")

        if opacity_hover > 0.9:
            print("SUCCESS: Hint is visible on hover.")
        else:
            print("FAILURE: Hint is NOT visible on hover.")

        # 2. Verify 'T' Key Functionality
        print("Checking 'T' Key Functionality...")
        # Move mouse away to avoid hover interference? Shouldn't matter for key press.
        page.mouse.move(0, 0)
        page.keyboard.press("t")

        # Check for toast
        # "Initiating Takeoff Sequence"
        toast = page.locator("div#toast-container").get_by_text("Initiating Takeoff Sequence")
        try:
            expect(toast).to_be_visible(timeout=2000)
            print("SUCCESS: 't' key triggered Takeoff toast.")
            page.screenshot(path="verification/toast_visible.png")
            print("Screenshot saved to verification/toast_visible.png")
        except AssertionError:
            print("FAILURE: Toast not found after pressing 't'.")

        # 3. Verify Overlay Accessibility (Simulated)
        print("Checking Overlay Accessibility...")
        overlay = page.locator("#connection-overlay")

        # Wait for potential connection
        time.sleep(1)

        status_text = page.locator("#status-text").inner_text()
        print(f"Current Status: {status_text}")

        if status_text == "Online":
            # Should be hidden
            aria_hidden = overlay.get_attribute("aria-hidden")
            if aria_hidden == "true":
                print("SUCCESS: Overlay has aria-hidden='true' when Online.")
            else:
                print(f"FAILURE: Overlay should have aria-hidden='true' when Online, got '{aria_hidden}'.")
        else:
            print("Skipping Online check as app is not Online (sim might need more time or deps missing).")

        browser.close()

if __name__ == "__main__":
    verify_takeoff_shortcut()
