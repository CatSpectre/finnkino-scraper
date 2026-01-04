from bearer_token import get_bearer_token
from showtime_scraper import get_theater_showtimes_by_date
import json
from pathlib import Path
from datetime import date, timedelta, datetime
import argparse


def load_keys(path: str | None = None):
    p = Path(path) if path else Path(__file__).parent / "data" / "cinemas.json"
    return json.loads(p.read_text(encoding="utf-8"))


def next_or_current_friday(from_date: date) -> date:
    # weekday: Monday=0 .. Sunday=6; Friday = 4
    days_ahead = (4 - from_date.weekday()) % 7
    return from_date + timedelta(days=days_ahead)


def daterange(start: date, days: int = 7):
    for n in range(days):
        yield start + timedelta(n)


def run_week(start_friday: date | None = None):
    if start_friday is None:
        start_friday = next_or_current_friday(date.today())

    keys = load_keys()
    token = get_bearer_token()

    for d in daterange(start_friday, 7):
        date_str = d.isoformat()
        print(f"Fetching showtimes for date {date_str}")
        for entry in keys:
            get_theater_showtimes_by_date(token, entry, date=date_str)


def main():
    parser = argparse.ArgumentParser(description="Fetch showtimes for a Friday->Thursday week for all cinemas")
    parser.add_argument("--start", help="Start Friday date (YYYY-MM-DD). Defaults to next or current Friday")
    args = parser.parse_args()

    start = None
    if args.start:
        try:
            start = datetime.fromisoformat(args.start).date()
        except Exception:
            raise SystemExit("Invalid --start date format. Use YYYY-MM-DD")

    run_week(start_friday=start)


if __name__ == "__main__":
    main()
