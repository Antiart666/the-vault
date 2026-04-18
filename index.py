import streamlit as st
import os
import streamlit.components.v1 as components
import docx

# 1. Titel
st.title("🎬 THE VAULT OF ANTICHRISTER")

# 2. Hitta mappen (Skottsäker sökning som hittar 'interviews' var den än ligger)
def hitta_mappen():
    for root, dirs, files in os.walk("."):
        if "interviews" in [d.lower() for d in dirs]:
            for d in dirs:
                if d.lower() == "interviews":
                    return os.path.join(root, d)
    return None

folder_path = hitta_mappen()

# 3. Visa rullistan och filerna
if folder_path:
    # Hämtar alla filer du lagt där (.txt, .html, .docx)
    alla_filer = [f for f in os.listdir(folder_path) if f.lower().endswith((".txt", ".html", ".docx"))]
    
    if alla_filer:
        # Din befintliga rullista
        val = st.selectbox("Intervjuer", ["-- Välj en intervju --"] + sorted(alla_filer))
        
        if val != "-- Välj en intervju --":
            fil_stig = os.path.join(folder_path, val)
            ext = val.lower()
            
            # LÄS FILEN BASERAT PÅ TYP
            try:
                if ext.endswith(".docx"):
                    doc = docx.Document(fil_stig)
                    text = "\n".join([para.text for para in doc.paragraphs])
                    st.info(text)
                
                elif ext.endswith(".html"):
                    with open(fil_stig, "r", encoding="utf-8", errors="ignore") as f:
                        # Visar din gamla HTML exakt som den är
                        components.html(f.read(), height=1000, scrolling=True)
                
                else: # För .txt filer
                    with open(fil_stig, "r", encoding="utf-8", errors="ignore") as f:
                        st.info(f.read())
            except Exception as e:
                st.error(f"Kunde inte ladda filen: {e}")
    else:
        st.write("Inga filer hittades i mappen 'interviews'.")
else:
    st.error("Hittar inte mappen 'interviews'.")