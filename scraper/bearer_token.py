from playwright.sync_api import sync_playwright
import time

url = "https://www.finnkino.fi"
keyword_url = "digital-api.finnkino.fi"

def get_bearer_token():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            with page.expect_response(lambda response: keyword_url in response.url, timeout=60000) as response_info:
                page.goto(url)

            response = response_info.value
            token = response.request.headers.get('authorization')
            # print("\n" + "="*30)
            print("SUCCESS! Token captured")
            print(token)
            # print("="*30 + "\n")

        except Exception as e:
            print(f"Error: {e}")
            # Keep window open for debugging
            time.sleep(10)

        browser.close()
        return token
