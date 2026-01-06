from pathlib import Path
import json
import datetime
from typing import List, Optional, Dict
from config import SEAT_AVAILABILITY
from bearer_token import get_bearer_token
from playwright.sync_api import sync_playwright


def _find_showtimes_file(site_id: str, date: str) -> Optional[Path]:
    data_root = Path(__file__).parent / "data"
    pattern = f"showtimes_{site_id}_{date}.json"
    for p in data_root.rglob(pattern):
        return p
    return None


def get_show_ids_from_existing(site_id: str, date: str) -> List[Dict]:
    """Return list of shows found in existing showtimes JSON for site and date.
    Each item: {'id': show_id, 'startsAt': startsAt}
    """
    p = _find_showtimes_file(site_id, date)
    if not p:
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        out = []
        for s in data.get("showtimes", []):
            sid = s.get("id") or s.get("showId") or s.get("show_id")
            starts = None
            sched = s.get("schedule")
            if sched:
                starts = sched.get("startsAt")
            if sid:
                out.append({"id": sid, "startsAt": starts})
        return out
    except Exception:
        return []


def _make_output_path_for_show(show_id: str, date: str) -> Path:
    # determine year/week from date
    try:
        dt = datetime.date.fromisoformat(date)
    except Exception:
        # try D.M.YYYY
        parts = date.split('.')
        if len(parts) == 3:
            d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
            dt = datetime.date(y, m, d)
        else:
            dt = datetime.date.today()
    year, week, _ = dt.isocalendar()
    data_dir = Path(__file__).parent / "data" / str(year) / f"week_{week:02d}" / "seat_availability"
    data_dir.mkdir(parents=True, exist_ok=True)
    # include time of scraping in filename (HHMMSS)
    ts = datetime.datetime.now().strftime("%H%M%S")
    return data_dir / f"seat_availability_{show_id}_{ts}.json"


def fetch_seat_availability_playwright(token: str, show_id: str, date: str) -> Optional[Path]:
    url = SEAT_AVAILABILITY.format(show_id=show_id)
    out_path = _make_output_path_for_show(show_id, date)

    headers = {"Authorization": f"{token}", "Accept": "application/json"}

    with sync_playwright() as p:
        req_ctx = p.request.new_context(extra_http_headers={"User-Agent": "Mozilla/5.0", **headers})
        try:
            resp = req_ctx.get(url, timeout=30000)
        except Exception as e:
            req_ctx.dispose()
            print(f"Playwright request error for seat availability {show_id}: {e}")
            return None

        try:
            text = resp.text()
            try:
                data = json.loads(text)
                out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                out_path.write_text(text, encoding="utf-8")
            print(f"Saved seat availability to {out_path}")
            return out_path
        finally:
            req_ctx.dispose()


def ensure_showtimes_and_get_show_ids(site_id: str, date: str) -> List[Dict]:
    """Ensure showtimes JSON exists for site/date. If missing and `entry` provided, try to fetch it using showtime scraper.
    Returns list of show dicts.
    """
    shows = get_show_ids_from_existing(site_id, date)
    if shows:
        return shows

    # import here to avoid circular imports
    from showtime_scraper import get_theater_showtimes_by_date

    token = get_bearer_token()

    get_theater_showtimes_by_date(token, date=date)
    # after fetching, try again
    return get_show_ids_from_existing(site_id, date)


if __name__ == "__main__":
    import argparse
    from showtime_scraper import get_theater_showtimes_by_date

    parser = argparse.ArgumentParser(description="Fetch seat availability for shows on a given site and date")
    parser.add_argument("site_id")
    parser.add_argument("date")
    args = parser.parse_args()

    token = get_bearer_token()

    shows = ensure_showtimes_and_get_show_ids(args.site_id, args.date)
    if not shows:
        print("No shows found for site/date")
        raise SystemExit(1)

    for s in shows:
        fetch_seat_availability_playwright(token, s["id"], args.date)
