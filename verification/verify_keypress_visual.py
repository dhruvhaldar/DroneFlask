import time
import sys
from playwright.sync_api import sync_playwright

def verify_visual_feedback():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("http://localhost:5001", timeout=5000)
        except:
            print("Could not connect to app. Is it running?")
            sys.exit(1)

        # 1. Takeoff (T)
        print("Testing Takeoff (T)...")
        # Inject a script to record if the class was added.
        page.evaluate("""
            window.wasPressed = false;
            const btn = document.getElementById('btn-takeoff');
            if(btn) {
                const observer = new MutationObserver(() => {
                    if (btn.classList.contains('scale-95')) {
                        window.wasPressed = true;
                    }
                });
                observer.observe(btn, { attributes: true, attributeFilter: ['class'] });
            }
        """)

        page.keyboard.press("t")
        time.sleep(0.5)

        was_pressed = page.evaluate("window.wasPressed")
        if was_pressed:
            print("SUCCESS: Takeoff button showed visual feedback.")
        else:
            print("FAILURE: Takeoff button did NOT show visual feedback.")
            # We expect failure initially

        browser.close()

if __name__ == "__main__":
    verify_visual_feedback()
