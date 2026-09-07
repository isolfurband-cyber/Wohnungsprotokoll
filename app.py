import os
import tempfile
from datetime import datetime
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from fpdf import FPDF

# Seitenkonfiguration
st.set_page_config(page_title="KARE-Immobilien - Wohnungsabnahmeprotokoll", page_icon="📋", layout="wide")

# Styling anpassen
st.markdown("""
    <style>
    .main-header { font-size: 24px; font-weight: bold; color: #1f3bb3; }
    .sub-header { font-size: 18px; font-weight: bold; margin-top: 20px; color: #333333; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">KARE-Immobilien – Wohnungsabnahmeprotokoll</p>', unsafe_allow_html=True)
st.markdown("Talstr. 32, 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de")
st.write("---")

# Session State für temporäre Dateien initialisieren
if "temp_files" not in st.session_state:
    st.session_state.temp_files = []

# --- FORMULAR DATEN ---
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="sub-header">1. Objektdaten & Parteien</p>', unsafe_allow_html=True)
    strasse = st.text_input("Straße & Hausnummer", "Talstr. 32")
    plz_ort = st.text_input("PLZ & Ort", "07545 Gera")
    wohnungseinheit = st.text_input("Wohnung / Lage", "OG links")
    
    vermieter_name = st.text_input("Vermieter / Vertreter", "KARE-Immobilien")
    mieter_name = st.text_input("Mieter (Neu/Alt)", "Max Mustermann")

with col2:
    st.markdown('<p class="sub-header">Datum & Übergabeart</p>', unsafe_allow_html=True)
    erstellungs_datum = st.date_input("Datum der Abnahme", datetime.now())
    uebergabe_art = st.selectbox("Anlass der Übergabe", ["Einzug (Übergabe)", "Auszug (Rückgabe)", "Zwischenprüfung"])
    schluessel_anzahl = st.number_input("Anzahl übergebener Schlüssel", min_value=0, max_value=50, value=3)

# --- ZÄHLERSTANDE ---
st.markdown('<p class="sub-header">2. Zählerstände</p>', unsafe_allow_html=True)
zc1, zc2 = st.columns(2)

with zc1:
    st.write("**Wasserzähler**")
    zaehler_kalt = st.text_input("Zählerstand Kaltwasser (m³)", "124.50")
    zaehler_warm = st.text_input("Zählerstand Warmwasser (m³)", "45.20")

with zc2:
    st.write("**Heizungszähler (Heizkostenverteiler)**")
    hz_wohnen = st.text_input("Heizungszähler - Wohnzimmer", "1023")
    hz_kind = st.text_input("Heizungszähler - Kinderzimmer", "412")
    hz_flur = st.text_input("Heizungszähler - Flur", "89")
    hz_bad = st.text_input("Heizungszähler - Bad", "305")
    hz_kuche = st.text_input("Heizungszähler - Küche", "154")

# --- MÄNGEL & ZUSTAND ---
st.markdown('<p class="sub-header">3. Zustand der Räume & Mängel</p>', unsafe_allow_html=True)
maengel_text = st.text_area("Festgestellte Mängel, Schäden oder Sondervereinbarungen", "Keine gravierenden Mängel festgestellt. Leichte Gebrauchsspuren an der Sockelleiste im Flur.")

# --- FOTO-UPLOAD ---
st.markdown('<p class="sub-header">4. Fotodokumentation (optional)</p>', unsafe_allow_html=True)
uploaded_photos = st.file_uploader("Fotos von Mängeln / Zählerständen hochladen", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

# --- UNTERSCHRIFTEN ---
st.markdown('<p class="sub-header">5. Unterschriften</p>', unsafe_allow_html=True)
st.write("Bitte hier im Feld digital unterschreiben:")

col_sig1, col_sig2 = st.columns(2)

with col_sig1:
    st.write("**Vermieter (KARE-Immobilien)**")
    canvas_vermieter = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#f8f9fa",
        height=150,
        width=300,
        drawing_mode="freedraw",
        key="canvas_vermieter",
        return_image_data=True,
    )

with col_sig2:
    st.write("**Mieter**")
    canvas_mieter = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#f8f9fa",
        height=150,
        width=300,
        drawing_mode="freedraw",
        key="canvas_mieter",
        return_image_data=True,
    )

st.write("---")

# --- PDF GENERIERUNGS-KLASSE ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 8, 'KARE-Immobilien - Wohnungsabnahmeprotokoll', 0, 1, 'L')
        self.set_font('Arial', '', 9)
        self.cell(0, 5, 'Talstr. 32, 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de', 0, 1, 'L')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Seite {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 6, title, 0, 1, 'L', fill=True)
        self.ln(2)


# --- PDF GENERIERUNG BEI KLICK ---
if st.button("Wohnungsabnahmeprotokoll als PDF generieren", type="primary"):
    # Alte temporäre Dateien bereinigen
    for f in st.session_state.temp_files:
        try:
            os.remove(f)
        except:
            pass
    st.session_state.temp_files = []

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font('Arial', '', 10)

    # Objektdaten
    pdf.chapter_title("1. Objektdaten & Beteiligte")
    pdf.cell(50, 6, "Objektadresse:", 0, 0)
    pdf.cell(0, 6, f"{strasse}, {plz_ort} ({wohnungseinheit})", 0, 1)
    pdf.cell(50, 6, "Anlass / Art:", 0, 0)
    pdf.cell(0, 6, uebergabe_art, 0, 1)
    pdf.cell(50, 6, "Datum:", 0, 0)
    pdf.cell(0, 6, erstellungs_datum.strftime("%d.%m.%Y"), 0, 1)
    pdf.cell(50, 6, "Vermieter:", 0, 0)
    pdf.cell(0, 6, vermieter_name, 0, 1)
    pdf.cell(50, 6, "Mieter:", 0, 0)
    pdf.cell(0, 6, mieter_name, 0, 1)
    pdf.cell(50, 6, "Schlüsselanzahl:", 0, 0)
    pdf.cell(0, 6, f"{schluessel_anzahl} Stk.", 0, 1)
    pdf.ln(4)

    # Zählerstände
    pdf.chapter_title("2. Zählerstände")
    pdf.cell(60, 6, "Kaltwasserzähler:", 0, 0)
    pdf.cell(0, 6, f"{zaehler_kalt} m³", 0, 1)
    pdf.cell(60, 6, "Warmwasserzähler:", 0, 0)
    pdf.cell(0, 6, f"{zaehler_warm} m³", 0, 1)
    pdf.cell(60, 6, "Heizung - Wohnzimmer:", 0, 0)
    pdf.cell(0, 6, hz_wohnen, 0, 1)
    pdf.cell(60, 6, "Heizung - Kinderzimmer:", 0, 0)
    pdf.cell(0, 6, hz_kind, 0, 1)
    pdf.cell(60, 6, "Heizung - Flur:", 0, 0)
    pdf.cell(0, 6, hz_flur, 0, 1)
    pdf.cell(60, 6, "Heizung - Bad:", 0, 0)
    pdf.cell(0, 6, hz_bad, 0, 1)
    pdf.cell(60, 6, "Heizung - Küche:", 0, 0)
    pdf.cell(0, 6, hz_kuche, 0, 1)
    pdf.ln(4)

    # Mängel
    pdf.chapter_title("3. Mängel & Zustand")
    pdf.multi_cell(0, 5, maengel_text)
    pdf.ln(4)

    # Fotos einbinden falls vorhanden
    if uploaded_photos:
        pdf.chapter_title("4. Fotodokumentation")
        for uploaded_file in uploaded_photos:
            try:
                img = Image.open(uploaded_file)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
                    img.convert("RGB").save(tmp_img.name, "JPEG")
                    st.session_state.temp_files.append(tmp_img.name)
                    pdf.image(tmp_img.name, w=80)
                    pdf.ln(5)
            except Exception as e:
                pdf.cell(0, 6, f"[Fehler beim Laden des Bildes: {uploaded_file.name}]", 0, 1)

    # Unterschriften ins PDF rendern
    pdf.chapter_title("5. Unterschriften")
    pdf.ln(2)
    sig_y = pdf.get_y()

    # Vermieter Unterschrift verarbeiten
    if canvas_vermieter.image_data is not None:
        try:
            img_v = Image.fromarray(canvas_vermieter.image_data.astype("uint8"), mode="RGBA")
            bg_v = Image.new("RGBA", img_v.size, (255, 255, 255, 255))
            alpha_v = Image.alpha_composite(bg_v, img_v).convert("RGB")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_sig_v:
                alpha_v.save(tmp_sig_v.name)
                st.session_state.temp_files.append(tmp_sig_v.name)
                pdf.image(tmp_sig_v.name, x=20, y=sig_y, w=75)
        except Exception:
            pass

    # Mieter Unterschrift verarbeiten
    if canvas_mieter.image_data is not None:
        try:
            img_m = Image.fromarray(canvas_mieter.image_data.astype("uint8"), mode="RGBA")
            bg_m = Image.new("RGBA", img_m.size, (255, 255, 255, 255))
            alpha_m = Image.alpha_composite(bg_m, img_m).convert("RGB")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_sig_m:
                alpha_m.save(tmp_sig_m.name)
                st.session_state.temp_files.append(tmp_sig_m.name)
                pdf.image(tmp_sig_m.name, x=110, y=sig_y, w=75)
        except Exception:
            pass

    pdf.ln(32)
    pdf.cell(95, 6, "___________________________________", 0, 0, "L")
    pdf.cell(95, 6, "___________________________________", 0, 1, "L")
    pdf.cell(95, 6, "Vermieter (KARE-Immobilien)", 0, 0, "L")
    pdf.cell(95, 6, "Mieter", 0, 1, "L")

    # PDF speichern und Download anbieten
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf.output(tmp_pdf.name)
        st.session_state.temp_files.append(tmp_pdf.name)
        
        with open(tmp_pdf.name, "rb") as pdf_file:
            st.success("Wohnungsabnahmeprotokoll wurde erfolgreich erstellt!")
            st.download_button(
                label="📥 PDF-Protokoll herunterladen",
                data=pdf_file,
                file_name=f"Wohnungsabnahmeprotokoll_{strasse.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
