import streamlit as st
import pandas as pd
import os

# --- 1. GRUNDINSTÄLLNINGAR & SÖKVÄGAR ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(CURRENT_DIR, 'Filmlista - Blad1.csv')
LIBRARY_DIR = os.path.join(CURRENT_DIR, 'library')

# Definiera kategorier och deras mappar (mappnamn : Rubrik på sidan)
CATEGORIES = {
    "interviews": "🎙️ INTERVJUER",
    "reviews": "📝 RECENSIONER",
    "articles": "📰 ARTIKLAR",
    "essays": "🎓 UPPSATSER",
    "film-history": "🎞️ FILMHISTORIA",
    "press": "✂️ PRESSKLIPP"
}

# Skapa mappar automatiskt om de saknas
for folder in CATEGORIES.keys():
    full_path = os.path.join(LIBRARY_DIR, folder)
    if not os.path.exists(full_path):
        os.makedirs(full_path, exist_ok=True)

st.set_page_config(page_title="The Vault of Antichrister", layout="wide", page_icon="🎬")

# --- 2. DESIGN (CSS) ---
st.markdown("""
    <style>
    /* Bakgrund och textfärg */
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* Rubriker */
    h1 { color: #e50914 !important; border-bottom: 2px solid #e50914; padding-bottom: 10px; font-weight: 800; }
    h2 { color: #ffa500 !important; margin-top: 40px; border-left: 5px solid #ffa500; padding-left: 15px; }
    
    /* Filmkort i databasen */
    .movie-card { 
        background-color: #1e2129; 
        padding: 20px; 
        border-radius: 10px; 
        border-right: 5px solid #e50914;
        margin-bottom: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    }
    
    /* Den stora läsrutan för texter */
    .content-box { 
        background-color: #161b22; 
        padding: 40px; 
        border-radius: 10px; 
        border: 1px solid #30363d; 
        margin-top: 20px; 
        white-space: pre-wrap; 
        font-family: 'Georgia', serif; 
        font-size: 1.25em; 
        color: #f0f0f0; 
        line-height: 1.8;
        box-shadow: inset 0 0 10px #000;
    }
    
    /* Styling för rullistor */
    .stSelectbox label { color: #ffffff !important; font-weight: bold; font-size: 1.1em; }
    
    /* Avdelare */
    hr { border: 0; height: 1px; background: #30363d; margin: 40px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDANS TITEL ---
st.markdown("<h1>🎬 THE VAULT OF ANTICHRISTER</h1>", unsafe_allow_html=True)
st.write("Välkommen till arkivet för film, intervjuer och historiskt material.")

# --- 4. FILMDATABASEN (CSV-SEKTION) ---
if os.path.exists(CSV_PATH):
    with st.expander("🔍 ÖPPNA FILMDATABASEN", expanded=False):
        try:
            # Läs CSV och rensa bort helt tomma rader
            df = pd.read_csv(CSV_PATH).dropna(how='all')
            
            search_query = st.text_input("Sök efter film, regi eller genre:", placeholder="T.ex. Evil Dead...")
            
            if search_query:
                # Sök i alla kolumner samtidigt
                mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
                display_df = df[mask]
            else:
                display_df = df

            if not display_df.empty:
                selected_movie = st.selectbox("Välj en film för detaljer:", ["-- Välj film --"] + display_df['Titel'].tolist())
                
                if selected_movie != "-- Välj film --":
                    m = display_df[display_df['Titel'] == selected_movie].iloc[0]
                    st.markdown(f"""
                        <div class="movie-card">
                            <h2 style="margin-top:0; color:#fff !important;">{m['Titel'].upper()}</h2>
                            <p><strong>📅 År:</strong> {m.get('År', 'Okänt')}</p>
                            <p><strong>🎥 Regi:</strong> {m.get('Regi', 'Okänt')}</p>
                            <p><strong>🎭 Genre:</strong> {m.get('Genre', 'Okänt')}</p>
                            <p><strong>💿 Format/Disk:</strong> {m.get('Disk 1', '-')} / {m.get('Disk 2', '-')}</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Inga filmer matchade din sökning.")
        except Exception as e:
            st.error(f"Ett fel uppstod med filmdatabasen: {e}")
else:
    st.info("Filmdatabasen (CSV) kunde inte hittas. Kontrollera att filen ligger i huvudmappen.")

st.markdown("<hr>", unsafe_allow_html=True)

# --- 5. BIBLIOTEKET (INTERVJUER, ARTIKLAR OSV.) ---
def load_and_display_library():
    # Loopa igenom de fördefinierade kategorierna
    for folder_id, display_title in CATEGORIES.items():
        folder_path = os.path.join(LIBRARY_DIR, folder_id)
        
        if os.path.exists(folder_path):
            # Hämta alla filer med rätt ändelse
            valid_extensions = ('.txt', '.html', '.md')
            files = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)]
            
            if files:
                st.markdown(f"<h2>{display_title}</h2>", unsafe_allow_html=True)
                
                # Skapa en mappning: "Snygg titel" -> "faktiskt_filnamn.txt"
                name_map = {}
                for f in files:
                    clean_name = f.replace('.txt','').replace('.html','').replace('.md','').replace('-', ' ').replace('_', ' ').title()
                    name_map[clean_name] = f
                
                selected_label = st.selectbox(
                    f"Välj ett dokument:", 
                    ["-- Välj dokument --"] + sorted(list(name_map.keys())), 
                    key=folder_id
                )
                
                if selected_label != "-- Välj dokument --":
                    actual_file = name_map[selected_label]
                    file_path = os.path.join(folder_path, actual_file)
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        st.markdown('<div class="content-box">', unsafe_allow_html=True)
                        if actual_file.lower().endswith(".html"):
                            st.markdown(content, unsafe_allow_html=True)
                        else:
                            st.write(content)
                        st.markdown('</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Kunde inte läsa filen (den kan vara låst av OneDrive): {e}")

# Kör biblioteksfunktionen
load_and_display_library()

# --- 6. FOOTER ---
st.markdown("<hr>", unsafe_allow_html=True)
st.caption("© 2026 The Vault of Antichrister | Hanterat via Streamlit & GitHub")