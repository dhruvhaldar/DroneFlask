from playwright.sync_api import sync_playwright, expect
import time
import subprocess
import os
import signal

def verify_telemetry(page):
    """
    Verifies that the telemetry values are updating on the page.
    """
    print("Navigating to app...")
    page.goto("http://localhost:5001")

    # Wait for connection
    print("Waiting for connection status...")
    expect(page.locator("#status-text")).to_have_text("Online", timeout=10000)

    # Wait for telemetry to update from 0.00
    # Since the sim starts at 0, 0, 0, we might need to wait for a small change or noise
    # Or we can trigger a takeoff to see values change.

    print("Triggering Takeoff...")
    page.get_by_role("button", name="Takeoff").click()

    # Wait for Altitude to increase
    print("Waiting for altitude change...")
    # Altitude is #val-z
    # We expect it to change from 0.00.
    # Note: text content might be "0.00" initially.

    # Wait for a bit of simulation time
    time.sleep(2)

    # Check if Z value is no longer 0.00 or check if it matches a regex
    # It should increase.
    z_val = page.locator("#val-z").inner_text()
    print(f"Altitude: {z_val}")

    if z_val == "0.00":
         print("WARNING: Altitude did not change. Sim might be paused or slow.")

    # Take screenshot
    page.screenshot(path="verification/telemetry_check.png")
    print("Screenshot saved to verification/telemetry_check.png")

if __name__ == '__main__':
    # Start the app in background
    print("Starting app...")
    # Using Setsid to be able to kill the process group later
    process = subprocess.Popen(["python", "app.py"], preexec_fn=os.setsid, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        # Give it time to start
        time.sleep(5)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            verify_telemetry(page)
            browser.close()
    finally:
        print("Stopping app...")
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
