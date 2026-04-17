import streamlit as st
import pandas as pd
import os
import requests

<<<<<<< HEAD
# --- 1. KONFIGURATION & DESIGN ---
st.set_page_config(page_title="The Vault of Antichrister", layout="wide")

# CSS för att bevara din unika "Arkiv-kontroll"-design
st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    h1 { color: #e50914 !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    .movie-card { background-color: #1f2937; padding: 20px; border-radius: 12px; border-left: 6px solid #e50914; margin-bottom: 20px; }
    .stSelectbox label { color: #e50914 !important; font-weight: bold; }
    .stInfo { background-color: #1f2937; border-left: 5px solid #e50914; color: white; }
    div.stRadio > div > label { background-color: #161b22; border: 1px solid #30363d; padding: 10px; border-radius: 8px; width: 100%; cursor: pointer; color: white; }
    div.stRadio > div > label > div:first-child { display: none; }
</style>
""", unsafe_allow_html=True)

st.title("🎬 THE VAULT OF ANTICHRISTER")

# --- 2. AUTOMATISERAT BIBLIOTEK (TEXTERNA) ---
# Koppling mellan mappar i library/ och rubrikerna på sidan
KATEGORIER = {
    "articles": "📰 Artiklar",
    "clips": "✂️ Pressklipp",
    "esseys": "📝 Uppsats",
    "film-history": "📚 Filmhistoria",
    "interviews": "🎤 Intervjuer",
    "reviews": "🎥 Recensioner"
}

def hitta_mapp_rekursivt(mappnamn):
    """Letar upp library-mappen oavsett var skriptet körs."""
    for root, dirs, files in os.walk("."):
        if mappnamn in dirs:
            return os.path.join(root, mappnamn)
    return None

st.sidebar.title("📚 BIBLIOTEK")
library_root = hitta_mapp_rekursivt("library")

if library_root:
    for mapp_id, rubrik in KATEGORIER.items():
        mapp_path = os.path.join(library_root, mapp_id)
        if os.path.exists(mapp_path):
            # Hämtar både textfiler och HTML-artiklar
            filer = sorted([f for f in os.listdir(mapp_path) if f.lower().endswith((".txt", ".html"))])
            if filer:
                val = st.sidebar.selectbox(rubrik, ["-- Välj läsning --"] + filer, key=mapp_id)
                if val != "-- Välj läsning --":
                    with open(os.path.join(mapp_path, val), "r", encoding="utf-8") as f:
                        innehall = f.read()
                        if val.endswith(".html"):
                            st.components.v1.html(innehall, height=600, scrolling=True)
                        else:
                            st.info(innehall)
else:
    st.sidebar.error("Kunde inte hitta mappen 'library'.")

# --- 3. FILMDATABASEN (CSV) ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = 'Filmlista - Blad1.csv'
CSV_PATH = os.path.join(CURRENT_DIR, FILE_NAME)

@st.cache_data
def load_movie_data():
    if os.path.exists(CSV_PATH):
        # Läser din CSV (hanterar både komma och semikolon automatiskt)
        df = pd.read_csv(CSV_PATH, encoding='utf-8-sig', sep=None, engine='python')
        return df.loc[:, ~df.columns.str.contains('^Unnamed')]
    return pd.DataFrame()

df = load_movie_data()
st.sidebar.markdown("---")
search_query = st.sidebar.text_input("🔍 Sök i filmdatabasen", "")

=======
# --- 1. KONFIGURATION OCH SÖKVÄG (SÄKERSTÄLLD FÖR VERCEL) ---
# Genom att använda os.path ser vi till att koden alltid letar i samma mapp 
# som index.py ligger i, oavsett om det är på din dator eller i molnet.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = 'Filmlista - Blad1.csv'
FULL_PATH = os.path.join(CURRENT_DIR, FILE_NAME)

# API för affischer
TMDB_API_TOKEN = "DIN_TMDB_TOKEN_HÄR"

st.set_page_config(page_title="Film-Arkivet Pro", layout="wide")

# --- 2. FELSÖKNINGS-CHECK ---
if not os.path.exists(FULL_PATH):
    st.error(f"⚠️ FILEN HITTADES INTE!")
    st.write("Se till att 'Filmlista - Blad1.csv' ligger i samma GitHub-mapp som index.py.")
    st.stop()

# --- 3. DESIGN (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    h1 { color: #e50914 !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    .movie-card { background-color: #1f2937; padding: 20px; border-radius: 12px; border-left: 6px solid #e50914; }
    div.stRadio > div > label { background-color: #161b22; border: 1px solid #30363d; padding: 10px; border-radius: 8px; width: 100%; cursor: pointer; }
    div.stRadio > div > label > div:first-child { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNKTIONER ---
@st.cache_data
def load_data():
    try:
        # Läser filen smart och hanterar oavsett om det är komma eller semikolon
        df = pd.read_csv(FULL_PATH, encoding='utf-8-sig', sep=None, engine='python')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        if 'År' in df.columns:
            df['År'] = pd.to_numeric(df['År'], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"Kunde inte läsa CSV-filen: {e}")
        return pd.DataFrame()

def get_movie_poster(title, year):
    if TMDB_API_TOKEN == "DIN_TMDB_TOKEN_HÄR" or not TMDB_API_TOKEN: return None
    url = f"https://api.themoviedb.org/3/search/movie?query={title}&year={year}"
    headers = {"Authorization": f"Bearer {TMDB_API_TOKEN}"}
    try:
        response = requests.get(url, headers=headers, timeout=2)
        data = response.json()
        if data.get('results'):
            path = data['results'][0].get('poster_path')
            if path: return f"https://image.tmdb.org/t/p/w500{path}"
    except: pass
    return None

# Ladda data
df = load_data()

# --- 5. SIDEBAR & SÖK ---
st.sidebar.title("🎬 ARKIV-KONTROLL")
search_query = st.sidebar.text_input("🔍 Sök i hela basen", "")

# --- 6. HUVUDINNEHÅLL ---
>>>>>>> parent of 11123b9 (Merge branch 'main' of https://github.com/Antiart666/the-vault)
if not df.empty:
    f_df = df.copy()
    if search_query:
        f_df = f_df[f_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
<<<<<<< HEAD
    
    col_list, col_info = st.columns([1, 2.2])
    with col_list:
        st.write(f"**Träffar: {len(f_df)}**")
        with st.container(height=600):
            titles = sorted(f_df['Titel'].unique().tolist()) if 'Titel' in f_df.columns else []
            selected_title = st.radio("Välj film", titles, label_visibility="collapsed")

    with col_info:
        if selected_title:
            m = df[df['Titel'] == selected_title].iloc
            st.markdown(f"<h1>{str(m['Titel']).upper()}</h1>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="movie-card">
                <p><strong>🎥 Regi:</strong> {m.get('Regissör', m.get('Regi', '-'))}</p>
                <p><strong>🎭 Skådespelare:</strong> {m.get('Skådespelare', '-')}</p>
                <p><strong>📅 År:</strong> {m.get('År', '-')}</p>
                <p><strong>📂 Plats:</strong> {m.get('Sökväg', '-')}</p>
            </div>
            """, unsafe_allow_html=True)
=======

    col_list, col_info = st.columns([1, 2.2])

    with col_list:
        st.write(f"**Träffar: {len(f_df)}**")
        with st.container(height=700):
            titel_col = 'Titel' if 'Titel' in f_df.columns else f_df.columns[0]
            titles = sorted(f_df[titel_col].unique().tolist())
            selected_title = st.radio("Välj", titles, label_visibility="collapsed")

    with col_info:
        if selected_title:
            titel_col = 'Titel' if 'Titel' in df.columns else df.columns[0]
            m = df[df[titel_col] == selected_title].iloc[0]
            st.markdown(f"<h1>{str(m[titel_col]).upper()}</h1>", unsafe_allow_html=True)
            st.write(f"### {m.get('År', '')} | {m.get('Genre', '')}")

            det_col, pos_col = st.columns([1.6, 1])
            with pos_col:
                poster = get_movie_poster(m[titel_col], m.get('År', ''))
                if poster: st.image(poster, use_container_width=True)
            
            with det_col:
                st.markdown(f"""
                    <div class="movie-card">
                        <p><strong>🎥 Regi:</strong> {m.get('Regissör', m.get('Regi', '-'))}</p>
                        <p><strong>🎭 Skådespelare:</strong> {m.get('Skådespelare', '-')}</p>
                        <p><strong>⏳ Tid:</strong> {m.get('Tid (min)', '-')} min</p>
                        <p><strong>📂 Plats:</strong> {m.get('Sökväg', '-')}</p>
                        <p><strong>💿 Disk:</strong> {m.get('Disk-markering', '-')}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                url_col = [c for c in df.columns if 'länk' in c.lower() or 'url' in c.lower()]
                if url_col:
                    url = m[url_col[0]]
                    if pd.notnull(url) and str(url).startswith('http'):
                        st.link_button("🌐 LÄS RECENSION", str(url), use_container_width=True)
>>>>>>> parent of 11123b9 (Merge branch 'main' of https://github.com/Antiart666/the-vault)
