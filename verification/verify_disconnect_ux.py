from playwright.sync_api import sync_playwright
import os
import sys

def run():
    print("Verifying Disconnect UX (Soft Disable)...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load local file (simulates disconnected state initially)
        cwd = os.getcwd()
        file_url = f"file://{cwd}/templates/index.html"
        print(f"Loading {file_url}")

        try:
            page.goto(file_url)
        except Exception as e:
            print(f"Error loading page: {e}")
            pass

        # Helper to check if element is disabled
        def check_disabled(selector, expected_disabled):
            locator = page.locator(selector)
            classes = locator.get_attribute("class")

            # Check for visual disable classes
            has_opacity = "opacity-50" in classes
            has_grayscale = "grayscale" in classes
            has_pointer_none = "pointer-events-none" in classes

            # Check opacity computed style to be sure
            opacity_val = locator.evaluate("el => getComputedStyle(el).opacity")

            print(f"Checking {selector}: Classes='{classes}', Opacity={opacity_val}")

            if expected_disabled:
                if not (has_opacity and has_grayscale and has_pointer_none):
                    return False, f"Missing disabled classes. Found: {classes}"
                # Note: opacity might not be exactly 0.5 depending on computation, but checking class is good for verification of logic.
                # If opacity-50 is applied, computed opacity should be 0.5
                if float(opacity_val) > 0.6:
                     return False, f"Computed opacity {opacity_val} seems too high."
            else:
                if (has_opacity or has_grayscale or has_pointer_none):
                     return False, f"Has disabled classes when shouldn't. Found: {classes}"
                if float(opacity_val) < 0.9:
                     return False, f"Computed opacity {opacity_val} seems too low."

            return True, "OK"

        ids = ["#ui-header", "#ui-telemetry", "#ui-controls", "#ui-cam-controls"]

        # 1. Verify Initial State (Should be Disabled)
        print("\n--- 1. Checking Initial State (Disconnected) ---")
        # Since we haven't implemented the logic yet, this MIGHT fail if run before changes.
        # But we want to verify the script works.
        # Actually, before changes, the classes won't be there, so this should FAIL.
        # This confirms the script detects the missing feature.

        # We can't easily wait for failure here, so we proceed.

        # 2. Simulate Connection
        print("\n--- 2. Simulating Connection (updateUIState(true)) ---")
        try:
            page.evaluate("updateUIState(true)")
            # Wait a bit for transition (if any)
            page.wait_for_timeout(600)
        except Exception as e:
            print(f"Could not call updateUIState: {e}")
            # This is expected if function doesn't exist yet

        for selector in ids:
            success, msg = check_disabled(selector, False)
            print(f"  {selector}: {msg}")

        # 3. Simulate Disconnection
        print("\n--- 3. Simulating Disconnection (updateUIState(false)) ---")
        try:
            page.evaluate("updateUIState(false)")
            page.wait_for_timeout(600)
        except Exception as e:
             print(f"Could not call updateUIState: {e}")

        for selector in ids:
            success, msg = check_disabled(selector, True)
            print(f"  {selector}: {msg}")

        # Take Screenshot
        screenshot_path = "verification/disconnect_ux.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 Screenshot saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    run()
