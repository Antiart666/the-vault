import streamlit as st
import os

st.title("🎬 THE VAULT OF ANTICHRISTER")

# DAMMSUGAREN: Letar efter alla .txt-filer i hela projektet
all_txt_files = {}

for root, dirs, files in os.walk("."):
    for file in files:
        if file.lower().endswith(".txt") and file.lower() != "requirements.txt":
            # Vi sparar filens namn och dess exakta gömställe
            full_path = os.path.join(root, file)
            all_txt_files[file] = full_path

# OM VI HITTADE FILER
if all_txt_files:
    # Din rullista - exakt som du vill ha den
    lista = sorted(list(all_txt_files.keys()))
    selected = st.selectbox("Intervjuer", ["-- Välj en intervju --"] + lista)
    
    if selected != "-- Välj en intervju --":
        path_to_open = all_txt_files[selected]
        with open(path_to_open, "r", encoding="utf-8") as f:
            st.info(f.read())
else:
    # Om listan fortfarande är tom
    st.error("Systemet hittar inga .txt-filer alls på servern.")
    st.write("Dessa filer ser jag just nu:", os.listdir("."))