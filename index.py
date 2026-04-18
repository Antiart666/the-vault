import streamlit as st
import os
import streamlit.components.v1 as components

# 1. Inställningar och Titel
st.set_page_config(page_title="The Vault", layout="wide")
st.title("🎬 THE VAULT OF ANTICHRISTER")

# 2. Hitta mappen (Vi kollar de två vanligaste ställena)
possible_paths = ["library/interviews", "the-vault/library/interviews", "."]
folder_path = None

for p in possible_paths:
    if os.path.exists(p) and any(f.lower().endswith(('.txt', '.html')) for f in os.listdir(p)):
        folder_path = p
        break

# 3. Om vi hittat mappen, hantera listan
if folder_path:
    # Vi hämtar ALLA filer som är .txt eller .html
    filer = [f for f in os.listdir(folder_path) if f.lower().endswith((".txt", ".html"))]
    
    if filer:
        # Din rullista (sorterad så David Hess är lätt att hitta)
        val = st.selectbox("Intervjuer", ["-- Välj en intervju --"] + sorted(filer))
        
        if val != "-- Välj en intervju --":
            fil_stig = os.path.join(folder_path, val)
            
            try:
                # Vi öppnar filen med 'latin-1' som backup om det är gamla HTML-filer
                with open(fil_stig, "r", encoding="utf-8", errors="replace") as f:
                    innehall = f.read().strip()
                
                if not innehall:
                    st.error(f"Filen '{val}' verkar vara helt tom på GitHub.")
                else:
                    # Om det är en HTML-fil, visa den som en komponent
                    if val.lower().endswith(".html"):
                        components.html(innehall, height=800, scrolling=True)
                    else:
                        # Om det är text, visa den snyggt
                        st.markdown(f"### {val.replace('.txt', '').replace('.html', '')}")
                        st.info(innehall)
                        
            except Exception as e:
                st.error(f"Kunde inte läsa filen: {e}")
    else:
        st.warning("Inga .txt eller .html-filer hittades i mappen.")
else:
    st.error("Systemet hittar inte din 'interviews'-mapp. Kontrollera strukturen på GitHub.")