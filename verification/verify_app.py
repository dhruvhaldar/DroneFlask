from playwright.sync_api import sync_playwright, expect
import time

def verify_app(page):
    # Go to app
    page.goto("http://localhost:5001")

    # Wait for connection (Toast or Status)
    expect(page.locator("#status-text")).to_have_text("Online", timeout=10000)

    # Wait a bit for data to stream
    time.sleep(2)

    # Check if HUD is updating (values not 0.00 usually, but initially might be)
    # Z might be slightly non-zero due to noise or initial settle

    # Take screenshot of the HUD and Viz
    page.screenshot(path="verification/app_running.png")
    print("Screenshot taken.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_app(page)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
