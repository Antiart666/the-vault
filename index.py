import streamlit as st
import os
import re
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


def samla_filer_fran_kategorisida(category_page):
    filer = {}
    if not os.path.isfile(category_page):
        return filer

    with open(category_page, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    match = re.search(
        r'<div class="reading-room">(.*?)</div>\s*<script',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return filer

    block = match.group(1)
    for href in re.findall(r'href="([^"]+)"', block, flags=re.IGNORECASE):
        if not href.lower().endswith(".html"):
            continue

        full_path = os.path.normpath(href)
        if not os.path.isfile(full_path):
            continue

        filnamn = os.path.basename(full_path)
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
    "Intervjuer": {
        "mappar": ["interviews", "Manus/Intervjuer"],
        "kategorisida": "cat_intervjuer.html",
    },
    "Artiklar": {
        "mappar": ["articles", "Manus/Artiklar"],
        "kategorisida": "cat_artiklar.html",
    },
    "Recensioner": {
        "mappar": ["reviews", "Manus/Recensioner"],
        "kategorisida": "cat_recensioner.html",
    },
}

vald_kategori = st.selectbox("Kategori", list(kategorier.keys()))
mappar = hitta_kandidatmappar(kategorier[vald_kategori]["mappar"])
kategorisida = kategorier[vald_kategori]["kategorisida"]

filer = samla_filer(mappar)
filer_fran_kategorisida = samla_filer_fran_kategorisida(kategorisida)

for filnamn, full_path in filer_fran_kategorisida.items():
    if filnamn not in filer:
        filer[filnamn] = full_path

if not filer:
    st.write(f"Inga filer hittades i kategorin {vald_kategori}.")
else:
    val = st.selectbox(
        vald_kategori,
        [f"-- Välj en text i {vald_kategori.lower()} --"] + sorted(filer.keys()),
    )

    if not val.startswith("-- Välj"):
        visa_fil(filer[val])