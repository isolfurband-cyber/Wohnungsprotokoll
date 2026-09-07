import os
import tempfile
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from fpdf import FPDF

# Seitenkonfiguration
st.set_page_config(page_title="KARE-Immobilien Abnahmeprotokoll", layout="centered")

st.title("Wohnungsabnahmeprotokoll - KARE-Immobilien")
st.markdown("**KARE-Immobilien, Talstr. 32 in 07545 Gera** | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de")

# --- Formularfelder ---
st.subheader("1. Stammdaten")
mietobjekt = st.text_input("Mietobjekt (Adresse & Details)")
mieter_name = st.text_input("Name des Mieters")
vermieter_name = st.text_input("Name des Vermieters / Vertreter", value="KARE-Immobilien")
uebergabe_datum = st.date_input("Übergabedatum")

st.subheader("2. Zählerstände")
col1, col2 = st.columns(2)
with col1:
    zaehler_kalt = st.text_input("Kaltwasserzähler (Zählernummer & Stand)")
with col2:
    zaehler_warm = st.text_input("Warmwasserzähler (Zählernummer & Stand)")

st.markdown("**Heizungszähler (Heizkostenverteiler)**")
heizung_wz = st.text_input("Wohnzimmer (Nr. / Stand)")
heizung_kz = st.text_input("Kinderzimmer (Nr. / Stand)")
heizung_flur = st.text_input("Flur (Nr. / Stand)")
heizung_bad = st.text_input("Bad (Nr. / Stand)")
heizung_kuche = st.text_input("Küche (Nr. / Stand)")

st.subheader("3. Schlüsselübergabe")
schluessel_haus = st.number_input("Haus-/Hauseingangstür", min_value=0, value=2)
schluessel_wohnung = st.number_input("Wohnungstür", min_value=0, value=3)
schluessel_keller = st.number_input("Keller", min_value=0, value=1)
schluessel_briefkasten = st.number_input("Briefkasten", min_value=0, value=1)

st.subheader("6. Unterschriften")
st.write("Bitte hier unterschreiben:")

# Canvas für die Unterschrift mit return_image_data=True
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=2,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=150,
    width=500,
    drawing_mode="freedraw",
    key="canvas_sig",
)

# PDF-Generierung Klasse
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "KARE-Immobilien - Wohnungsabnahmeprotokoll", 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "KARE-Immobilien, Talstr. 32, 07545 Gera", 0, 0, "C")

if st.button("Protokoll als PDF generieren"):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "", 10)

    # Obere Daten einfügen
    pdf.cell(0, 8, f"Objekt: {mietobjekt}", 0, 1)
    pdf.cell(0, 8, f"Mieter: {mieter_name}", 0, 1)
    pdf.cell(0, 8, f"Vermieter: {vermieter_name}", 0, 1)
    pdf.cell(0, 8, f"Datum: {uebergabe_datum.strftime('%d.%m.%Y')}", 0, 1)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Zählerstände:", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"- Kaltwasser: {zaehler_kalt}", 0, 1)
    pdf.cell(0, 6, f"- Warmwasser: {zaehler_warm}", 0, 1)
    pdf.cell(0, 6, f"- Heizung Wohnzimmer: {heizung_wz}", 0, 1)
    pdf.cell(0, 6, f"- Heizung Kinderzimmer: {heizung_kz}", 0, 1)
    pdf.cell(0, 6, f"- Heizung Flur: {heizung_flur}", 0, 1)
    pdf.cell(0, 6, f"- Heizung Bad: {heizung_bad}", 0, 1)
    pdf.cell(0, 6, f"- Heizung Küche: {heizung_kuche}", 0, 1)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Schlüssel:", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"- Haustür: {schluessel_haus} Stk.", 0, 1)
    pdf.cell(0, 6, f"- Wohnungstür: {schluessel_wohnung} Stk.", 0, 1)
    pdf.cell(0, 6, f"- Keller: {schluessel_keller} Stk.", 0, 1)
    pdf.cell(0, 6, f"- Briefkasten: {schluessel_briefkasten} Stk.", 0, 1)
    pdf.ln(10)

    # Unterschriften-Sektion
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "6. Unterschriften", 0, 1)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, "Mit ihrer Unterschrift bestätigen die Parteien die Richtigkeit der Angaben.", 0, 1)
    pdf.ln(10)

    # Unterschrift sicher verarbeiten und einbetten
    if canvas_result.image_data is not None:
        img_data = canvas_result.image_data
        # Prüfen, ob gezeichnet wurde (Alpha-Kanal Check)
        if np.any(img_data[:, :, 3] > 0):
            img = Image.fromarray(img_data.astype('uint8'), mode="RGBA")
            background = Image.new("RGBA", img.size, (255, 255, 255, 255))
            alpha_composite = Image.alpha_composite(background, img)
            signature_image = alpha_composite.convert("RGB")
            
            # Temporäre Datei für die PDF-Engine erzeugen
            sig_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
            signature_image.save(sig_path)
            
            # Bild ins PDF einfügen (X, Y, Breite)
            pdf.image(sig_path, x=10, y=pdf.get_y(), w=60)
            
            # Datei nach Nutzung aufräumen
            try:
                os.remove(sig_path)
            except:
                pass

    pdf.ln(25)
    pdf.cell(100, 6, "________________________________________", 0, 0)
    pdf.cell(0, 6, "________________________________________", 0, 1)
    pdf.cell(100, 6, "Unterschrift Vermieter (KARE-Immobilien)", 0, 0)
    pdf.cell(0, 6, "Unterschrift Mieter", 0, 1)

    # PDF-Ausgabe für Streamlit
    pdf_output = pdf.output(dest='S').encode('latin1')
    st.download_button(
        label="PDF herunterladen",
        data=pdf_output,
        file_name="Wohnungsabnahmeprotokoll_KARE.pdf",
        mime="application/pdf"
    )
