from playwright.sync_api import sync_playwright, expect

def verify_changes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:5001")

        # Verify Header
        header = page.locator("header")
        expect(header).to_be_visible()

        # Verify Status Transition
        status_text = page.locator("#status-text")
        expect(status_text).to_have_class("text-green-400 font-medium transition-colors duration-500")

        # Verify Telemetry Aside
        telemetry = page.locator("aside[aria-label='Telemetry']")
        expect(telemetry).to_be_visible()

        # Verify Tabular Nums
        val_z = page.locator("#val-z")
        expect(val_z).to_have_class("font-mono tabular-nums text-blue-300 cursor-pointer hover:bg-white/10 rounded px-1 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400")

        # Verify Footer
        footer = page.locator("footer[aria-label='Flight Controls']")
        expect(footer).to_be_visible()

        # Take screenshot
        page.screenshot(path="verification/semantic_changes.png")
        print("Verification successful, screenshot saved to verification/semantic_changes.png")

        browser.close()

if __name__ == "__main__":
    verify_changes()
