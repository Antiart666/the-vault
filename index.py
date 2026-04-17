import streamlit as st
import os

# --- SETUP ---
st.set_page_config(page_title="The Vault of Antichrister", layout="wide")

# CSS för snyggt utseende
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    h1 { color: #e50914 !important; border-bottom: 2px solid #e50914; }
    .content-box { background-color: #161b22; padding: 30px; border-radius: 10px; border: 1px solid #30363d; line-height: 1.7; font-family: serif; font-size: 1.2em; color: #f0f0f0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 THE VAULT OF ANTICHRISTER")

# --- DEN SMARTA SKANNERN ---
# Denna funktion letar i ALLA undermappar efter .txt-filer
def find_all_texts():
    results = {}
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    for root, dirs, files in os.walk(base_path):
        # Skippa dolda mappar
        if '.git' in root or '.streamlit' in root:
            continue
            
        txt_files = [f for f in files if f.lower().endswith('.txt')]
        if txt_files:
            # Använd mappnamnet som kategori
            folder_name = os.path.basename(root)
            if folder_name not in results:
                results[folder_name] = []
            for f in txt_files:
                results[folder_name].append(os.path.join(root, f))
    return results

all_data = find_all_texts()

if not all_data:
    st.error("Inga .txt-filer hittades någonstans i projektet. Kontrollera att de är uppladdade på GitHub.")
else:
    # Sortera kategorier snyggt (Intervjuer först om det finns)
    for category in sorted(all_data.keys()):
        if category.lower() in ["venv", "lib", "site-packages", "__pycache__"]:
            continue # Skippa system-mappar
            
        st.header(f"📁 {category.upper()}")
        
        file_paths = all_data[category]
        file_map = {os.path.basename(p).replace('.txt', '').replace('-', ' ').title(): p for p in file_paths}
        
        selected = st.selectbox(f"Välj dokument i {category}:", ["-- Välj --"] + list(file_map.keys()), key=category)
        
        if selected != "-- Välj --":
            path_to_open = file_map[selected]
            with open(path_to_open, "r", encoding="utf-8") as f:
                content = f.read()
            st.markdown(f'<div class="content-box">{content}</div>', unsafe_allow_html=True)

st.write("---")
st.caption("Systemet skannar automatiskt alla mappar efter innehåll.")