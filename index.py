import streamlit as st
import pandas as pd
import os

# --- 1. KONFIGURATION ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(CURRENT_DIR, 'Filmlista - Blad1.csv')
# Vi letar efter 'library' i huvudmappen
LIBRARY_DIR = os.path.join(CURRENT_DIR, 'library')

st.set_page_config(page_title="The Vault of Antichrister", layout="wide")

# --- 2. DESIGN (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    h1 { color: #e50914 !important; border-bottom: 2px solid #e50914; padding-bottom: 10px; }
    h2 { color: #ffa500 !important; margin-top: 40px; border-left: 5px solid #ffa500; padding-left: 15px; }
    .movie-card { background-color: #1e2129; padding: 20px; border-radius: 10px; border-left: 5px solid #e50914; margin-bottom: 20px; }
    .library-box { 
        background-color: #161b22; 
        padding: 30px; 
        border-radius: 10px; 
        border: 1px solid #30363d; 
        margin-top: 20px; 
        white-space: pre-wrap; 
        font-family: 'Georgia', serif; 
        font-size: 1.15em; 
        color: #f0f0f0; 
        line-height: 1.7;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 THE VAULT OF ANTICHRISTER")

# --- 3. FILMDATABASEN ---
if os.path.exists(CSV_PATH):
    with st.expander("🔍 ÖPPNA FILMDATABASEN", expanded=False):
        try:
            df = pd.read_csv(CSV_PATH)
            sel_movie = st.selectbox("Välj film:", ["-- Välj film --"] + df['Titel'].tolist())
            if sel_movie != "-- Välj film --":
                m = df[df['Titel'] == sel_movie].iloc[0]
                st.write(f"### {m['Titel']}")
                st.write(f"**Regi:** {m.get('Regi', '-')}")
        except: st.error("Kunde inte ladda CSV.")

st.write("---")

# --- 4. KATEGORIERNA ---
categories = {
    "reviews": "📝 RECENSIONER",
    "articles": "📰 ARTIKLAR",
    "essays": "🎓 UPPSATSER",
    "interviews": "🎙️ INTERVJUER",
    "film-history": "🎞️ FILMHISTORIA",
    "press": "✂️ PRESSKLIPP"
}

def load_category(folder_id, title):
    folder_path = os.path.join(LIBRARY_DIR, folder_id)
    
    # Om mappen finns på GitHub
    if os.path.exists(folder_path):
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.txt', '.html', '.md'))]
        
        if files:
            st.header(title)
            # Snygga till namnen
            name_map = {f.replace('.txt','').replace('.html','').replace('.md','').replace('-', ' ').title(): f for f in files}
            
            selected = st.selectbox(f"Välj ur {title}:", ["-- Välj --"] + sorted(list(name_map.keys())), key=folder_id)
            
            if selected != "-- Välj --":
                file_path = os.path.join(folder_path, name_map[selected])
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                st.markdown('<div class="library-box">', unsafe_allow_html=True)
                if file_path.lower().endswith(".html"):
                    st.markdown(content, unsafe_allow_html=True)
                else:
                    st.write(content)
                st.markdown('</div>', unsafe_allow_html=True)

# Loopa igenom kategorierna
for folder, display_title in categories.items():
    load_category(folder, display_title)