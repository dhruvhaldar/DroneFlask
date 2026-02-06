from playwright.sync_api import sync_playwright, expect
import time
import subprocess
import sys
import os

APP_URL = "http://127.0.0.1:5001"

def verify_throttle_hold():
    # Start App
    print("Starting App...")
    proc = subprocess.Popen([sys.executable, "app.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5) # Wait for start

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(APP_URL)

            # Wait for connection
            expect(page.locator("#status-text")).to_have_text("Online", timeout=10000)

            # Initial Throttle
            thr_elem = page.locator("#val-thr")
            initial_thr = float(thr_elem.inner_text())
            print(f"Initial Throttle: {initial_thr}")

            # Locate 'W' key
            w_btn = page.locator("#key-w")

            # Simulate Hold: Mouse Down, Wait, Mouse Up
            print("Holding W for 500ms...")
            box = w_btn.bounding_box()
            page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            page.mouse.down()
            time.sleep(0.5) # Should trigger ~10 updates (50ms interval) -> +20%
            page.mouse.up()

            # Check Final Throttle
            final_thr = float(thr_elem.inner_text())
            print(f"Final Throttle: {final_thr}")

            # Screenshot
            page.screenshot(path="verification_throttle.png")

            # Assert
            # If auto-repeat works, it should be significantly higher than initial + 2% (single click)
            # 500ms / 50ms = 10 steps. 10 * 2 = 20%.
            # Allow some margin.
            if final_thr > initial_thr + 10:
                print("SUCCESS: Throttle increased significantly (Auto-repeat works).")
            else:
                print(f"FAILURE: Throttle only increased by {final_thr - initial_thr} (Auto-repeat failed).")
                exit(1)

    finally:
        proc.terminate()

if __name__ == "__main__":
    verify_throttle_hold()
