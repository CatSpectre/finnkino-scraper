import json
import argparse
import sys
from datetime import datetime
from pathlib import Path


def load_json_input(path: str | None):
    if path:
        p = Path(path)
        return json.loads(p.read_text(encoding="utf-8"))
    data = sys.stdin.read()
    return json.loads(data)

def parse_finnkino_schedule(data):
    """Parse the Finnkino showtime JSON data into a structured schedule."""
    films_map = {f['id']: f for f in data['relatedData']['films']}
    screens_map = {s['id']: s for s in data['relatedData']['screens']}
    attrs_map = {a['id']: a for a in data['relatedData']['attributes']}

    parsed_schedule = []

    for show in data['showtimes']:
        film_id = show['filmId']
        screen_id = show['screenId']
        start_time_iso = show['schedule']['startsAt'] # '2026-01-02T12:00:00+02:00'
        
        film_details = films_map.get(film_id, {})
        screen_details = screens_map.get(screen_id, {})
        
        # Clean up time (2026-01-02T12:00:00+02:00 -> 12:00)
        dt_object = datetime.fromisoformat(start_time_iso)
        time_str = dt_object.strftime("%H:%M")
        

        attributes = [attrs_map.get(attr_id, {}).get('name', {}).get('text') 
                      for attr_id in show.get('attributeIds', [])]
        attributes = [a for a in attributes if a]

        movie_entry = {
            "time": time_str,
            "title": film_details.get('title', {}).get('text', "Unknown Title"),
            "duration": f"{film_details.get('runtimeInMinutes')} min",
            "screen": screen_details.get('name', {}).get('text'),
            "attributes": ", ".join(attributes)
        }
        
        parsed_schedule.append(movie_entry)

    parsed_schedule.sort(key=lambda x: x['time'])

    return parsed_schedule

def main():
    parser = argparse.ArgumentParser(description="Parse Finnkino schedule JSON from file or stdin")
    parser.add_argument("--input", "-i", help="Path to showtimes JSON file (optional). If omitted, reads stdin.")
    args = parser.parse_args()

    json_data = load_json_input(args.input)
    schedule = parse_finnkino_schedule(json_data)

    print(f"{'TIME':<8} | {'SCREEN':<8} | {'TITLE'}")
    print("-" * 50)
    for movie in schedule:
        print(f"{movie['time']:<8} | {movie['screen']:<8} | {movie['title']}")


if __name__ == "__main__":
    main()