import subprocess
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# 🎯 Configuration: Add your cloud application URLs here
TARGET_APPS = [
    "https://your-first-app.streamlit.app/",
    "https://your-second-app.streamlit.app/",
    "https://your-database-demo.app/"
]

# Ping interval: 12 hours in seconds (12 * 60 * 60)
PING_INTERVAL_SECONDS = 43200 

def send_macos_notification(title, message):
    """Sends a native macOS system notification to the Notification Center"""
    applescript = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", applescript])

def ping_apps():
    print(f"\n--- 🚀 Starting Keep-Alive Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    success_count = 0
    with sync_playwright() as p:
        # Launch headless browser to simulate real user traffic
        browser = p.chromium.launch(headless=True)
        
        for app_url in TARGET_APPS:
            page = browser.new_page()
            try:
                print(f"🔗 Navigating to: {app_url}")
                # Wait until DOM content is loaded (handles heavy cold starts up to 90s)
                page.goto(app_url, wait_until="load", timeout=90000)
                
                # Allow WebSockets / initial DB queries to fully initialize
                time.sleep(10)
                
                success_count += 1
                print(f"✅ Successfully pinged! App Title: '{page.title()}'")
            except Exception as e:
                print(f"❌ Failed to wake up {app_url}. Error: {e}")
            finally:
                page.close()
                
        browser.close()
        
    # Trigger macOS Notification Center feedback
    if success_count == len(TARGET_APPS):
        send_macos_notification("Cloud Pacemaker", "All applications are awake and active! 🚀")
    else:
        send_macos_notification("Cloud Pacemaker", f"⚠️ Warning: Only {success_count} of {len(TARGET_APPS)} apps responded.")

    print("--- 💤 Session Finished. Sleeping for 12 hours... ---\n")

if __name__ == "__main__":
    while True:
        try:
            ping_apps()
        except Exception as main_error:
            print(f"🚨 Critical error in main loop: {main_error}")
            send_macos_notification("Cloud Pacemaker", "🚨 Script crashed in the main loop!")
        
        time.sleep(PING_INTERVAL_SECONDS)
