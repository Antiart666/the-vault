import streamlit as st
import os

st.title("🎬 THE VAULT OF ANTICHRISTER")

# DEN SMARTA SÖKAREN: Letar efter mappen 'interviews' var den än gömmer sig
def hitta_mappen():
    for root, dirs, files in os.walk("."):
        if "interviews" in [d.lower() for d in dirs]:
            # Hittade mappen! Vi returnerar den exakta sökvägen
            for d in dirs:
                if d.lower() == "interviews":
                    return os.path.join(root, d)
    return None

folder_path = hitta_mappen()

if folder_path:
    # Vi har hittat mappen, nu hämtar vi filerna
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(".txt")]
    
    if files:
        # Din rullista - exakt som du vill ha den
        selected = st.selectbox("Intervjuer", ["-- Välj en intervju --"] + sorted(files))
        
        if selected != "-- Välj en intervju --":
            with open(os.path.join(folder_path, selected), "r", encoding="utf-8") as f:
                st.info(f.read())
    else:
        st.warning("Mappen 'interviews' hittades, men den verkar vara tom på .txt-filer.")
else:
    # Detta visas bara om mappen faktiskt inte finns på GitHub
    st.error("Kunde inte hitta mappen 'interviews' i projektet.")
    st.write("Filer som servern ser:", os.listdir("."))