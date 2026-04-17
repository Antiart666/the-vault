import streamlit as st
import os

# Titeln som du vill ha den
st.title("🎬 THE VAULT OF ANTICHRISTER")

# 1. Hitta mappen 'library/interviews' direkt
# Vi använder en säker sökning som fungerar på Vercel
base_path = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(base_path, "library", "interviews")

# 2. Om mappen finns, skapa rullistan
if os.path.exists(folder_path):
    # Vi hämtar alla .txt (och .TXT) filer
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(".txt")]
    
    if files:
        # HÄR ÄR DIN RULLISTA - Vi döper den exakt till "Intervjuer"
        selected = st.selectbox("Intervjuer", ["-- Välj en intervju --"] + sorted(files))
        
        if selected != "-- Välj en intervju --":
            file_path = os.path.join(folder_path, selected)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Visar texten snyggt utan att ändra designen
                st.markdown(f"### {selected[:-4]}") # Visar filnamnet som rubrik
                st.info(content) 
    else:
        st.write("Hittade inga textfiler i mappen 'library/interviews'.")
else:
    # Om mappen inte hittas kollar vi om den ligger i en undermapp
    st.error("Kunde inte hitta biblioteket. Kontrollera att mappen 'library' ligger bredvid index.py på GitHub.")

# Vi tar bort felsöknings-boxen helt så sidan blir "ren" och perfekt!