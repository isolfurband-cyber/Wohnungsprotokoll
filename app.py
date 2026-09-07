import streamlit as st
from streamlit_drawable_canvas import st_canvas
from fpdf import FPDF
from PIL import Image
import tempfile
import os
import base64
import io

st.set_page_config(page_title="Wohnungsabnahmeprotokoll - KARE-Immobilien", layout="centered")

class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 12)
        self.set_text_color(30, 41, 59)
        self.cell(0, 6, "KARE-Immobilien - Wohnungsabnahmeprotokoll", 0, 1, "L")
        self.set_font("helvetica", size=8)
        self.set_text_color(100, 110, 120)
        self.cell(0, 4, "Talstr. 32, 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de", 0, 1, "L")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", size=8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Seite {self.page_no()}", 0, 0, "C")

    def chapter_title(self, title):
        self.set_font("helvetica", "B", 10)
        self.set_text_color(30, 41, 59)
        self.cell(0, 6, title, 0, 1, "L")
        self.ln(2)

st.title("🏠 Wohnungsabnahmeprotokoll")
st.subheader("KARE-Immobilien")

# Stammdaten & Zähler Eingaben
with st.form("protocol_form"):
    st.markdown("### 1. Stammdaten")
    col1, col2 = st.columns(2)
    with col1:
        mietobjekt = st.text_input("Mietobjekt (Adresse)", "Beispielstraße 1, 07545 Gera")
        mieter_name = st.text_input("Name des Mieters", "Max Mustermann")
    with col2:
        vermieter_name = st.text_input("Vermieter / Vertreter", "KARE-Immobilien")
        uebergabe_datum = st.date_input("Übergabedatum")

    st.markdown("### 2. Zählerstände")
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        zähler_kalt = st.text_input("Kaltwasserzähler (Zähler-Nr. / Stand)", "Zähler 1 / Stand: ")
    with col_w2:
        zähler_warm = st.text_input("Warmwasserzähler (Zähler-Nr. / Stand)", "Zähler 2 / Stand: ")

    st.markdown("Heizungszähler:")
    heiz_wz = st.text_input("Heizungszähler Wohnzimmer", "Stand: ")
    heiz_kz = st.text_input("Heizungszähler Kinderzimmer", "Stand: ")
    heiz_fl = st.text_input("Heizungszähler Flur", "Stand: ")
    heiz_ba = st.text_input("Heizungszähler Bad", "Stand: ")
    heiz_ku = st.text_input("Heizungszähler Küche", "Stand: ")

    st.markdown("### 3. Mängel & Bemerkungen")
    bemerkungen = st.text_area("Bemerkungen / Vereinbarungen", "Z.B. Schönheitsreparaturen bis zum 15.04. vereinbart...")

    submitted = st.form_submit_button("Formular-Daten zwischenspeichern")

st.markdown("---")
st.markdown("### ✍️ 6. Unterschriften")
st.markdown("Bitte unterschreiben Sie mit dem Finger oder der Maus in das Feld.")

col_s1, col_s2 = st.columns(2)
with col_s1:
    st.write("Vermieter (KARE)")
    canvas_vermieter = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=150,
        width=300,
        drawing_mode="freedraw",
        key="canvas_vermieter",
    )
with col_s2:
    st.write("Mieter")
    canvas_mieter = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=150,
        width=300,
        drawing_mode="freedraw",
        key="canvas_mieter",
    )

