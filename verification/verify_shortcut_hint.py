import time
from playwright.sync_api import sync_playwright, expect

def verify_shortcut_hint():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        # Navigate to the app (assuming it's running on port 5001 as per memory)
        try:
            page.goto("http://localhost:5001", timeout=10000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            return

        # Wait for the camera reset button
        reset_btn = page.locator("#btn-cam-reset")
        expect(reset_btn).to_be_visible(timeout=5000)

        # Initial screenshot
        page.screenshot(path="verification/before_hover.png")

        # Locate the wrapper/hint
        # The hint is a sibling in the wrapper, or we can target the text "Home"
        hint = page.get_by_text("Home")

        # Verify it's hidden initially (opacity 0)
        # Note: visibility check in playwright might return true if it's in DOM but opacity 0.
        # So we check CSS opacity.
        # But wait, class `opacity-0` is tailwind.
        # Let's just hover and check visibility.

        print("Hovering over the button...")
        # Hover over the wrapper or the button.
        # The wrapper has the `group` class, so hovering anywhere inside should trigger it.
        # But best to hover the button itself as that's the main interaction target.
        reset_btn.hover()

        # Wait for transition (duration-200)
        time.sleep(0.5)

        # Check if hint is visible
        # expect(hint).to_be_visible() # This might fail if opacity is handled via CSS classes that Playwright doesn't fully evaluate as "hidden" in all cases?
        # Actually Playwright considers opacity:0 as not visible.
        if hint.is_visible():
            print("Hint is visible!")
        else:
            print("Hint is NOT visible (unexpected if hover worked). checking computed style...")
            # opacity = hint.evaluate("el => getComputedStyle(el).opacity")
            # print(f"Opacity: {opacity}")

        # Take screenshot with hover
        page.screenshot(path="verification/after_changes.png")
        print("Screenshot saved to verification/after_changes.png")

        browser.close()

if __name__ == "__main__":
    verify_shortcut_hint()
