from playwright.sync_api import sync_playwright

def test_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0")
        
        # Navigate to login page
        print("Navigating to login page...")
        page.goto("http://uma.infinityfreeapp.com/wp-login.php")
        page.wait_for_timeout(4000) # Wait for aes.js challenge
        
        # Fill login form
        print("Filling login form...")
        page.fill("#user_login", "admin")
        page.fill("#user_pass", "ZT4mCGkryYgFY9UE2eFdj1CY")
        page.click("#wp-submit")
        
        # Check if we landed on the dashboard
        page.wait_for_timeout(4000)
        current_url = page.url
        print(f"Landed on: {current_url}")
        
        if "wp-admin" in current_url:
            print("LOGIN SUCCESSFUL!")
        else:
            print("LOGIN FAILED. Could be an application password or wrong credentials.")
            
test_login()
