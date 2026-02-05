import pytest
from playwright.sync_api import Page, expect
import subprocess
import time
import sys
import os

APP_URL = "http://127.0.0.1:5001"

@pytest.fixture(scope="module", autouse=True)
def run_app():
    print("Starting Flask App (Unbuffered)...")
    # Use -u for unbuffered output so we can see logs immediately
    # Redirect stdout/stderr to files for inspection if needed, or inherit
    # Inherit allows pytest -s to show it.
    
    # Let's write to a log file we can read later
    with open("server_stdout.log", "w") as out, open("server_stderr.log", "w") as err:
        p = subprocess.Popen(
            [sys.executable, "-u", "app.py"],
            cwd=os.getcwd(),
            stdout=out,
            stderr=err
        )
        time.sleep(5) # Wait for start
        yield
        print("Terminating Flask App...")
        p.terminate()

def test_thrust_control(page: Page):
    # Capture console logs
    page.on("console", lambda msg: print(f"BROWSER: {msg.text}"))
    
    # 1. Navigate to App
    page.goto(APP_URL)
    
    # 2. Wait for connection
    expect(page.locator("#status-text")).to_have_text("Online", timeout=10000)
    
    # 3. Check Initial Altitude (should be near 0)
    z_elem = page.locator("#val-z")
    initial_z = float(z_elem.inner_text())
    print(f"Initial Z: {initial_z}")
    
    # 5. Apply Thrust via UI Button (Simulate User)
    print("Clicking Takeoff Button...")
    page.click("#btn-takeoff")
    page.wait_for_timeout(500)
    
    # Verify Throttle HUD updated
    thr_elem = page.locator("#val-thr")
    thr_val = float(thr_elem.inner_text())
    print(f"Throttle HUD: {thr_val}%")
    assert thr_val >= 40, f"Throttle did not update! Value: {thr_val}"
    
    # Wait for physical response
    page.wait_for_timeout(3000)
    
    # 6. Check Altitude Change
    final_z = float(z_elem.inner_text())
    print(f"Final Z: {final_z}")
    
    assert final_z > 0.1, f"Drone did not take off! Final Z: {final_z}"
