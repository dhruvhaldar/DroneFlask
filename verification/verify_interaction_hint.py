from playwright.sync_api import sync_playwright
import time
import subprocess
import os
import signal
import sys

def verify_interaction_hint():
    env = os.environ.copy()
    process = subprocess.Popen(
        ["python", "-u", "app.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print("App process started. Waiting for server to come up...")
    start_time = time.time()
    started = False
    while time.time() - start_time < 20:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 5001))
        sock.close()
        if result == 0:
            print("Server is listening on 5001.")
            started = True
            break
        time.sleep(1)

    if not started:
        print("Server failed to start in 20s.")
        process.kill()
        sys.exit(1)

    try:
        with sync_playwright() as p:
            print("Launching browser...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print("Navigating to app...")
            page.goto("http://localhost:5001")

            print("Waiting for UI layer...")
            page.wait_for_selector("#ui-layer", timeout=10000)

            hint_selector = "#interaction-hint"
            page.wait_for_selector(hint_selector, timeout=5000)

            # Check initial class
            initial_class = page.locator(hint_selector).get_attribute("class")
            print(f"Initial class: {initial_class}")

            # 2. Verify Hint Disappears on Interaction
            print("Simulating interaction (dispatch event)...")

            # Use evaluate to dispatch directly to ensure it hits window
            page.evaluate("window.dispatchEvent(new MouseEvent('mousedown'))")

            print("Waiting for fade out (2s)...")
            time.sleep(2.0)

            hint_el = page.locator(hint_selector)
            if hint_el.count() > 0:
                classes = hint_el.get_attribute("class")
                print(f"Hint classes after interaction: {classes}")
                if "opacity-0" in classes:
                    print("✅ Hint has opacity-0 class.")
                else:
                    print("❌ Hint does not have opacity-0 class.")
                    # Let's inspect if the listener is even there? Hard to do from here.
                    sys.exit(1)
            else:
                 print("✅ Hint element removed from DOM.")

            browser.close()

    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    finally:
        print("Killing app process...")
        os.kill(process.pid, signal.SIGTERM)
        process.wait()
        print("Done.")

if __name__ == "__main__":
    verify_interaction_hint()
