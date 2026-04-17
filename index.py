import streamlit as st
import os

st.title("🎬 THE VAULT OF ANTICHRISTER")

# 1. Hitta rätt mapp (Gör ingen skillnad på stora/små bokstäver)
base_path = os.path.dirname(__file__)
all_folders = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]

# Letar efter mappen 'library' oavsett om den heter Library, LIBRARY eller library
lib_folder = next((d for d in all_folders if d.lower() == "library"), None)

if lib_folder:
    # Gå in i mappen och leta efter undermappar (t.ex. interviews)
    lib_path = os.path.join(base_path, lib_folder)
    sub_folders = [d for d in os.listdir(lib_path) if os.path.isdir(os.path.join(lib_path, d))]
    
    for sub in sub_folders:
        st.header(f"📁 {sub.upper()}")
        sub_path = os.path.join(lib_path, sub)
        # Hitta alla .txt-filer
        files = [f for f in os.listdir(sub_path) if f.lower().endswith(".txt")]
        
        if files:
            selected = st.selectbox(f"Välj i {sub}:", ["-- Välj --"] + files)
            if selected != "-- Välj --":
                with open(os.path.join(sub_path, selected), "r", encoding="utf-8") as f:
                    st.text_area("", f.read(), height=400)
        else:
            st.write("Inga .txt-filer hittades här.")
else:
    st.error("Kunde inte hitta mappen 'library' på GitHub. Kolla att den inte ligger inuti en annan mapp!")

# En liten lista längst ner som bara DU ser, för att vi ska veta vad som är fel
with st.expander("Teknisk felsökning (Klicka om det inte funkar)"):
    st.write("Mappar på servern:", all_folders)