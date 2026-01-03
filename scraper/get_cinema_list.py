import json
from pathlib import Path
from config import CINEMAS_LIST
import urllib.error
import time
import ua_generator

from urllib.request import Request, urlopen

def get_page_content(url, head):
  req = Request(url, headers=head)
  return urlopen(req)

attempt = 0
data = None
while True:
  attempt += 1
  ua = ua_generator.generate()
  head = {
    'User-Agent': ua.text,
    'Accept': 'text/html',
  }
  try:
    print(f"Attempt {attempt}: fetching with User-Agent: {ua.text}")
    resp = get_page_content(CINEMAS_LIST, head)
    data = resp.read()
    break
  except urllib.error.HTTPError as e:
    if e.code == 403:
      print(f"Attempt {attempt} got 403 Forbidden — generating new User-Agent and retrying")
      time.sleep(1)
      continue
    else:
      raise
  except Exception as e:
    print(f"Attempt {attempt} encountered error: {e}; retrying")
    time.sleep(1)
    continue

out_path = Path(__file__).parent / "data" / "cinemas.json"
out_path.parent.mkdir(parents=True, exist_ok=True)

try:
  text = data.decode("utf-8")
  parsed = json.loads(text)
  out_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
  print(f"Success! Wrote cinemas JSON to {out_path}")
except Exception:
  try:
    out_path.write_bytes(data if isinstance(data, (bytes, bytearray)) else str(data).encode("utf-8"))
    print(f"Wrote raw response to {out_path}")
  except Exception as e:
    print(f"Failed to write response to {out_path}: {e}")
