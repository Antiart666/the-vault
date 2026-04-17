import streamlit as st
import os

# 1. Din snygga titel
st.title("🎬 THE VAULT OF ANTICHRISTER")

# 2. Leta upp mappen 'interviews' var den än befinner sig
def hitta_intervju_mapp():
    # Vi letar i hela projektet efter en mapp som heter 'interviews'
    for root, dirs, files in os.walk("."):
        if "interviews" in dirs:
            return os.path.join(root, "interviews")
    return None

intervju_sokvag = hitta_intervju_mapp()

# 3. Om vi hittade mappen, visa din rullista
if intervju_sokvag:
    alla_filer = [f for f in os.listdir(intervju_sokvag) if f.lower().endswith(".txt")]
    
    if alla_filer:
        # HÄR ÄR DIN RULLISTA
        val = st.selectbox("Intervjuer", ["-- Välj en intervju --"] + sorted(alla_filer))
        
        if val != "-- Välj en intervju --":
            with open(os.path.join(intervju_sokvag, val), "r", encoding="utf-8") as f:
                st.info(f.read()) # Visar texten snyggt
    else:
        st.warning("Hittade mappen 'interviews', men den var tom på .txt-filer.")
else:
    # Denna rad hjälper oss att se vad som är fel utan att förstöra sidan
    st.error("Kunde inte hitta mappen 'interviews'.")
    st.write("Detta är vad servern ser just nu:", os.listdir("."))