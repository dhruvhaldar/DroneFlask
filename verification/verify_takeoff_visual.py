from playwright.sync_api import sync_playwright
import os
import sys

def run():
    print("Capturing Takeoff Shortcut Verification...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        cwd = os.getcwd()
        file_url = f"file://{cwd}/templates/index.html"
        page.goto(file_url)

        # 1. Hover over the Takeoff button to show the tooltip
        # The button is id="btn-takeoff"
        # The group is the parent div.
        btn = page.locator("#btn-takeoff")
        btn.hover()

        # Take a screenshot of the Actions area
        # Locate the actions group
        actions_group = page.get_by_role("group", name="Flight Actions")

        # Ensure tooltip is visible
        tooltip = actions_group.locator("kbd", has_text="T")
        tooltip.wait_for(state="visible")

        screenshot_path = "verification/takeoff_shortcut_visual.png"
        actions_group.screenshot(path=screenshot_path)
        print(f"📸 Screenshot saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    run()
