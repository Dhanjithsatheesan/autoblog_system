import base64
import requests
import logging
from config import WP_API_ENDPOINT, WP_USERNAME, WP_PASSWORD, WP_CATEGORY_IDS, WP_TAG_IDS, POST_STATUS
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def publish_to_wordpress(title, content):
    """
    Publishes a blog post to WordPress using its REST API.
    Uses Playwright to solve InfinityFree's Javascript anti-bot challenge first.
    """
    logger.info(f"Connecting to WordPress at {WP_API_ENDPOINT} to post: '{title}'")
    
    # Construct the basic auth payload (spaces must be stripped)
    clean_password = WP_PASSWORD.replace(" ", "")
    credentials = f"{WP_USERNAME}:{clean_password}"
    token = base64.b64encode(credentials.encode()).decode('utf-8')
    headers = {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Forwarded-Proto': 'https'
    }
    
    # Construct the post payload
    payload = {
        'title': title,
        'content': content,
        'status': POST_STATUS,
    }
    
    if WP_CATEGORY_IDS:
        payload['categories'] = WP_CATEGORY_IDS
    if WP_TAG_IDS:
        payload['tags'] = WP_TAG_IDS
        
    try:
        logger.info("Initializing Headless Browser to bypass Anti-Bot protection...")
        with sync_playwright() as p:
            # We must use a standard browser to solve the 'aes.js' challenge
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=headers['User-Agent'], ignore_https_errors=True)
            page = context.new_page()
            
            # Navigate once to the endpoint to trigger and solve the challenge
            page.goto(WP_API_ENDPOINT, wait_until="commit")
            page.wait_for_timeout(4000) # Give it 4 seconds to solve the JS challenge and set cookie
            
            # Extract the solved cookies (specifically the __test cookie)
            cookies = context.cookies()
            cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            headers['Cookie'] = cookie_header
            browser.close()
            
        logger.info("Challenge Solved. Injecting cookies into WP REST API request...")
        
        # Now make the actual POST request using standard Python requests
        response = requests.post(
            f"{WP_API_ENDPOINT}/posts",
            headers=headers,
            json=payload,
            timeout=30,
            verify=False
        )
        
        if response.status_code in (200, 201):
            try:
                post_data = response.json()
                post_url = post_data.get('link', 'Unknown URL')
                logger.info(f"Successfully published post! URL: {post_url}")
                return True, post_url
            except ValueError:
                logger.error("Successfully connected but WordPress returned HTML instead of JSON.")
                logger.error(f"Response snippet: {response.text[:200]}")
                return False, "Invalid JSON from server."
        else:
            logger.error(f"Failed to publish to WordPress. Status Code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False, response.text
            
    except Exception as e:
        logger.error(f"Error while connecting to WordPress: {e}")
        return False, str(e)

if __name__ == "__main__":
    # Test connection
    publish_to_wordpress("Playwright API Connection Test", "<p>Hello from Autoblog bypass!</p>")
