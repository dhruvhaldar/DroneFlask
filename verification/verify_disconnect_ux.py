from playwright.sync_api import sync_playwright
import os
import sys

def run():
    print("Verifying Offline UI State...")
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
            sys.exit(1)

        # Check UI Elements for disabled classes
        # The IDs we added: #ui-controls, #ui-cam-controls, #ui-telemetry, #ui-header

        elements_to_check = [
            ("#ui-controls", ["opacity-50", "grayscale", "pointer-events-none"]),
            ("#ui-cam-controls", ["opacity-50", "grayscale", "pointer-events-none"]),
            ("#ui-header", ["opacity-50", "grayscale", "pointer-events-none"]),
            ("#ui-telemetry", ["opacity-50", "grayscale"]) # We didn't add pointer-events-none to telemetry in JS
        ]

        failed = False
        for selector, expected_classes in elements_to_check:
            locator = page.locator(selector)
            if not locator.count():
                print(f"❌ FAIL: Element {selector} not found.")
                failed = True
                continue

            class_attr = locator.get_attribute("class") or ""
            print(f"Checking {selector}... Classes: '{class_attr}'")

            for cls in expected_classes:
                if cls not in class_attr:
                    print(f"  ❌ Missing class '{cls}'")
                    failed = True
                else:
                    print(f"  ✅ Has class '{cls}'")

        if failed:
             print("❌ Verification FAILED: Some elements are missing disabled state classes.")
             sys.exit(1)

        # Take Screenshot
        screenshot_path = "verification/disconnect_ux.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 Screenshot saved to {screenshot_path}")

        print("✅ PASS: Offline UX state is correct.")
        browser.close()

if __name__ == "__main__":
    run()
