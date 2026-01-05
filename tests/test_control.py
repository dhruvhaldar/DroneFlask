import pytest
from playwright.sync_api import Page, expect
import subprocess
import time
import sys
import os

APP_URL = "http://127.0.0.1:5001"

@pytest.fixture(scope="module", autouse=True)
def run_app():
    # Start the Flask app
    # Only if not already running? 
    # To be safe for repro, let's assume we use the one running or start one.
    # User has app running. Let's try to connect first.
    
    # Actually, for robust testing, we should kill existing and start fresh,
    # or just rely on the one running if we want to confirm user state.
    # Given the complexity of "killing existing", let's assume APP IS RUNNING at 5001 as per previous steps.
    # If we need to start it, we can uncomment below.
    
    # p = subprocess.Popen([sys.executable, "app.py"], cwd="E:\\Misc\\DroneFlask")
    # time.sleep(5) # Wait for start
    yield
    # p.terminate()

def test_thrust_control(page: Page):
    # Capture console logs
    page.on("console", lambda msg: print(f"BROWSER: {msg.text}"))
    
    # 1. Navigate to App
    page.goto(APP_URL)
    
    # 2. Wait for connection
    expect(page.locator("#status-text")).to_have_text("Online", timeout=10000)
    
    # 3. Check Initial Altitude (should be near 0)
    # The HUD updates rapidly. We get text content.
    z_elem = page.locator("#val-z")
    initial_z = float(z_elem.inner_text())
    print(f"Initial Z: {initial_z}")
    
    # 4. Apply Thrust (Press 'W')
    # We hold it for a while to generate enough force to lift off
    print("Applying Thrust (Holding W)...")
    for _ in range(50): # 50 * 50ms = 2.5s ?? Keydown events need to be consistent
        page.keyboard.press("w")
        page.wait_for_timeout(50) # Manual repeat
        
    # Better: trigger keydown and hold?
    # page.keyboard.down("w")
    # page.wait_for_timeout(2000)
    # page.keyboard.up("w")
    
    # Let's try continuous key presses as the JS handler increments throttle on 'w' keydown
    # JS: if (keys.w) throttle += 0.05; (in updateCmd)
    # updateCmd is called on 'keydown'. 
    # Yes, so repeated keydown is needed, OR holding 'w' if OS repeats. 
    # Playwright `down` might not trigger repeated events unless we implement it.
    # The JS `window.addEventListener("keydown", ...)` is standard.
    # If we `down('w')`, we fire one event. 
    # We need to FIRE multiple keydowns to increase throttle if the logic relies on repeated events.
    # Logic in index.html: 
    # window.addEventListener("keydown", (e) => { keys[e.key] = 1; updateCmd(); });
    # if (keys.w) throttle += 0.05;
    
    # It seems `updateCmd` is called on every keydown.
    # So we need MULTIPLE presses to ramp up throttle.
    
    
    # Reset Sim
    print("Resetting Sim...")
    page.click("#btn-reset")
    page.wait_for_timeout(1000)
    
    # Check On-Screen Key Interaction (Tap 'W' once)
    print("Clicking On-Screen 'W' Key...")
    page.locator("#key-w").click()
    page.wait_for_timeout(100)
    
    # Throttle should be 0.02 -> 2% (rounding might make it 2)
    thr_elem = page.locator("#val-thr")
    expect(thr_elem).to_have_text("2") 
    print("On-Screen Key W works (Throttle increased)")
    
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
    # 5. Check Altitude Change
    # If throttle works, Z should increase (negative in NED? HUD shows -z)
    # HUD: (-s.z).toFixed(2). So positive HUD = Altitude.
    
    final_z = float(z_elem.inner_text())
    print(f"Final Z: {final_z}")
    
    # Assert
    # 6. Check Altitude Change
    # Z should increase 
    final_z = float(z_elem.inner_text())
    print(f"Final Z: {final_z}")
    
    assert final_z > 0.1, f"Drone did not take off! Final Z: {final_z}"

    # 7. Check Roll Control
    print("Clicking Right Arrow (Roll)...")
    # Simulate holding right arrow or clicking the button if mapped
    # We mapped 'key-right' in index.html to 'ArrowRight' in keys object.
    
    # We need to HOLD it to see effect? logic: if(keys.ArrowRight) r = rollMax; 
    # It sets a Target Roll. So one click (mousedown) sets keys=1. 
    # But mouseup sets keys=0.
    # So we need to mouse down and hold?
    # Playwright click() is press+release.
    # So Pulse command. 
    # If we pulse, r goes to 0.5 then back to 0.
    # The drone should twitch.
    
    # Let's drag? or down/wait/up.
    page.locator("#key-right").dispatch_event("mousedown") 
    page.wait_for_timeout(1000)
    
    # Check HUD for Roll mismatch
    phi_elem = page.locator("#val-phi")
    phi_val = float(phi_elem.inner_text())
    print(f"Phi (Roll) during hold: {phi_val}")
    
    page.locator("#key-right").dispatch_event("mouseup")
    
    assert abs(phi_val) > 0.01, f"Drone did not roll! Phi: {phi_val}"
