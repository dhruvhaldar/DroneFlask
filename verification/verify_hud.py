from playwright.sync_api import sync_playwright

def verify_hud(page):
    page.goto("http://localhost:5001")
    # Wait for the HUD to load
    page.wait_for_selector("text=DroneFlask")

    # Check if Throttle is visible
    page.wait_for_selector("text=Throttle:")

    # Check if Takeoff button is visible
    page.wait_for_selector("#btn-takeoff")

    # Take a screenshot
    # Use absolute path to ensure it goes where we expect
    page.screenshot(path="/home/jules/verification/hud_verification.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            verify_hud(page)
            print("HUD verification script ran successfully.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
