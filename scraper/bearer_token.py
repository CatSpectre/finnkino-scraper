from playwright.sync_api import sync_playwright
from config import BASE_URL, DIGITAL_API_HOST, DEFAULT_USER_AGENT
from pathlib import Path
import json
import time
from base64 import urlsafe_b64decode


TOKEN_FILE = Path(__file__).parent / "data" / "bearer_token.json"


def _ensure_data_dir():
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)


def _decode_jwt_payload(token: str) -> dict:
    try:
        parts = token.split('.')
        if len(parts) < 2:
            return {}
        payload_b64 = parts[1]
        padding = '=' * (-len(payload_b64) % 4)
        payload_bytes = urlsafe_b64decode(payload_b64 + padding)
        return json.loads(payload_bytes.decode())
    except Exception:
        return {}


def _token_valid(token: str) -> bool:
    try:
        payload = _decode_jwt_payload(token)
        exp = payload.get('exp')
        if exp is None:
            return False
        # print(f"Token expires at {int(exp)}, current time is {time.time()}")
        return time.time() < int(exp)
    except Exception:
        return False


def _save_token(token: str):
    _ensure_data_dir()
    TOKEN_FILE.write_text(json.dumps({"token": token}), encoding="utf-8")


def _load_token() -> str | None:
    try:
        if not TOKEN_FILE.exists():
            return None
        data = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
        return data.get("token")
    except Exception:
        return None


def _fetch_token_via_playwright() -> str | None:
    with sync_playwright() as p:
        # 1. Launch with flags to disable automation features in Chrome
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox", 
                "--disable-setuid-sandbox"
            ]
        )
        
        # 2. Use a high-resolution viewport and standard User Agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        # 3. MANUAL STEALTH: Inject JavaScript to hide the 'navigator.webdriver' flag
        # This acts exactly like playwright-stealth but without the import errors
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        token = None
        try:
            # Monitor requests
            def request_handler(request):
                nonlocal token
                auth = request.headers.get('authorization')
                if auth and DIGITAL_API_HOST in request.url:
                    token = auth

            page.on("request", request_handler)

            print(f"Navigating to {BASE_URL}...")
            # increased timeout to 90s for slower CI runners
            page.goto(BASE_URL, wait_until="networkidle", timeout=90000)
            
            # 4. Human-like behavior: Move mouse slightly to prove we aren't a script
            page.mouse.move(100, 200)
            page.mouse.down()
            page.mouse.up()
            
            # Wait a moment for any lazy-loaded APIs
            time.sleep(5)

            if token:
                print("SUCCESS! Token captured")
            else:
                print("Failed to capture token. Taking screenshot...")
                page.screenshot(path="debug_final.png")

        except Exception as e:
            print(f"Error capturing token: {e}")
            try:
                page.screenshot(path="debug_error.png")
            except:
                pass
        finally:
            browser.close()

        return token

def get_bearer_token(force_refresh: bool = False) -> str:
    # ... [Keep your existing get_bearer_token logic] ...
    # Copy/paste the rest of your original function here
    if not force_refresh:
        token = _load_token()
        if token and _token_valid(token):
            return token

    token = _fetch_token_via_playwright()
    if token:
        try:
            _save_token(token)
        except Exception:
            pass
        return token

    cached = _load_token()
    if cached:
        return cached

    raise RuntimeError("Unable to obtain bearer token")
