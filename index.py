import streamlit as st
import pandas as pd
import os

# --- 1. SÖKVÄGAR ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(CURRENT_DIR, 'Filmlista - Blad1.csv')
LIBRARY_DIR = os.path.join(CURRENT_DIR, 'library')

# --- 2. SETUP & DESIGN ---
st.set_page_config(page_title="The Vault of Antichrister", layout="wide", page_icon="🎬")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    h1 { color: #e50914 !important; border-bottom: 2px solid #e50914; padding-bottom: 10px; font-weight: 800; }
    h2 { color: #ffa500 !important; margin-top: 40px; border-left: 5px solid #ffa500; padding-left: 15px; }
    .content-box { 
        background-color: #161b22; 
        padding: 35px; 
        border-radius: 10px; 
        border: 1px solid #30363d; 
        margin-top: 20px; 
        white-space: pre-wrap; 
        font-family: 'Georgia', serif; 
        font-size: 1.2em; 
        color: #f0f0f0; 
        line-height: 1.8;
    }
    .stSelectbox label { color: #ffffff !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 THE VAULT OF ANTICHRISTER")

# --- 3. FILMDATABASEN (CSV) ---
if os.path.exists(CSV_PATH):
    with st.expander("🔍 FILMDATABAS (SÖKBAR)", expanded=False):
        try:
            df = pd.read_csv(CSV_PATH).dropna(how='all')
            search = st.text_input("Sök film eller regi:")
            if search:
                df = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)]
            
            sel = st.selectbox("Välj film för info:", ["-- Välj --"] + df['Titel'].tolist())
            if sel != "-- Välj --":
                m = df[df['Titel'] == sel].iloc[0]
                st.info(f"**Titel:** {m['Titel']} | **Regi:** {m.get('Regi', 'N/A')} | **År:** {m.get('År', 'N/A')}")
        except: st.error("Kunde inte ladda CSV-filen.")

st.write("---")

# --- 4. BIBLIOTEKET (AUTOMATISKT) ---
# Här mappar vi mappnamn till snygga rubriker
CATEGORIES = {
    "interviews": "🎙️ INTERVJUER",
    "reviews": "📝 RECENSIONER",
    "articles": "📰 ARTIKLAR",
    "essays": "🎓 UPPSATSER",
    "film-history": "🎞️ FILMHISTORIA",
    "press": "✂️ PRESSKLIPP"
}

for folder_id, display_title in CATEGORIES.items():
    folder_path = os.path.join(LIBRARY_DIR, folder_id)
    
    if os.path.exists(folder_path):
        # Leta efter .txt filer
        files = [f for f in os.listdir(folder_path) if f.lower().endswith('.txt')]
        
        if files:
            st.header(display_title)
            # Gör filnamnen snygga för rullistan
            clean_names = {f.replace('.txt','').replace('-', ' ').title(): f for f in files}
            
            selected_label = st.selectbox(f"Välj i {display_title}:", ["-- Välj dokument --"] + sorted(list(clean_names.keys())), key=folder_id)
            
            if selected_label != "-- Välj dokument --":
                file_to_read = clean_names[selected_label]
                with open(os.path.join(folder_path, file_to_read), "r", encoding="utf-8") as f:
                    content = f.read()
                
                st.markdown(f'<div class="content-box">{content}</div>', unsafe_allow_html=True)

st.caption("© 2026 The Vault of Antichrister")