import streamlit as st
import os

# --- 1. SETUP ---
st.set_page_config(page_title="The Vault of Antichrister", layout="wide")

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

# --- 2. DEN ULTIMATA FIL-SKANNERN ---
# Den här funktionen letar i ALLA mappar efter dina filer
def find_all_txt_files():
    found_files = {}
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    for root, dirs, files in os.walk(current_dir):
        # Vi ignorerar dolda mappar som .git
        if '.git' in root:
            continue
            
        for file in files:
            if file.lower().endswith('.txt'):
                # Vi kollar vilken mapp filen ligger i för att gissa kategori
                category = os.path.basename(root).lower()
                if category not in found_files:
                    found_files[category] = []
                
                full_path = os.path.join(root, file)
                found_files[category].append((file, full_path))
    return found_files

all_content = find_all_txt_files()

# --- 3. PRESENTATION ---
if not all_content:
    st.warning("Hittade inga .txt-filer i projektet. Kontrollera att filerna är uppladdade på GitHub.")
else:
    # Vi mappar mappnamn till snygga rubriker
    labels = {
        "interviews": "🎙️ INTERVJUER",
        "reviews": "📝 RECENSIONER",
        "articles": "📰 ARTIKLAR",
        "essays": "🎓 UPPSATSER",
        "library": "📚 BIBLIOTEK"
    }

    for folder_name in sorted(all_content.keys()):
        # Om vi har ett snyggt namn använd det, annars använd mappnamnet
        display_title = labels.get(folder_name, f"📁 {folder_name.upper()}")
        
        st.header(display_title)
        file_list = all_content[folder_name]
        
        # Skapa en lista med bara filnamnen för rullistan
        file_names = [f[0] for f in file_list]
        selected_file_name = st.selectbox(f"Välj i {folder_name}:", ["-- Välj --"] + file_names, key=folder_name)
        
        if selected_file_name != "-- Välj --":
            # Hitta rätt sökväg för den valda filen
            file_path = next(f[1] for f in file_list if f[0] == selected_file_name)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text_data = f.read()
                st.markdown(f'<div class="content-box">{text_data}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Kunde inte läsa filen: {e}")

st.write("---")
st.caption("Systemet skannar automatiskt efter nya .txt-filer.")