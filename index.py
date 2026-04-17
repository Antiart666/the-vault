import streamlit as st
import pandas as pd
import os

# --- 1. KONFIGURATION ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(CURRENT_DIR, 'Filmlista - Blad1.csv')

# --- 2. DEN SMARTA MAPPLÄSAREN ---
# Vi kollar både 'library' och 'Library' för att vara helt säkra
def get_library_path():
    p1 = os.path.join(CURRENT_DIR, 'library')
    p2 = os.path.join(CURRENT_DIR, 'Library')
    if os.path.exists(p2):
        return p2
    return p1

LIBRARY_DIR = get_library_path()

st.set_page_config(page_title="The Vault of Antichrister", layout="wide")

# --- 3. DESIGN (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    h1 { color: #e50914 !important; border-bottom: 2px solid #e50914; padding-bottom: 10px; }
    h2 { color: #ffa500 !important; margin-top: 40px; border-left: 5px solid #ffa500; padding-left: 15px; }
    .content-box { 
        background-color: #161b22; 
        padding: 30px; 
        border-radius: 10px; 
        border: 1px solid #30363d; 
        white-space: pre-wrap; 
        font-family: 'Georgia', serif; 
        font-size: 1.2em; 
        color: #f0f0f0; 
        line-height: 1.7;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 THE VAULT OF ANTICHRISTER")

# --- 4. FILMDATABASEN ---
if os.path.exists(CSV_PATH):
    with st.expander("🔍 FILMDATABAS (SÖKBAR)", expanded=False):
        try:
            df = pd.read_csv(CSV_PATH)
            sel = st.selectbox("Välj film:", ["-- Välj --"] + df['Titel'].tolist())
            if sel != "-- Välj --":
                m = df[df['Titel'] == sel].iloc[0]
                st.info(f"**Titel:** {m['Titel']} | **Regi:** {m.get('Regi', 'N/A')}")
        except: st.error("Kunde inte läsa CSV.")

st.write("---")

# --- 5. BIBLIOTEKET (Här sker magin) ---
CATEGORIES = {
    "interviews": "🎙️ INTERVJUER",
    "reviews": "📝 RECENSIONER",
    "articles": "📰 ARTIKLAR"
}

# Vi kollar igenom kategorierna
for folder_id, display_title in CATEGORIES.items():
    # Vi kollar både 'interviews' och 'Interviews'
    folder_path = os.path.join(LIBRARY_DIR, folder_id)
    folder_path_alt = os.path.join(LIBRARY_DIR, folder_id.capitalize())
    
    final_path = folder_path if os.path.exists(folder_path) else folder_path_alt
    
    if os.path.exists(final_path):
        files = [f for f in os.listdir(final_path) if f.lower().endswith('.txt')]
        
        if files:
            st.header(display_title)
            clean_names = {f.replace('.txt','').replace('-', ' ').title(): f for f in files}
            selected = st.selectbox(f"Välj i {display_title}:", ["-- Välj --"] + sorted(list(clean_names.keys())), key=folder_id)
            
            if selected != "-- Välj --":
                with open(os.path.join(final_path, clean_names[selected]), "r", encoding="utf-8") as f:
                    st.markdown(f'<div class="content-box">{f.read()}</div>', unsafe_allow_html=True)

st.caption("© 2026 The Vault")