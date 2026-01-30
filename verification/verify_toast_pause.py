from playwright.sync_api import sync_playwright
import os
import sys
import time

def run():
    print("Verifying Toast Pause on Hover...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        cwd = os.getcwd()
        file_url = f"file://{cwd}/templates/index.html"
        page.goto(file_url)

        # Trigger a toast
        print("Triggering toast...")
        page.evaluate("showToast('Pause Test', 'info')")
        toast = page.locator("#toast-container > div").first
        toast.wait_for(state="visible")

        # Hover over the toast
        print("Hovering over toast...")
        toast.hover()

        # Wait for 4 seconds (default timeout is 3s)
        print("Waiting for 4 seconds (should stay visible)...")
        time.sleep(4)

        # Check if toast is still visible
        if not toast.is_visible():
            print("❌ FAIL: Toast disappeared while hovering!")
            sys.exit(1)

        # Check if opacity is not 0 (since our dismiss logic sets opacity-0)
        classes = toast.get_attribute("class")
        if "opacity-0" in classes:
             print("❌ FAIL: Toast has opacity-0 class while hovering!")
             sys.exit(1)

        # Take screenshot
        page.screenshot(path="verification/toast_pause_hover.png")
        print("📸 Screenshot saved to verification/toast_pause_hover.png")

        print("✅ PASS: Toast remained visible while hovering.")

        # Move mouse away to top-left corner
        print("Moving mouse away...")
        page.mouse.move(0, 0)
        # Also trigger mouseleave event explicitly just in case Playwright hover behavior is sticky
        # But mouse.move should work if it leaves the element bounding box.

        # Wait for 4 seconds
        print("Waiting for 4 seconds (should disappear)...")
        time.sleep(4)

        # Check if toast is gone
        count = page.locator("#toast-container > div").count()
        if count > 0:
             print(f"❌ FAIL: Toast still present in DOM after timeout! Count: {count}")
             sys.exit(1)

        print("✅ PASS: Toast disappeared after mouse leave.")
        browser.close()

if __name__ == "__main__":
    run()
