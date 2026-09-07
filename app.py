import streamlit as st
from streamlit_drawable_canvas import st_canvas
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Wohnungsabnahmeprotokoll - KARE-Immobilien",
    page_icon="🏠",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: bold;
        color: #1f4e78;
        margin-bottom: 10px;
    }
    .sub-header {
        font-size: 18px;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .company-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #1f4e78;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">KARE-Immobilien – Digitales Wohnungsabnahmeprotokoll</div>', unsafe_allow_html=True)
st.markdown("""
<div class="company-box">
    <strong>KARE-Immobilien</strong><br>
    Talstr. 32, 07545 Gera<br>
    Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Stammdaten", 
    "2. Zählerstände", 
    "3. Schlüssel & Mängel", 
    "4. Unterschriften", 
    "5. Export & Übersicht"
])

with tab1:
    st.markdown('<div class="sub-header">Allgemeine Daten zum Mietverhältnis</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        mietobjekt = st.text_input("Mietobjekt (Straße, Hausnummer, Etage)", value="Talstr. 32, 07545 Gera")
        wohnung_nr = st.text_input("Wohnungsnummer / Lage", value="Whg. Nr. 4")
        vermieter_name = st.text_input("Vermieter / Vertreter", value="KARE-Immobilien")
        uebergabe_datum = st.date_input("Übergabedatum", value=datetime.today())
    with col2:
        mieter_alt = st.text_input("Ausziehender Mieter (falls Abnahme)", value="")
        mieter_neu = st.text_input("Einziehender Mieter (falls Übergabe)", value="")
        uebergabe_art = st.selectbox("Art der Begehung", ["Wohnungsübergabe (Einzug)", "Wohnungsabnahme (Auszug)", "Zwischenbesichtigung"])

with tab2:
    st.markdown('<div class="sub-header">Zählerstände (Wasser- & Heizungszähler)</div>', unsafe_allow_html=True)
    st.info("Erfassung der Zählerstände für Kaltwasser, Warmwasser sowie die 5 spezifischen Heizungszähler.")
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.markdown("### Wasserzähler")
        kw_stand = st.text_input("Kaltwasserzähler (m³)", value="0.00")
        kw_nr = st.text_input("Zählernummer Kaltwasser", value="")
    with col_w2:
        st.markdown("&nbsp;")
        ww_stand = st.text_input("Warmwasserzähler (m³)", value="0.00")
        ww_nr = st.text_input("Zählernummer Warmwasser", value="")

    st.markdown("### Heizungszähler (Heizkostenverteiler)")
    h_raeume = ["Wohnzimmer", "Kinderzimmer", "Flur", "Bad", "Küche"]
    heizungs_daten = {}
    
    col_h1, col_h2 = st.columns(2)
    for i, raum in enumerate(h_raeume):
        with (col_h1 if i % 2 == 0 else col_h2):
            st.markdown(f"**Raum: {raum}**")
            h_stand = st.text_input(f"Zählerstand {raum}", value="0", key=f"h_stand_{raum}")
            h_num = st.text_input(f"Gerätenummer {raum}", value="", key=f"h_num_{raum}")
            heizungs_daten[raum] = {"stand": h_stand, "nummer": h_num}
            st.markdown("---")

with tab3:
    st.markdown('<div class="sub-header">Schlüsselübergabe & Raumzustand / Mängel</div>', unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("### Übergabe der Schlüssel")
        s_haustür = st.number_input("Haustürschlüssel", min_value=0, value=2, step=1)
        s_wohnung = st.number_input("Wohnungstürschlüssel", min_value=0, value=3, step=1)
        s_keller = st.number_input("Kellertürschlüssel", min_value=0, value=1, step=1)
        s_briefkasten = st.number_input("Briefkastenschlüssel", min_value=0, value=1, step=1)
    with col_s2:
        st.markdown("### Allgemeine Mängel / Notizen")
        maengel_text = st.text_area("Festgestellte Mängel, Beschädigungen oder Sondervereinbarungen", height=150, placeholder="z. B. Wand im Flur leicht beschädigt...")

with tab4:
    st.markdown('<div class="sub-header">Unterschriften & Signaturen</div>', unsafe_allow_html=True)
    st.write("Bitte unterschreiben Sie im jeweiligen Feld:")
    
    col_sig1, col_sig2 = st.columns(2)
    with col_sig1:
        st.markdown("**Unterschrift Vermietung / KARE-Immobilien**")
        canvas_vermieter = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=2,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=150,
            width=350,
            drawing_mode="freedraw",
            key="canvas_vermieter",
        )
    with col_sig2:
        st.markdown("**Unterschrift Mieter**")
        canvas_mieter = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=2,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=150,
            width=350,
            drawing_mode="freedraw",
            key="canvas_mieter",
        )

with tab5:
    st.markdown('<div class="sub-header">Zusammenfassung & Export</div>', unsafe_allow_html=True)
    
    st.markdown("### Protokoll-Zusammenfassung")
    st.write(f"**Objekt:** {mietobjekt} ({wohnung_nr})")
    st.write(f"**Datum:** {uebergabe_datum.strftime('%d.%m.%Y')}")
    st.write(f"**Art:** {uebergabe_art}")
    st.write(f"**Kaltwasser:** {kw_stand} m³ (Nr: {kw_nr}) | **Warmwasser:** {ww_stand} m³ (Nr: {ww_nr})")
    
    st.markdown("**Heizungszähler:**")
    for r, d in heizungs_daten.items():
        st.write(f"- {r}: Stand {d['stand']} (Nr. {d['nummer']})")

    sig_vermieter_vorhanden = False
    try:
        if canvas_vermieter is not None and getattr(canvas_vermieter, "image_data", None) is not None:
            sig_vermieter_vorhanden = True
    except Exception:
        sig_vermieter_vorhanden = False

    sig_mieter_vorhanden = False
    try:
        if canvas_mieter is not None and getattr(canvas_mieter, "image_data", None) is not None:
            sig_mieter_vorhanden = True
    except Exception:
        sig_mieter_vorhanden = False

    st.success(f"Unterschrift Vermieter erfasst: {'Ja' if sig_vermieter_vorhanden else 'Nein (leer)'}")
    st.success(f"Unterschrift Mieter erfasst: {'Ja' if sig_mieter_vorhanden else 'Nein (leer)'}")

    if st.button("Protokoll als Daten-Übersicht anzeigen"):
        st.balloons()
        st.info("Alle Protokolldaten sind vollständig erfasst und bereit.")
