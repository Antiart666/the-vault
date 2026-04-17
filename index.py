import streamlit as st
import os

# Din perfekta titel
st.title("🎬 THE VAULT OF ANTICHRISTER")

# Vi definierar den exakta stigen som du ser på GitHub
# Vi kollar både med och utan "the-vault" i början för att vara helt säkra
path1 = "the-vault/library/interviews"
path2 = "library/interviews"

folder_path = None
if os.path.exists(path1):
    folder_path = path1
elif os.path.exists(path2):
    folder_path = path2

if folder_path:
    # Vi hämtar alla .txt-filer
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(".txt")]
    
    if files:
        # Din rullista - nu med rätt namn och rätt filer!
        selected = st.selectbox("Intervjuer", ["-- Välj en intervju --"] + sorted(files))
        
        if selected != "-- Välj en intervju --":
            with open(os.path.join(folder_path, selected), "r", encoding="utf-8") as f:
                st.info(f.read())
    else:
        st.write("Mappen hittades, men den verkar vara tom på .txt-filer.")
else:
    # Om mappen fortfarande inte hittas visar vi vad servern faktiskt ser
    st.error("Hittar inte mappen 'library/interviews'.")
    st.write("Filer på servern just nu:", os.listdir("."))