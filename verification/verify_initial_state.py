from playwright.sync_api import sync_playwright
import os

def test_initial_state():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Construct file URL
        cwd = os.getcwd()
        file_path = os.path.join(cwd, "templates", "index.html")
        url = f"file://{file_path}"

        print(f"Loading: {url}")
        page.goto(url)

        # Verify
        assert "Connecting..." in page.locator("#conn-title").inner_text()

        # Screenshot
        screenshot_path = "verification/initial_state.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    test_initial_state()
