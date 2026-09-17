import json
import datetime
import os
import re

# === KONFIGURACE ===
INPUT_DIR = "/home/josef/Documents/Data_skripty/API_BBS_Responses/Cena_map"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
MAPS_DIR = os.path.join(REPO_DIR, "data", "maps")
INDEX_FILE = os.path.join(REPO_DIR, "data", "index.json")
# ===================


def map_id_from_name(name: str) -> str:
    """Převede název mapy na bezpečné ID pro název souboru."""
    name = name.lower()
    name = name.replace(" ", "_")
    name = re.sub(r"[^a-z0-9_]", "", name)
    return name


def main():
    today = datetime.date.today()
    date_str = today.isoformat()
    filename = f"Cena_map-{today.strftime('%d_%m_%Y')}.json"
    input_path = os.path.join(INPUT_DIR, filename)

    if not os.path.exists(input_path):
        print(f"CHYBA: Soubor nenalezen: {input_path}")
        return

    with open(input_path, encoding="utf-8") as f:
        daily = json.load(f)

    os.makedirs(MAPS_DIR, exist_ok=True)

    index = {}
    updated = 0
    created = 0

    for entry in daily:
        name = entry["name"]
        price = entry["price"]
        map_id = map_id_from_name(name)
        path = os.path.join(MAPS_DIR, f"{map_id}.json")

        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            # Nepřidávej duplicitní záznam pro stejný den
            if data["prices"] and data["prices"][-1][0] == date_str:
                print(f"PŘESKOČENO (již existuje): {name}")
                index[map_id] = {"name": name, "current": price}
                continue
            updated += 1
        else:
            data = {"name": name, "prices": []}
            created += 1

        data["prices"].append([date_str, price])

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, separators=(",", ":"), ensure_ascii=False)

        index[map_id] = {"name": name, "current": price}

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, separators=(",", ":"), ensure_ascii=False)

    print(f"Hotovo: {created} nových, {updated} aktualizovaných, celkem {len(daily)} map.")
    print(f"Datum: {date_str}")


if __name__ == "__main__":
    main()
