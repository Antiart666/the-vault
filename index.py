import streamlit as st
import pandas as pd
import os
import requests

# --- 1. KONFIGURATION OCH SÖKVÄG ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = 'Filmlista - Blad1.csv'
FULL_PATH = os.path.join(CURRENT_DIR, FILE_NAME)
# Vi använder 'library' som huvudmapp för allt arkivmaterial
LIBRARY_DIR = os.path.join(CURRENT_DIR, 'library')

# Skapa mappar om de saknas
if not os.path.exists(LIBRARY_DIR):
    os.makedirs(LIBRARY_DIR)

st.set_page_config(page_title="The Vault of Antichrister", layout="wide")

# --- 2. FUNKTIONER ---
def get_movie_poster(title, year):
    # (Behåll din befintliga poster-kod här om du har en fungerande API-nyckel)
    return None

# --- 3. DESIGN (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    h1 { color: #e50914 !important; }
    .movie-card { background-color: #1e2129; padding: 20px; border-radius: 10px; border-left: 5px solid #e50914; }
    .stSelectbox label { color: #e50914 !important; font-weight: bold; }
    .library-box { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-top: 20px; white-space: pre-wrap; font-family: sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HUVUDINNEHÅLL (DATABASEN) ---
if os.path.exists(FULL_PATH):
    df = pd.read_csv(FULL_PATH)
    
    st.title("🎬 THE VAULT OF ANTICHRISTER")
    
    # Sökfunktion för filmer
    search_query = st.text_input("Sök i filmdatabasen (Titel, Regi, Genre...):")
    if search_query:
        df = df[df.apply(lambda row: search_query.lower() in row.astype(str).str.lower().values, axis=1)]

    # Visa tabell eller vald film
    if not df.empty:
        selected_title = st.selectbox("Välj en film för detaljer:", ["-- Välj film --"] + df['Titel'].tolist())
        
        if selected_title != "-- Välj film --":
            m = df[df['Titel'] == selected_title].iloc[0]
            st.markdown(f"<h1>{str(m['Titel']).upper()}</h1>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.info("Poster-service aktiv")
            with col2:
                st.markdown(f"""
                    <div class="movie-card">
                        <p><strong>📅 År:</strong> {m.get('År', '-')}</p>
                        <p><strong>🎥 Regi:</strong> {m.get('Regi', '-')}</p>
                        <p><strong>🎭 Genre:</strong> {m.get('Genre', '-')}</p>
                        <p><strong>⏳ Tid:</strong> {m.get('Längd', '-')} </p>
                        <p><strong>💿 Disk:</strong> {m.get('Disk 1', '-')} / {m.get('Disk 2', '-')}</p>
                    </div>
                """, unsafe_allow_html=True)

# --- 5. DET NYA BIBLIOTEKET (AUTOMATISK SKANNING AV UNDERMAPPAR) ---
st.write("---")
st.header("📖 ARKIVET")
st.write("Välj kategori och dokument nedan.")

if os.path.exists(LIBRARY_DIR):
    # Denna del letar nu i ALLA mappar inuti library
    all_files = []
    for root, dirs, files in os.walk(LIBRARY_DIR):
        for file in files:
            if file.endswith(('.html', '.txt', '.md')):
                # Skapar en snygg sökväg (t.ex. 'interviews/bruce-campbell.txt')
                rel_path = os.path.relpath(os.path.join(root, file), LIBRARY_DIR)
                all_files.append(rel_path)
    
    if all_files:
        all_files.sort() # Sorterar så att mappar kommer i ordning
        
        # Funktion för att göra filnamnen snygga i listan
        def format_file_names(path):
            clean_name = path.replace('.txt', '').replace('.html', '').replace('.md', '')
            clean_name = clean_name.replace('\\', ' / ').replace('/', ' / ') # Fixar snedstreck
            return clean_name.replace('-', ' ').title()

        selected_file = st.selectbox("Välj ett dokument ur arkivet:", 
                                     options=all_files, 
                                     format_func=format_file_names)
        
        if selected_file:
            file_path = os.path.join(LIBRARY_DIR, selected_file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                st.markdown('<div class="library-box">', unsafe_allow_html=True)
                if selected_file.endswith(".html"):
                    st.markdown(content, unsafe_allow_html=True)
                else:
                    # För .txt-filer bevarar vi radbrytningar snyggt
                    st.markdown(content)
                st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Kunde inte läsa filen: {e}")
    else:
        st.write("Arkivet är tomt. Lägg till mappar och .txt-filer i '/library' för att se dem här.")
else:
    st.error("Mappen 'library' saknas.")  