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
        browser = p.chromium.launch(
            headless=True
        )
        
        context = browser.new_context(
            user_agent=DEFAULT_USER_AGENT
        )
        page = context.new_page()
        token = None
        try:
            with page.expect_response(lambda response: DIGITAL_API_HOST in response.url, timeout=60000) as response_info:
                page.goto(BASE_URL)

            response = response_info.value
            token = response.request.headers.get('authorization')
            print("SUCCESS! Token captured")
            # print(token)

        except Exception as e:
            print(f"Error capturing token: {e}")
        finally:
            try:
                browser.close()
            except Exception:
                pass

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