if st.button("Protokoll generieren & herunterladen", type="primary"):
    pdf = PDF()
    pdf.add_page()
    temp_files = []

    # 1. Stammdaten
    pdf.chapter_title("1. Stammdaten")
    pdf.set_font("helvetica", size=9)
    pdf.cell(50, 6, "Mietobjekt:", 0, 0)
    pdf.cell(0, 6, mietobjekt, 0, 1)
    pdf.cell(50, 6, "Mieter:", 0, 0)
    pdf.cell(0, 6, mieter_name, 0, 1)
    pdf.cell(50, 6, "Vermieter:", 0, 0)
    pdf.cell(0, 6, vermieter_name, 0, 1)
    pdf.cell(50, 6, "Datum:", 0, 0)
    pdf.cell(0, 6, str(uebergabe_datum), 0, 1)
    pdf.ln(5)

    # 2. Zählerstände
    pdf.chapter_title("2. Zählerstände")
    pdf.cell(50, 6, "Kaltwasserzähler:", 0, 0)
    pdf.cell(0, 6, zähler_kalt, 0, 1)
    pdf.cell(50, 6, "Warmwasserzähler:", 0, 0)
    pdf.cell(0, 6, zähler_warm, 0, 1)
    pdf.cell(50, 6, "Heizung Wohnzimmer:", 0, 0)
    pdf.cell(0, 6, heiz_wz, 0, 1)
    pdf.cell(50, 6, "Heizung Kinderzimmer:", 0, 0)
    pdf.cell(0, 6, heiz_kz, 0, 1)
    pdf.cell(50, 6, "Heizung Flur:", 0, 0)
    pdf.cell(0, 6, heiz_fl, 0, 1)
    pdf.cell(50, 6, "Heizung Bad:", 0, 0)
    pdf.cell(0, 6, heiz_ba, 0, 1)
    pdf.cell(50, 6, "Heizung Küche:", 0, 0)
    pdf.cell(0, 6, heiz_ku, 0, 1)
    pdf.ln(5)

    # 3. Bemerkungen
    pdf.chapter_title("3. Bemerkungen & Vereinbarungen")
    pdf.set_font("helvetica", size=9)
    pdf.multi_cell(0, 6, bemerkungen)
    pdf.ln(10)

    # 6. Unterschriften
    if pdf.get_y() > 210:
        pdf.add_page()

    pdf.chapter_title("6. Unterschriften")
    pdf.set_font("helvetica", size=9)
    pdf.set_text_color(100, 110, 120)
    pdf.cell(
        0,
        5,
        "Mit ihrer Unterschrift bestätigen die Parteien die Richtigkeit der oben genannten Angaben.",
        0,
        1,
    )
    pdf.ln(12)

    sig_y = pdf.get_y()

    def process_signature(canvas_result, pdf_obj, x_pos, y_pos, width):
        if isinstance(canvas_result, dict) and canvas_result.get("data_url") is not None:
            data_url = canvas_result["data_url"]
            if "," in data_url:
                header, encoded = data_url.split(",", 1)
                binary_data = base64.b64decode(encoded)
                
                pil_img = Image.open(io.BytesIO(binary_data))
                
                if pil_img.mode == "RGBA":
                    alpha = pil_img.split()[3]
                    has_drawing = any(pixel > 0 for pixel in alpha.getdata())
                else:
                    has_drawing = True

                if has_drawing:
                    background = Image.new("RGB", pil_img.size, (255, 255, 255))
                    if pil_img.mode == "RGBA":
                        background.paste(pil_img, mask=pil_img.split()[3])
                    else:
                        background.paste(pil_img)

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        background.save(tmp.name, "PNG")
                        tmp_path = tmp.name
                        temp_files.append(tmp_path)

                    w_orig, h_orig = background.size
                    if w_orig > 0:
                        height = (width / w_orig) * h_orig
                        pdf_obj.image(
                            tmp_path,
                            x=x_pos,
                            y=y_pos - height + 2,
                            w=width,
                            h=height,
                        )

    process_signature(canvas_vermieter, pdf, 15, sig_y, 75)
    process_signature(canvas_mieter, pdf, 115, sig_y, 75)

    pdf.set_y(sig_y + 8)
    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(95, 5, "________________________________________", 0, 0)
    pdf.cell(95, 5, "________________________________________", 0, 1)
    pdf.set_font("helvetica", size=9)
    pdf.cell(95, 5, "Unterschrift Vermieter (KARE-Immobilien)", 0, 0)
    pdf.cell(95, 5, "Unterschrift Mieter", 0, 1)

    # Output PDF as bytes
    pdf_output = pdf.output(dest='S')
    if isinstance(pdf_output, str):
        pdf_output = pdf_output.encode('latin1')

    st.success("Protokoll wurde erfolgreich erstellt!")
    st.download_button(
        label="📄 PDF herunterladen",
        data=pdf_output,
        file_name="Wohnungsabnahmeprotokoll.pdf",
        mime="application/pdf",
    )

    # Aufräumen von temporären Dateien
    for path in temp_files:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
