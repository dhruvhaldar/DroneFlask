from playwright.sync_api import sync_playwright
import os
import sys
import time

def run():
    print("Verifying Error Toast Persistence...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        cwd = os.getcwd()
        file_url = f"file://{cwd}/templates/index.html"
        page.goto(file_url)

        # Trigger an error toast
        print("Triggering error toast...")
        page.evaluate("showToast('Test Error', 'error')")

        # Wait for toast to appear
        toast = page.locator("#toast-container > div[role='alert']").first
        toast.wait_for(state="visible")
        print("Toast appeared.")

        # Wait for 3.5 seconds (should disappear if bug is present)
        print("Waiting 3.5 seconds...")
        time.sleep(3.5)

        # Check visibility
        if toast.is_visible():
            print("✅ PASS: Error toast is still visible.")
            page.screenshot(path="verification/error_toast_persistence.png")
            print("📸 Screenshot saved to verification/error_toast_persistence.png")
        else:
            print("❌ FAIL: Error toast disappeared.")
            sys.exit(1)

        browser.close()

if __name__ == "__main__":
    run()
