
import os
import json
from playwright.sync_api import sync_playwright
from config import THEATERS_LIST, DEFAULT_USER_AGENT

def theater_data_scrape():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    out_path = os.path.join(data_dir, "theaters.json")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )

        context = browser.new_context(
            user_agent=DEFAULT_USER_AGENT,
        )
        page = context.new_page()

        try:
            response = page.goto(THEATERS_LIST, timeout=60000)
            if response is None:
                raise RuntimeError(f"No response received from {THEATERS_LIST}")
            text = response.text()
            try:
                data = json.loads(text)
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"Saved theaters JSON to {out_path}")
            except Exception:
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"Saved raw response to {out_path}")

        except Exception as e:
            print(f"Playwright error: {e}")

        finally:
            browser.close()


if __name__ == "__main__":
    theater_data_scrape()
    