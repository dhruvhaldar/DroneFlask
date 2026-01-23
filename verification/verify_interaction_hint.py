from playwright.sync_api import sync_playwright
import time
import subprocess
import os
import signal

def verify_interaction_hint():
    # Start the app in a subprocess
    env = os.environ.copy()
    process = subprocess.Popen(["python", "app.py"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        # Give it time to start
        time.sleep(10)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Debug console
            page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
            page.on("pageerror", lambda exc: print(f"PAGE ERROR: {exc}"))

            # Navigate to the app
            page.goto("http://127.0.0.1:5001")

            # Wait for content
            page.wait_for_selector("#ui-layer")

            # 1. Check if hint is initially visible
            # Note: It might be added dynamically or just exist.
            # We expect it to be in the DOM.
            hint = page.locator("#interaction-hint")
            if not hint.is_visible():
                print("Hint not visible initially.")

            # Assert it IS visible (will fail until implemented)
            # assert hint.is_visible() # Commented out for initial run, uncomment for verification
            # Actually, for the tool flow, I'll rely on the output "Hint not visible initially" to confirm it's missing.
            # But to be rigorous, I will add a check that prints failure.

            if not hint.is_visible():
                print("FAILURE: Hint element not visible.")
            else:
                print("SUCCESS: Hint element visible.")
                page.screenshot(path="verification/interaction_hint_visible.png")

            # 2. Simulate interaction
            # Click on canvas (center of screen roughly)
            # Use force=True to ensure we click the canvas even if Playwright thinks it's covered
            # (though it shouldn't be if overlays are pointer-events-none)
            page.locator("#canvas-container").click(force=True)

            # Also dispatch manually to be sure
            page.evaluate("window.dispatchEvent(new MouseEvent('mousedown', {bubbles: true, view: window}))")

            # 3. Verify it fades out
            # It has transition-opacity duration-1000.
            # We wait a bit.
            time.sleep(1.5)

            # Check class list for opacity-0
            # or check computed style
            # The element might still be 'visible' to playwright if it just has opacity: 0
            # So we check class.

            # We expect 'opacity-0' in class list
            classes = hint.get_attribute("class")
            if "opacity-0" in classes:
                print("SUCCESS: Hint faded out (opacity-0 class present).")
            else:
                print(f"FAILURE: Hint did not fade out. Classes: {classes}")

            print("Interaction simulation complete.")

            browser.close()

    finally:
        # Kill the process
        os.kill(process.pid, signal.SIGTERM)
        process.wait()

if __name__ == "__main__":
    verify_interaction_hint()
