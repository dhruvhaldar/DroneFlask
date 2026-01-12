import time
from playwright.sync_api import sync_playwright, expect

def verify_keys(page):
    page.goto("http://localhost:5001")

    # Wait for page to load
    page.wait_for_selector("#key-w")

    # Check attributes for 'W' key
    key_w = page.locator("#key-w")
    expect(key_w).to_have_attribute("role", "button")
    expect(key_w).to_have_attribute("tabindex", "0")
    expect(key_w).to_have_attribute("aria-label", "Increase Thrust (W)")
    expect(key_w).to_have_class(re.compile(r"cursor-pointer"))

    print("Attributes verified for key-w")

    # Verify visual highlight on click (mouse)
    # Take initial screenshot of controls
    controls = page.locator(".glass.interactive").last # The controls container is likely the last glass interactive element

    # Wait for connection to settle (toast might appear)
    time.sleep(2)

    # Hover over W key to show hover state
    key_w.hover()
    time.sleep(0.5)
    page.screenshot(path="verification/hover_w.png")
    print("Hover screenshot taken")

    # Click/Press W key (simulating mouse down)
    # The app uses mousedown/touchstart for activation
    # We can trigger mousedown via dispatch_event or just mouse.down()

    box = key_w.bounding_box()
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.mouse.down()
    time.sleep(0.5) # Wait for highlight

    # Verify class has changed (bg-blue-600)
    expect(key_w).to_have_class(re.compile(r"bg-blue-600"))

    page.screenshot(path="verification/press_w.png")
    print("Press screenshot taken")

    page.mouse.up()
    time.sleep(0.5)

    # Verify highlight removed
    expect(key_w).not_to_have_class(re.compile(r"bg-blue-600"))
    print("Release verified")

import re

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_keys(page)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
