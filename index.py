import streamlit as st
import pandas as pd
import os
import requests

# --- 1. KONFIGURATION OCH SÖKVÄG ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = 'Filmlista - Blad1.csv'
FULL_PATH = os.path.join(CURRENT_DIR, FILE_NAME)
LIBRARY_DIR = os.path.join(CURRENT_DIR, 'library')

# Skapa library-mappen om den inte finns (för säkerhets skull)
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
    .library-box { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-top: 20px; }
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
                st.info("Poster-service aktiv") # Här kan din poster-funktion ligga
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

# --- 5. DET NYA BIBLIOTEKET (AUTOMATISK SKANNING) ---
st.write("---")
st.header("📖 ARKIVET: RECENSIONER & ARTIKLAR")
st.write("Här hittar du inskannat material från Violent Vision och andra källor.")

# Lista alla filer i library-mappen
if os.path.exists(LIBRARY_DIR):
    archive_files = [f for f in os.listdir(LIBRARY_DIR) if f.endswith(('.html', '.txt', '.md'))]
    
    if archive_files:
        # Skapa en snygg lista med filnamn (rensad från filändelser för utseendet)
        display_names = {f: f.replace('.html', '').replace('.txt', '').replace('-', ' ').title() for f in archive_files}
        
        selected_file = st.selectbox("Välj ett dokument att läsa ur arkivet:", 
                                     options=archive_files, 
                                     format_func=lambda x: display_names[x])
        
        if selected_file:
            with open(os.path.join(LIBRARY_DIR, selected_file), "r", encoding="utf-8") as f:
                content = f.read()
                
            st.markdown('<div class="library-box">', unsafe_allow_html=True)
            if selected_file.endswith(".html"):
                st.markdown(content, unsafe_allow_html=True)
            else:
                st.text(content)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.write("Arkivet är tomt för tillfället. Ladda upp filer till mappen '/library' för att se dem här.")
else:
    st.error("Mappen 'library' saknas i projektet.")
