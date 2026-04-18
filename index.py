import streamlit as st
import os
import streamlit.components.v1 as components
import docx

# 1. Titel
st.title("🎬 THE VAULT OF ANTICHRISTER")

def hitta_kandidatmappar(relative_paths):
    hittade = []
    for rel_path in relative_paths:
        normalized = os.path.normpath(rel_path)
        if os.path.isdir(normalized):
            hittade.append(normalized)
    return hittade


def samla_filer(folder_paths):
    filer = {}
    for folder in folder_paths:
        for filnamn in os.listdir(folder):
            if not filnamn.lower().endswith((".txt", ".html", ".docx")):
                continue

            full_path = os.path.join(folder, filnamn)
            if not os.path.isfile(full_path):
                continue

            if filnamn not in filer:
                filer[filnamn] = full_path

    return filer


def visa_fil(fil_stig):
    ext = fil_stig.lower()
    try:
        if ext.endswith(".docx"):
            doc = docx.Document(fil_stig)
            text = "\n".join([para.text for para in doc.paragraphs])
            st.info(text)

        elif ext.endswith(".html"):
            with open(fil_stig, "r", encoding="utf-8", errors="ignore") as f:
                components.html(f.read(), height=1000, scrolling=True)

        else:
            with open(fil_stig, "r", encoding="utf-8", errors="ignore") as f:
                st.info(f.read())
    except Exception as e:
        st.error(f"Kunde inte ladda filen: {e}")


kategorier = {
    "Intervjuer": ["interviews", "Manus/Intervjuer"],
    "Artiklar": ["articles", "Manus/Artiklar"],
    "Recensioner": ["reviews", "Manus/Recensioner"],
}

vald_kategori = st.selectbox("Kategori", list(kategorier.keys()))
mappar = hitta_kandidatmappar(kategorier[vald_kategori])

if not mappar:
    st.error(f"Hittar inga mappar för kategorin {vald_kategori}.")
else:
    filer = samla_filer(mappar)

    if not filer:
        st.write(f"Inga filer hittades i kategorin {vald_kategori}.")
    else:
        val = st.selectbox(
            vald_kategori,
            [f"-- Välj en text i {vald_kategori.lower()} --"] + sorted(filer.keys()),
        )

        if not val.startswith("-- Välj"):
            visa_fil(filer[val])