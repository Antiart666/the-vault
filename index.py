import streamlit as st
import pandas as pd
import os
import requests

# --- 1. GRUNDLÄGGANDE KONFIGURATION ---
st.set_page_config(page_title="The Vault of Antichrister", layout="wide")

# Titel enligt specifikation
st.title("🎬 THE VAULT OF ANTICHRISTER")

# --- 2. DYNAMISK SÖKVÄGSHANTERING (SKOTTSÄKER) ---
def hitta_mapp_rekursivt(mappnamn):
    """Letar efter en specifik mapp i hela projektet oavsett rot-katalog."""
    for root, dirs, files in os.walk("."):
        if mappnamn in dirs:
            return os.path.join(root, mappnamn)
    return None

# Hitta mappen för intervjuer
intervju_sokvag = hitta_mapp_rekursivt("interviews")

# Sökväg till filmdatabasen (CSV)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(CURRENT_DIR, 'Filmlista - Blad1.csv')

# API för affischer
TMDB_API_TOKEN = "DIN_TMDB_TOKEN_HÄR" # Behåll din befintliga token här

# --- 3. FUNKTIONER FÖR DATALADDNING ---
@st.cache_data
def load_movie_data():
    if os.path.exists(CSV_PATH):
        try:
            df = pd.read_csv(CSV_PATH, encoding='utf-8-sig', sep=None, engine='python')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            return df
        except Exception as e:
            st.error(f"Kunde inte läsa filmdatabasen: {e}")
    return pd.DataFrame()

def get_movie_poster(title, year):
    if TMDB_API_TOKEN == "DIN_TMDB_TOKEN_HÄR" or not TMDB_API_TOKEN: return None
    url = f"https://api.themoviedb.org/3/search/movie?query={title}&year={year}"
    headers = {"Authorization": f"Bearer {TMDB_API_TOKEN}"}
    try:
        response = requests.get(url, headers=headers, timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                path = data['results'].get('poster_path')
                if path: return f"https://image.tmdb.org/t/p/w500{path}"
    except: pass
    return None

# --- 4. SIDEBAR & AUTOMATISERAD RULLISTA (INTERVJUER) ---
st.sidebar.header("Navigation")

if intervju_sokvag:
    # Hämtar alla .txt-filer automatiskt vid varje laddning
    alla_intervjuer = [f for f in os.listdir(intervju_sokvag) if f.lower().endswith(".txt")]
    
    if alla_intervjuer:
        selected_interview = st.sidebar.selectbox(
            "Intervjuer", 
            ["-- Välj en intervju --"] + sorted(alla_intervjuer),
            format_func=lambda x: x.replace(".txt", "").replace("-", " ").title()
        )
        
        if selected_interview != "-- Välj en intervju --":
            with open(os.path.join(intervju_sokvag, selected_interview), "r", encoding="utf-8") as f:
                st.info(f.read()) # Visar textinnehållet i en tydlig box
    else:
        st.sidebar.warning("Inga .txt-filer hittades i 'interviews'.")
else:
    st.sidebar.error("Mappen 'interviews' kunde inte hittas.")

# --- 5. HUVUDINNEHÅLL: FILMARKIVET ---
df = load_movie_data()
search_query = st.text_input("🔍 Sök i filmdatabasen", "")

if not df.empty:
    f_df = df.copy()
    if search_query:
        f_df = f_df[f_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
    
    col_list, col_info = st.columns([1, 2.2])
    
    with col_list:
        st.write(f"**Träffar: {len(f_df)}**")
        with st.container(height=500):
            titel_col = 'Titel' if 'Titel' in f_df.columns else f_df.columns
            titles = sorted(f_df[titel_col].unique().tolist())
            selected_title = st.radio("Välj film", titles, label_visibility="collapsed")

    with col_info:
        if selected_title:
            m = df[df[titel_col] == selected_title].iloc
            st.subheader(str(m[titel_col]).upper())
            
            det_col, pos_col = st.columns([8, 9])
            with pos_col:
                poster = get_movie_poster(m[titel_col], m.get('År', ''))
                if poster: st.image(poster)
            
            with det_col:
                st.markdown(f"""
                **🎥 Regi:** {m.get('Regissör', m.get('Regi', '-'))}  
                **🎭 Skådespelare:** {m.get('Skådespelare', '-')}  
                **📅 År:** {m.get('År', '-')}  
                **📂 Plats:** {m.get('Sökväg', '-')}  
                **💿 Disk:** {m.get('Disk-markering', '-')}
                """)
                
                # Dynamisk länk för recensioner
                url_col = [c for c in df.columns if 'länk' in c.lower() or 'url' in c.lower() or 'recension' in c.lower()]
                if url_col:
                    url = m[url_col]
                    if pd.notnull(url) and str(url).startswith('http'):
                        st.link_button("🌐 LÄS RECENSION", str(url))