from pathlib import Path
import csv

root = Path("players")
files = sorted(root.rglob("*.csv"))

print(f"PLAYER CSV FILES: {len(files)}")
print()

for path in files:
    with path.open(
        encoding="utf-8-sig",
        newline="",
    ) as f:
        reader = csv.reader(f)
        header = next(reader, [])
        first = next(reader, [])

    print("=" * 90)
    print(path)
    print("COLUMNS:", len(header))
    print("HEADER:", header)
    print("FIRST ROW:", first)
    print()
