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
        # 1. Use a standard window size and common args to look less like a bot
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            user_agent=DEFAULT_USER_AGENT,
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        token = None
        
        try:
            # 2. Use a custom predicate to capture the token from ANY request 
            # (sometimes it's in a GET request, not just a 'response')
            def request_handler(request):
                nonlocal token
                auth = request.headers.get('authorization')
                if auth and DIGITAL_API_HOST in request.url:
                    token = auth

            page.on("request", request_handler)

            # 3. Go to the URL and wait until the network is idle
            # This is usually more reliable than expect_response for background APIs
            page.goto(BASE_URL, wait_until="networkidle", timeout=60000)

            # 4. Optional: Small sleep to allow async JS to fire after idle
            if not token:
                time.sleep(5)

            if token:
                print("SUCCESS! Token captured")
            else:
                print("Failed to capture token: No request with Authorization header found.")

        except Exception as e:
            print(f"Error capturing token: {e}")
            page.screenshot(path="debug.png")
        finally:
            browser.close()

        return token


def get_bearer_token(force_refresh: bool = False) -> str:
    """Return a valid bearer token. If a cached token exists and is valid it is returned.
    Otherwise a new token is fetched via Playwright and cached.
    Set `force_refresh=True` to always fetch a fresh token.
    """
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

    # If fails to fetch but has a cached token, return it
    cached = _load_token()
    if cached:
        return cached

    raise RuntimeError("Unable to obtain bearer token")
