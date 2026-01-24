from playwright.sync_api import sync_playwright
import os
import sys
import time

def run():
    print("Verifying Disconnect UX (Soft Disable)...")
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

        # Helper to check classes
        def check_dimmed(element_name, selector, should_be_dimmed):
            locator = page.locator(selector)
            # wait for element to be attached
            locator.wait_for(state="attached")
            classes = locator.get_attribute("class")

            is_dimmed = "opacity-50" in classes and "grayscale" in classes

            status = "DIMMED" if is_dimmed else "ACTIVE"
            expected = "DIMMED" if should_be_dimmed else "ACTIVE"

            print(f"Checking {element_name}: Found {status}, Expected {expected}")

            if is_dimmed != should_be_dimmed:
                print(f"❌ FAIL: {element_name} state mismatch. Classes: {classes}")
                return False
            return True

        # 1. Check Initial State (Should be disconnected -> Dimmed)
        print("\n--- 1. Checking Initial State (Disconnected) ---")
        # Give a moment for initial script to run
        page.wait_for_timeout(500)

        success = True
        success &= check_dimmed("Telemetry Panel", "#telemetry-panel", True)
        success &= check_dimmed("Controls Footer", "#controls-footer", True)

        if not success:
            print("Initial state check failed. Ensure elements have IDs and initial dimmed state.")
            sys.exit(1)

        # 2. Simulate Connect
        print("\n--- 2. Simulating Connect Event ---")
        page.evaluate("updateUIState(true)")
        page.wait_for_timeout(600) # Wait for transition (500ms)

        success &= check_dimmed("Telemetry Panel", "#telemetry-panel", False)
        success &= check_dimmed("Controls Footer", "#controls-footer", False)

        if not success:
            print("Connect state check failed.")
            sys.exit(1)

        # 3. Simulate Disconnect
        print("\n--- 3. Simulating Disconnect Event ---")
        page.evaluate("updateUIState(false)")
        page.wait_for_timeout(600) # Wait for transition

        success &= check_dimmed("Telemetry Panel", "#telemetry-panel", True)
        success &= check_dimmed("Controls Footer", "#controls-footer", True)

        if not success:
            print("Disconnect state check failed.")
            sys.exit(1)

        # Take Screenshot
        screenshot_path = "verification/disconnect_ux.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 Screenshot saved to {screenshot_path}")

        print("✅ PASS: Disconnect UX (Soft Disable) verified.")
        browser.close()

if __name__ == "__main__":
    run()
