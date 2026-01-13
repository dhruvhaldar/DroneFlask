from playwright.sync_api import sync_playwright, expect
import time

def verify_controls_ux(page):
    page.goto("http://localhost:5001")

    # Wait for the control bar to appear
    control_bar = page.locator('div[role="toolbar"][aria-label="Flight Controls"]')
    expect(control_bar).to_be_visible()

    # Verify groupings
    thrust_group = page.locator('div[role="group"][aria-label="Thrust Controls"]')
    expect(thrust_group).to_be_visible()

    # Verify icons in buttons
    takeoff_btn = page.locator("#btn-takeoff")
    expect(takeoff_btn).to_contain_text("🚀")

    kill_btn = page.locator("#btn-reset")
    expect(kill_btn).to_contain_text("🛑")

    # Verify visual separator is hidden from accessibility tree
    # (We can't easily check a11y tree in simple playwright script without a11y engine,
    # but we can check the attribute exists)
    separators = page.locator('span[aria-hidden="true"]')
    expect(separators.first).to_be_visible()

    # Take a screenshot of the control bar
    # We need to wait a bit for styles to settle
    time.sleep(1)

    # Screenshot the specific element
    control_bar.screenshot(path="verification/control_bar_ux.png")
    print("Screenshot taken: verification/control_bar_ux.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_controls_ux(page)
        except Exception as e:
            print(f"Error: {e}")
            raise e
        finally:
            browser.close()
