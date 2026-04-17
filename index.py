import streamlit as st
import pandas as pd
import os
import requests

# --- 1. KONFIGURATION OCH DESIGN ---
st.set_page_config(page_title="The Vault of Antichrister", layout="wide")

# CSS för att bevara din unika design (den röda arkiv-stilen)
st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    h1 { color: #e50914 !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    .movie-card { background-color: #1f2937; padding: 20px; border-radius: 12px; border-left: 6px solid #e50914; margin-bottom: 20px; }
    .stSelectbox label { color: #e50914 !important; font-weight: bold; }
    div.stRadio > div > label { background-color: #161b22; border: 1px solid #30363d; padding: 10px; border-radius: 8px; width: 100%; cursor: pointer; color: white; }
    div.stRadio > div > label > div:first-child { display: none; }
</style>
""", unsafe_allow_html=True)

st.title("🎬 THE VAULT OF ANTICHRISTER")

# --- 2. DYNAMISK SÖKVÄGSHANTERING (SKOTTSÄKER) ---
def hitta_mapp_rekursivt(mappnamn):
    """Letar efter en specifik mapp i hela projektet oavsett var skriptet startar [1]."""
    for root, dirs, files in os.walk("."):
        if mappnamn in dirs:
            return os.path.join(root, mappnamn)
    return None

# Koppling mellan mappar och dina rubriker på sidan [2]
KATEGORIER = {
    "articles": "📰 Artiklar",
    "clips": "✂️ Pressklipp",
    "esseys": "📝 Uppsats",
    "film-history": "📚 Filmhistoria",
    "interviews": "🎤 Intervjuer",
    "reviews": "🎥 Recensioner"
}

# --- 3. SIDEBAR: AUTOMATISKA RULLISTER FÖR BIBLIOTEKET ---
st.sidebar.title("📚 BIBLIOTEKET")

library_root = hitta_mapp_rekursivt("library")

if library_root:
    for mapp_id, rubrik in KATEGORIER.items():
        mapp_path = os.path.join(library_root, mapp_id)
        
        if os.path.exists(mapp_path):
            # Hämtar alla .txt och .html filer i mappen [1]
            filer = [f for f in os.listdir(mapp_path) if f.lower().endswith((".txt", ".html"))]
            
            if filer:
                val = st.sidebar.selectbox(
                    rubrik, 
                    ["-- Välj läsning --"] + sorted(filer),
                    key=mapp_id,
                    format_func=lambda x: x.replace(".txt", "").replace(".html", "").replace("-", " ").title()
                )
                
                # Visa innehållet om användaren väljer en fil
                if val != "-- Välj läsning --":
                    file_path = os.path.join(mapp_path, val)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        st.markdown("---")
                        if val.lower().endswith(".html"):
                            st.components.v1.html(content, height=600, scrolling=True)
                        else:
                            st.info(content)
else:
    st.sidebar.error("⚠️ Kunde inte hitta mappen 'library'. Kontrollera strukturen på GitHub.")

# --- 4. HUVUDINNEHÅLL: FILMARKIVET (DIN CSV-LOGIK) ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = 'Filmlista - Blad1.csv'
CSV_PATH = os.path.join(CURRENT_DIR, FILE_NAME)

@st.cache_data
def load_movie_data():
    if os.path.exists(CSV_PATH):
        try:
            # Läser din CSV (hanterar både komma och semikolon) [3]
            df = pd.read_csv(CSV_PATH, encoding='utf-8-sig', sep=None, engine='python')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            return df
        except Exception as e:
            st.error(f"Kunde inte läsa filmdatabasen: {e}")
    return pd.DataFrame()

df = load_movie_data()
st.sidebar.markdown("---")
search_query = st.sidebar.text_input("🔍 Sök i filmdatabasen", "")

if not df.empty:
    f_df = df.copy()
    if search_query:
        f_df = f_df[f_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
    
    col_list, col_info = st.columns([1, 2.2])
    
    with col_list:
        st.write(f"**Träffar: {len(f_df)}**")
        with st.container(height=600):
            titel_col = 'Titel' if 'Titel' in f_df.columns else f_df.columns
            titles = sorted(f_df[titel_col].unique().tolist())
            selected_title = st.radio("Välj film", titles, label_visibility="collapsed")

    with col_info:
        if selected_title:
            m = df[df[titel_col] == selected_title].iloc
            st.markdown(f"<h1>{str(m[titel_col]).upper()}</h1>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="movie-card">
                <p><strong>🎥 Regi:</strong> {m.get('Regissör', m.get('Regi', '-'))}</p>
                <p><strong>🎭 Skådespelare:</strong> {m.get('Skådespelare', '-')}</p>
                <p><strong>📅 År:</strong> {m.get('År', '-')}</p>
                <p><strong>📂 Plats:</strong> {m.get('Sökväg', '-')}</p>
                <p><strong>💿 Disk:</strong> {m.get('Disk-markering', '-')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Recensionslänk om den finns
            url_col = [c for c in df.columns if 'länk' in c.lower() or 'url' in c.lower() or 'recension' in c.lower()]
            if url_col:
                url = m[url_col]
                if pd.notnull(url) and str(url).startswith('http'):
                    st.link_button("🌐 LÄS RECENSION", str(url))