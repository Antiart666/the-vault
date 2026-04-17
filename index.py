import streamlit as st
import pandas as pd
import os

# --- 1. KONFIGURATION OCH SÖKVÄG ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = 'Filmlista - Blad1.csv'
FULL_PATH = os.path.join(CURRENT_DIR, FILE_NAME)
LIBRARY_DIR = os.path.join(CURRENT_DIR, 'library')

# Skapa mappar om de saknas
if not os.path.exists(LIBRARY_DIR):
    os.makedirs(LIBRARY_DIR)

st.set_page_config(page_title="The Vault of Antichrister", layout="wide")

# --- 2. DESIGN (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    h1 { color: #e50914 !important; }
    .movie-card { background-color: #1e2129; padding: 20px; border-radius: 10px; border-left: 5px solid #e50914; }
    .stSelectbox label { color: #e50914 !important; font-weight: bold; }
    .library-box { background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-top: 20px; white-space: pre-wrap; font-family: sans-serif; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HUVUDINNEHÅLL (DATABASEN) ---
if os.path.exists(FULL_PATH):
    try:
        df = pd.read_csv(FULL_PATH)
        st.title("🎬 THE VAULT OF ANTICHRISTER")
        
        search_query = st.text_input("Sök i filmdatabasen (Titel, Regi, Genre...):")
        if search_query:
            df = df[df.apply(lambda row: search_query.lower() in row.astype(str).str.lower().values, axis=1)]

        if not df.empty:
            selected_title = st.selectbox("Välj en film för detaljer:", ["-- Välj film --"] + df['Titel'].tolist())
            if selected_title != "-- Välj film --":
                m = df[df['Titel'] == selected_title].iloc[0]
                st.markdown(f"<h1>{str(m['Titel']).upper()}</h1>", unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="movie-card">
                        <p><strong>📅 År:</strong> {m.get('År', '-')}</p>
                        <p><strong>🎥 Regi:</strong> {m.get('Regi', '-')}</p>
                        <p><strong>🎭 Genre:</strong> {m.get('Genre', '-')}</p>
                        <p><strong>⏳ Tid:</strong> {m.get('Längd', '-')} </p>
                        <p><strong>💿 Disk:</strong> {m.get('Disk 1', '-')} / {m.get('Disk 2', '-')}</p>
                    </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Kunde inte ladda filmlistan: {e}")

# --- 4. DET NYA BIBLIOTEKET ---
st.write("---")
st.header("📖 ARKIVET")

if os.path.exists(LIBRARY_DIR):
    all_files = []
    for root, dirs, files in os.walk(LIBRARY_DIR):
        for file in files:
            if file.endswith(('.html', '.txt', '.md')):
                rel_path = os.path.relpath(os.path.join(root, file), LIBRARY_DIR)
                all_files.append(rel_path)
    
    if all_files:
        all_files.sort()
        
        def format_file_names(path):
            clean_name = path.replace('.txt', '').replace('.html', '').replace('.md', '')
            clean_name = clean_name.replace('\\', ' / ').replace('/', ' / ')
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
                    st.text(content)
                st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Kunde inte läsa filen: {e}")
    else:
        st.write("Arkivet är tomt. Lägg till filer i mappen 'library'.")
else:
    st.error("Mappen 'library' hittades inte.")
