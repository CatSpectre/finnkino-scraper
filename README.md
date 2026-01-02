# Finnkino Scraper

## Playwright Browsers

After installing Python dependencies, Playwright requires browser binaries to be installed.

Run:

```bash
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium
python3 -m playwright install-deps  # optional: installs Linux system dependencies
```

This will download the Chromium browser Playwright uses and (on Linux) install helper packages.
