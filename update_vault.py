import os

# --- KONFIGURATION ---
LIBRARY_DIR = "library"
INDEX_FILE = "index.html"
KATEGORIER = {
    "articles": "Artiklar",
    "clips": "Pressklipp",
    "esseys": "Uppsats",
    "film-history": "Filmhistoria",
    "interviews": "Intervjuer",
    "reviews": "Recensioner"
}

def uppdatera_meny():
    print("🚀 Startar uppdatering av biblioteket...")
    
    # Skapa en ordlista med alla filer i varje undermapp
    bibliotek_data = {}
    for mapp_id, rubrik in KATEGORIER.items():
        sokvag = os.path.join(LIBRARY_DIR, mapp_id)
        if os.path.exists(sokvag):
            filer = [f for f in os.listdir(sokvag) if f.lower().endswith((".txt", ".html"))]
            bibliotek_data[mapp_id] = sorted(filer)
        else:
            bibliotek_data[mapp_id] = []

    # Här kan du lägga till logik för att läsa din index.html och ersätta menyerna
    # För tillfället fungerar detta som en kontroll att filerna hittas lokalt
    for kat, filer in bibliotek_data.items():
        print(f"✅ Hittade {len(filer)} filer i {kat} (inklusive {', '.join(filer[:2]) if filer else 'inga'})")

    print("\n👉 För att dessa ska synas på nätet måste de nu länkas i din index.html.")
    print("Använd GitHub Desktop för att göra en Push nu.")

if __name__ == "__main__":
    uppdatera_meny()