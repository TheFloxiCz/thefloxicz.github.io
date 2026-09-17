import json
import datetime
import os
import re
import glob

# === KONFIGURACE ===
INPUT_DIR = "/home/josef/Documents/Data_skripty/API_BBS_Responses/Cena_map"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
MAPS_DIR = os.path.join(REPO_DIR, "data", "maps")
INDEX_FILE = os.path.join(REPO_DIR, "data", "index.json")
# ===================


def map_id_from_name(name: str) -> str:
    name = name.lower()
    name = name.replace(" ", "_")
    name = re.sub(r"[^a-z0-9_]", "", name)
    return name


def parse_date_from_filename(filename: str) -> datetime.date | None:
    """Extrahuje datum z názvu souboru Cena_map-DD_MM_YYYY.json"""
    match = re.search(r"(\d{2})_(\d{2})_(\d{4})", filename)
    if not match:
        return None
    day, month, year = match.groups()
    try:
        return datetime.date(int(year), int(month), int(day))
    except ValueError:
        return None


def main():
    pattern = os.path.join(INPUT_DIR, "Cena_map-*.json")
    files = glob.glob(pattern)

    if not files:
        print(f"CHYBA: Žádné soubory nenalezeny v {INPUT_DIR}")
        return

    # Seřaď soubory chronologicky
    files_with_dates = []
    for f in files:
        date = parse_date_from_filename(os.path.basename(f))
        if date:
            files_with_dates.append((date, f))
        else:
            print(f"PŘESKOČENO (nelze parsovat datum): {f}")

    files_with_dates.sort(key=lambda x: x[0])
    print(f"Nalezeno {len(files_with_dates)} souborů ke zpracování.")

    os.makedirs(MAPS_DIR, exist_ok=True)

    # Načti existující data map do paměti (rychlejší než číst každý soubor znovu)
    all_data = {}

    for date, filepath in files_with_dates:
        date_str = date.isoformat()

        with open(filepath, encoding="utf-8") as f:
            daily = json.load(f)

        for entry in daily:
            name = entry["name"]
            price = entry["price"]
            map_id = map_id_from_name(name)

            if map_id not in all_data:
                all_data[map_id] = {"name": name, "prices": []}

            # Nepřidávej duplicitní záznam pro stejný den
            existing_dates = {p[0] for p in all_data[map_id]["prices"]}
            if date_str not in existing_dates:
                all_data[map_id]["prices"].append([date_str, price])

        print(f"  Zpracován: {os.path.basename(filepath)} ({len(daily)} map)")

    # Ulož všechny soubory map
    print(f"\nUkládám {len(all_data)} souborů map...")
    index = {}

    for map_id, data in all_data.items():
        # Seřaď záznamy chronologicky pro jistotu
        data["prices"].sort(key=lambda x: x[0])

        path = os.path.join(MAPS_DIR, f"{map_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, separators=(",", ":"), ensure_ascii=False)

        # Aktuální cena = poslední záznam
        index[map_id] = {"name": data["name"], "current": data["prices"][-1][1]}

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, separators=(",", ":"), ensure_ascii=False)

    print(f"Hotovo! {len(all_data)} map, {len(files_with_dates)} dní zpracováno.")


if __name__ == "__main__":
    main()
