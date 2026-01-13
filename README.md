# Finnkino Scraper

Scraper for Finnkino cinema data. Still working on it!

## Summary
- Currently focused on scraping weekly showtimes.
- Contains utilities to scrape seat availability, film metadata and cinema lists.

## Key scripts
- [scraper/weekly_showtime_scrape.py](scraper/weekly_showtime_scrape.py): main weekly showtime scraper.
- [scraper/seat_availability_scraper.py](scraper/seat_availability_scraper.py): seat availability scraper.
- [scraper/get_cinema_list.py](scraper/get_cinema_list.py): fetch cinema listings.

## Quickstart
1. Install Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Install Playwright browsers:

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
```

3. Run the weekly scraper locally:

```bash
python3 scraper/weekly_showtime_scrape.py
```

## Notes
- This project is WIP
