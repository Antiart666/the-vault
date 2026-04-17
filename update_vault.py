import os
import shutil
from datetime import datetime

# --- KONFIGURATION ---
LIBRARY_DIR = "library"
INDEX_FILE = "index.html"
BACKUP_DIR = "backups"
CSV_FILE = "Filmlista - Blad1.csv"

KATEGORIER = {
    "articles": "Artiklar",
    "clips": "Pressklipp",
    "esseys": "Uppsats",
    "film-history": "Filmhistoria",
    "interviews": "Intervjuer",
    "reviews": "Recensioner"
}

def create_backup():
    """Räddar din data innan uppdatering börjar."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    if os.path.exists(CSV_FILE):
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
        shutil.copy2(CSV_FILE, os.path.join(BACKUP_DIR, f"backup_filmlista_{ts}.csv"))
        print(f"✅ Backup skapad.")

def generera_meny_html():
    """Skannar mappar och skapar listor med länkar."""
    print("🔍 Skannar mappar efter nya texter...")
    html_data = {}
    for mapp_id in KATEGORIER.keys():
        path = os.path.join(LIBRARY_DIR, mapp_id)
        lankar = []
        if os.path.exists(path):
            filer = sorted([f for f in os.listdir(path) if f.lower().endswith((".txt", ".html"))])
            for f in filer:
                namn = f.replace(".txt", "").replace(".html", "").replace("-", " ").title()
                lankar.append(f'            <li><a href="{LIBRARY_DIR}/{mapp_id}/{f}">{namn}</a></li>')
        html_data[mapp_id] = "\n".join(lankar)
    return html_data

def uppdatera_index(data):
    """Skriver in länkarna i index.html automatiskt med skottsäker logik."""
    if not os.path.exists(INDEX_FILE):
        print(f"❌ Fel: Hittade inte {INDEX_FILE}!")
        return
        
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        innehall = f.read()

    for mapp_id, html_lankar in data.items():
        start_tag = f"<!-- START_{mapp_id.upper()} -->"
        end_tag = f"<!-- END_{mapp_id.upper()} -->"
        
        if start_tag in innehall and end_tag in innehall:
            # Skär ut allt FÖRE start-taggen
            del1 = innehall.split(start_tag)
            # Skär ut allt EFTER slut-taggen
            del2 = innehall.split(end_tag)[-1]
            # Pussla ihop filen igen med det nya innehållet i mitten
            innehall = f"{del1}{start_tag}\n{html_lankar}\n{end_tag}{del2}"
            print(f"✅ Uppdaterade: {KATEGORIER[mapp_id]}")
        else:
            print(f"⚠️ Varning: Hittade inte taggar för {mapp_id}")

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(innehall)

if __name__ == "__main__":
    print(f"🚀 Startar MASTER-UPPDATERING...")
    create_backup()
    meny_data = generera_meny_html()
    uppdatera_index(meny_data)
    print("\n✨ ALLT KLART! Kontrollera index.html och gör sedan en PUSH.")