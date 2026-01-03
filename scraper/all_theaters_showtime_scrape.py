from bearer_token import get_bearer_token
from showtime_scraper import get_theater_showtimes_by_date
import json
from pathlib import Path


def load_keys(path: str | None = None):
    p = Path(path) if path else Path(__file__).parent / "data" / "vistacinema_list.json"
    return json.loads(p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    token = get_bearer_token()
    keys = load_keys()
    for entry in keys:
        token = get_theater_showtimes_by_date(token, entry)
