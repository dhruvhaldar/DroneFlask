from playwright.sync_api import sync_playwright
import os
import sys

def run():
    print("Verifying Toast Interaction Fix...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        cwd = os.getcwd()
        file_url = f"file://{cwd}/templates/index.html"
        page.goto(file_url)

        # Trigger a toast
        page.evaluate("showToast('Test Message', 'info')")

        # Wait for toast to appear
        toast = page.locator("#toast-container > div").first
        toast.wait_for(state="visible")

        # Check computed style for pointer-events
        pointer_events = toast.evaluate("el => getComputedStyle(el).pointerEvents")
        print(f"Toast pointer-events: {pointer_events}")

        if pointer_events != "auto":
            print(f"❌ FAIL: Toast should be interactive (pointer-events: auto), but found: {pointer_events}")
            sys.exit(1)
        else:
            print("✅ PASS: Toast is interactive.")

        # Also verify the button has type="button"
        btn = toast.locator("button")
        btn_type = btn.get_attribute("type")
        if btn_type != "button":
            print(f"❌ FAIL: Dismiss button should have type='button', found: {btn_type}")
            sys.exit(1)
        else:
             print("✅ PASS: Dismiss button has correct type.")

        # Focus the button to show the ring
        btn.focus()

        # Take Screenshot
        screenshot_path = "verification/toast_interaction.png"
        page.screenshot(path=screenshot_path)
        print(f"📸 Screenshot saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    run()
