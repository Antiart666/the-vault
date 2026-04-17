import os
import shutil
from datetime import datetime

# --- 1. KONFIGURATION ---
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
    """Skapar en tidstämplad backup av CSV-filen."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    if os.path.exists(CSV_FILE):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        backup_name = f"backup_filmlista_{timestamp}.csv"
        shutil.copy2(CSV_FILE, os.path.join(BACKUP_DIR, backup_name))
        print(f"✅ Backup skapad: {backup_name}")

def generera_html_lankar():
    """Skannar mappar och skapar HTML-kod för menyerna."""
    print("🔍 Skannar biblioteket efter nya texter...")
    alla_lankar = {}

    for mapp_id, rubrik in KATEGORIER.items():
        sokvag = os.path.join(LIBRARY_DIR, mapp_id)
        lankar = []
        if os.path.exists(sokvag):
            filer = sorted([f for f in os.listdir(sokvag) if f.lower().endswith((".txt", ".html"))])
            for fil in filer:
                visningsnamn = fil.replace(".txt", "").replace(".html", "").replace("-", " ").title()
                # Skapar själva länk-raden för HTML-menyn
                lankar.append(f'<li><a href="{LIBRARY_DIR}/{mapp_id}/{fil}">{visningsnamn}</a></li>')
        alla_lankar[mapp_id] = "\n".join(lankar)
    
    return alla_lankar

def uppdatera_index_html(lank_data):
    """Injicerar de nya länkarna i index.html mellan taggar."""
    if not os.path.exists(INDEX_FILE):
        print(f"❌ Fel: Hittade inte {INDEX_FILE}")
        return

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Denna del letar efter dina kategorier i HTML-filen och ersätter innehållet
    for mapp_id, html_lankar in lank_data.items():
        start_tag = f'<!-- START_{mapp_id.upper()} -->'
        end_tag = f'<!-- END_{mapp_id.upper()} -->'
        
        if start_tag in html_content and end_tag in html_content:
            pattern = html_content.split(start_tag) + start_tag + "\n" + html_lankar + "\n" + end_tag + html_content.split(end_tag)[1]
            html_content = pattern
            print(f"✅ Uppdaterade kategorin: {KATEGORIER[mapp_id]}")
        else:
            print(f"⚠️ Varning: Kunde inte hitta taggarna för {mapp_id} i index.html")

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    print(f"🚀 Startar 'The Vault' Master-uppdatering ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    create_backup() # Fas 1: Säkerhet [2, 3]
    data = generera_html_lankar() # Fas 2: Skanning [4, 5]
    uppdatera_index_html(data) # Fas 3: Bygge [6, 7]
    print("\n✨ ALLT KLART! Kontrollera index.html lokalt och gör sedan en PUSH i GitHub Desktop.")