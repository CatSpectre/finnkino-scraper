import argparse
import json
from pathlib import Path


def load_theaters(path: str | None = None):
    p = Path(path) if path else Path(__file__).parent / "data" / "theaters.json"
    return json.loads(p.read_text(encoding="utf-8"))


def extract_vistacinema_list(theaters: list) -> list:
    out = []
    for t in theaters:
        vc = t.get("vistaCinema")
        if vc and vc.get("key"):
            out.append({
                "key": vc.get("key"),
                "name": t.get("name"),
                "urlSegment": t.get("urlSegment"),
            })
    return out


def main():
    parser = argparse.ArgumentParser(description="Extract vistaCinema keys and theater names")
    parser.add_argument("--input", "-i", help="Path to theaters.json (optional)")
    parser.add_argument("--output", "-o", help="Output JSON file path (optional)")
    args = parser.parse_args()

    theaters = load_theaters(args.input)
    lst = extract_vistacinema_list(theaters)

    default_out = Path(__file__).parent / "data" / "vistacinema_list.json"
    outp = Path(args.output) if args.output else default_out
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(lst, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(lst)} entries to {outp}")


if __name__ == "__main__":
    main()
