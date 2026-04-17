import streamlit as st
import os

# --- KONFIGURATION ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="The Vault - Debug Mode", layout="wide")
st.title("🎬 THE VAULT OF ANTICHRISTER")

# --- FELSÖKNING (Detta hjälper oss se problemet) ---
with st.expander("🛠️ FELSÖKNING: Vad ser servern?"):
    st.write(f"Nuvarande mapp: `{CURRENT_DIR}`")
    all_files = os.listdir(CURRENT_DIR)
    st.write(f"Filer i huvudmappen: `{all_files}`")
    
    # Kolla efter biblioteket (både stort och litet L)
    lib_path = None
    for name in ['library', 'Library']:
        if name in all_files:
            lib_path = os.path.join(CURRENT_DIR, name)
            st.success(f"Hittade biblioteksmappen: `{name}`")
            st.write(f"Innehåll i {name}: `{os.listdir(lib_path)}`")

# --- BIBLIOTEKS-KOD ---
if lib_path:
    # Vi letar efter undermappar
    subfolders = ['interviews', 'Interviews', 'reviews', 'Reviews']
    found_content = False
    
    for sub in subfolders:
        sub_path = os.path.join(lib_path, sub)
        if os.path.exists(sub_path):
            files = [f for f in os.listdir(sub_path) if f.lower().endswith('.txt')]
            if files:
                found_content = True
                st.header(f"🎙️ {sub.upper()}")
                selected = st.selectbox(f"Välj fil i {sub}:", ["-- Välj --"] + files)
                if selected != "-- Välj --":
                    with open(os.path.join(sub_path, selected), "r", encoding="utf-8") as f:
                        st.markdown(f'<div style="background:#161b22;padding:20px;border-radius:10px;">{f.read()}</div>', unsafe_allow_html=True)
    
    if not found_content:
        st.warning("Hittade biblioteksmappen, men inga .txt-filer inuti undermapparna.")
else:
    st.error("Kunde inte hitta mappen 'library' eller 'Library'. Kontrollera att den ligger i huvudmappen på GitHub.")