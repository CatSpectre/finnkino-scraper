from bearer_token import get_bearer_token
from showtime_scraper import get_theater_showtimes_by_date
import json
from pathlib import Path
from typing import Optional


def fetch_showtimes_for_key(site_key: str, date: Optional[str] = None, token: Optional[str] = None, keys_path: Optional[str] = None):
    """Fetch showtimes for a single cinema `site_key` and `date`.

    If `token` is not provided, a bearer token will be obtained.
    """
    p = Path(keys_path) if keys_path else Path(__file__).parent / "data" / "vistacinema_list.json"
    keys = json.loads(p.read_text(encoding="utf-8"))
    entry = next((e for e in keys if e.get("key") == site_key), None)
    if not entry:
        raise ValueError(f"No entry with key {site_key}")

    if token is None:
        token = get_bearer_token()

    return get_theater_showtimes_by_date(token, entry, date=date)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch showtimes for a single cinema key")
    parser.add_argument("site_key", help="Cinema site key (e.g. '1004')")
    parser.add_argument("--date", default=None, help="Date (YYYY-MM-DD). Defaults to today.")
    parser.add_argument("--token", default=None, help="Optional bearer token to reuse")
    args = parser.parse_args()

    fetch_showtimes_for_key(args.site_key, date=args.date, token=(args.token or None))
