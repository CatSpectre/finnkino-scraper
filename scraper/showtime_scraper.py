from bearer_token import get_bearer_token
import requests
import json
import time
from pathlib import Path
from config import THEATER_SHOWTIMES
import datetime


def get_theater_showtimes_by_date(token, entry, date: str | None = None, delay=0.5):
    """Fetch and save showtimes for a single cinema entry and date.
    """
    if date is None:
        date = datetime.date.today().isoformat()

    # parse date string to determine year and ISO week
    try:
        dt = datetime.date.fromisoformat(date)
    except Exception:
        try:
            parts = date.split('.')
            if len(parts) == 3:
                d = int(parts[0])
                m = int(parts[1])
                y = int(parts[2])
                dt = datetime.date(y, m, d)
            else:
                dt = datetime.date.today()
        except Exception:
            dt = datetime.date.today()

    iso_year, iso_week, _ = dt.isocalendar()
    data_dir = Path(__file__).parent / "data" / str(iso_year) / f"week_{iso_week:02d}"
    data_dir.mkdir(parents=True, exist_ok=True)

    headers = {
        "Authorization": f"{token}",
        "Content-Type": "application/json",
    }

    site_id = entry.get("key")
    if not site_id:
        return

    url = THEATER_SHOWTIMES.format(date=date, site_id=site_id)
    try:
        resp = requests.get(url, headers=headers, timeout=30)
    except Exception as e:
        print(f"Request error for {site_id}: {e}")
        return

    # If unauthorized, refresh token once and retry
    if resp.status_code == 401:
        print(f"401 Unauthorized for {site_id}, refreshing token and retrying")
        token = get_bearer_token(force_refresh=True)
        headers["Authorization"] = f"{token}"
        try:
            resp = requests.get(url, headers=headers, timeout=30)
        except Exception as e:
            print(f"Retry request error for {site_id}: {e}")
            return

    fname = f"showtimes_{site_id}_{date}.json"
    out_path = data_dir / fname

    try:
        data = resp.json()
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved showtimes to {out_path}")
    except Exception:
        print(f"Failed to parse JSON for {site_id}")

    time.sleep(delay)
    return
