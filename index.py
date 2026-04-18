import streamlit as st
import os
import streamlit.components.v1 as components

# 1. Inställningar för sidan
st.set_page_config(page_title="The Vault", layout="wide")
st.title("🎬 THE VAULT OF ANTICHRISTER")

# 2. Hitta mappen (Skottsäker sökning)
def hitta_mappen():
    for root, dirs, files in os.walk("."):
        if "interviews" in [d.lower() for d in dirs]:
            for d in dirs:
                if d.lower() == "interviews":
                    return os.path.join(root, d)
    return None

folder_path = hitta_mappen()

# 3. Om mappen finns, skapa rullistan
if folder_path:
    # Vi hämtar både .txt och .html (viktigt för David Hess!)
    alla_filer = [f for f in os.listdir(folder_path) if f.lower().endswith((".txt", ".html"))]
    
    if alla_filer:
        # Din rullista - AUTOMATISK (nya filer dyker upp här direkt)
        val = st.selectbox("Intervjuer", ["-- Välj en intervju --"] + sorted(alla_filer))
        import streamlit as st
import os
import streamlit.components.v1 as components
from bs4 import BeautifulSoup
import docx

# 1. Sidan inställningar
st.set_page_config(page_title="The Vault", layout="wide")
st.title("🎬 THE VAULT OF ANTICHRISTER")

# 2. Funktion för att läsa Word-filer (.docx)
def read_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# 3. Skottsäker sökning efter mappen 'interviews'
def hitta_mappen():
    for root, dirs, files in os.walk("."):
        if "interviews" in [d.lower() for d in dirs]:
            for d in dirs:
                if d.lower() == "interviews":
                    return os.path.join(root, d)
    return None

folder_path = hitta_mappen()

# 4. Huvudmeny och visning
if folder_path:
    # Hittar alla filer (txt, html, docx)
    alla_filer = [f for f in os.listdir(folder_path) if f.lower().endswith((".txt", ".html", ".docx"))]
    
    if alla_filer:
        val = st.selectbox("Intervjuer", ["-- Välj en intervju --"] + sorted(alla_filer))
        
        if val != "-- Välj en intervju --":
            fil_stig = os.path.join(folder_path, val)
            ext = val.lower()
            
            # --- VISNING BASERAT PÅ FILTYP ---
            
            # WORD-DOKUMENT (.docx)
            if ext.endswith(".docx"):
                text = read_docx(fil_stig)
                st.info(text)
            
            # HTML-FILER (.html från Netlify)
            elif ext.endswith(".html"):
                with open(fil_stig, "r", encoding="utf-8", errors="ignore") as f:
                    html_content = f.read()
                # Vi visar HTML-sidan i en egen box för att bevara designen från förr
                components.html(html_content, height=800, scrolling=True)
            
            # VANLIGA TEXTFILER (.txt)
            else:
                with open(fil_stig, "r", encoding="utf-8", errors="ignore") as f:
                    st.info(f.read())
    else:
        st.write("Mappen hittades men är tom.")
else:
    st.error("Kunde inte hitta mappen 'interviews' på GitHub.")

# Enkel felsökning som bara du ser
with st.expander("Systemstatus"):
    if folder_path:
        st.write(f"Söker i: {folder_path}")
        st.write(f"Hittade filer: {alla_filer}")
        if val != "-- Välj en intervju --":
            fil_stig = os.path.join(folder_path, val)
            
            # Vi läser filen med extra säkerhet för gamla format
            with open(fil_stig, "r", encoding="utf-8", errors="ignore") as f:
                innehall = f.read()
            
            # KOLLA FILTYP:
            if val.lower().endswith(".html"):
                # Om det är en gammal HTML-fil från Netlify, rendera den som en sida
                components.html(innehall, height=1000, scrolling=True)
            else:
                # Om det är en vanlig textfil, visa den som text
                st.info(innehall)
    else:
        st.write("Mappen hittades men den verkar vara tom.")
else:
    st.error("Kunde inte hitta mappen 'interviews' på GitHub.")

# Denna rad är bara för dig, så du ser att koden hittar rätt
if folder_path:
    with st.expander("Teknisk info (om något krånglar)"):
        st.write(f"Sökväg: {folder_path}")
        st.write(f"Filer som hittades: {alla_filer}")