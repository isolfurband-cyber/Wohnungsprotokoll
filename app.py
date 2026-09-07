import tempfile
from datetime import datetime
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from fpdf import FPDF


class PDF(FPDF):

    def header(self):
        # Firmenkopf KARE-Immobilien
        self.set_font("helvetica", "B", 14)
        self.set_text_color(30, 41, 59)
        self.cell(0, 8, "KARE-Immobilien", 0, 1, "L")

        self.set_font("helvetica", size=9)
        self.set_text_color(100, 110, 120)
        self.cell(
            0,
            4,
            "Talstr. 32, 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de",
            0,
            1,
            "L",
        )
        self.ln(2)

        # Trennlinie
        self.set_draw_color(203, 213, 225)
        self.set_line_width(0.5)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(6)

        # Dokumenttitel
        self.set_font("helvetica", "B", 12)
        self.set_text_color(15, 23, 42)
        self.cell(
            0, 6, "Wohnungsabnahmeprotokoll", 0, 1, "C"
        )  # Korrigierter Titel
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", size=8)
        self.set_text_color(150, 150, 150)
        self.cell(
            0,
            10,
            f"Seite {self.page_no()} von {{nb}} — KARE-Immobilien Protokollsystem",
            0,
            0,
            "C",
        )

    def chapter_title(self, title):
        self.set_font("helvetica", "B", 10)
        self.set_fill_color(241, 245, 249)
        self.set_text_color(30, 41, 59)
        self.cell(0, 6, f"  {title}", 0, 1, "L", fill=True)
        self.ln(3)


st.set_page_config(
    page_title="Wohnungsabnahmeprotokoll - KARE",
    page_icon="🏠",
    layout="centered",
)

st.title("Wohnungsabnahmeprotokoll Generator")
st.markdown("Erfassen Sie alle Daten für das Übergabeprotokoll von KARE-Immobilien.")

# --- FORMULAR-EINGABEN ---
with st.form("protocol_form"):
    st.subheader("1. Stammdaten")
    col1, col2 = st.columns(2)
    with col1:
        mietobjekt = st.text_input(
            "Mietobjekt (Adresse & Details)", "Talstr. 32, 07545 Gera"
        )
        vermieter = st.text_input("Vermieter / Vertreter", "KARE-Immobilien")
    with col2:
        mieter = st.text_input("Mieter", "Max Mustermann")
        uebergabe_datum = st.date_input(
            "Datum der Übergabe", datetime.today()
        )

    st.subheader("2. Zählerstände")
    st.markdown("Wasserzähler")
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        zähler_kalt = st.text_input(
            "Kaltwasserzähler (Nr. / Stand)", "Z-Nr: _________ | Stand: "
        )
    with col_w2:
        zähler_warm = st.text_input(
            "Warmwasserzähler (Nr. / Stand)", "Z-Nr: _________ | Stand: "
        )

    st.markdown("Heizungszähler (5 Räume)")
    heizung_raeume = ["Wohnzimmer", "Kinderzimmer", "Flur", "Bad", "Küche"]
    heizung_staende = {}
    for raum in heizung_raeume:
        heizung_staende[raum] = st.text_input(
            f"Heizungszähler {raum} (Nr. / Stand)",
            f"{raum}: _________ | Stand: ",
        )

    st.subheader("3. Schlüsselübergabe")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        schluessel_haus = st.number_input(
            "Haustürschlüssel", min_value=0, value=2
        )
        schluessel_wohnung = st.number_input(
            "Wohnungsschlüssel", min_value=0, value=3
        )
    with col_s2:
        schluessel_keller = st.number_input(
            "Keller-/Dachbodenschlüssel", min_value=0, value=1
        )
        schluessel_briefkasten = st.number_input(
            "Briefkastenschlüssel", min_value=0, value=1
        )

    st.subheader("4. Zustand & Mängel")
    zustand_allgemein = st.text_area(
        "Allgemeiner Zustand / Festgestellte Mängel",
        "Wohnung in ordnungsgemäßem Zustand. Keine wesentlichen Mängel festgestellt.",
    )

    submitted = st.form_submit_button("PDF-Protokoll generieren")

# --- UNTERSCHRIFTEN CANVAS (Außerhalb des Formulars für reaktive Canvas-Daten) ---
st.subheader("5. Digitale Unterschriften")
col_c1, col_c2 = st.columns(2)

with col_c1:
    st.markdown("**Unterschrift Vermieter (KARE)**")
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

with col_c2:
    st.markdown("**Unterschrift Mieter**")
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

# --- PDF GENERIERUNG BEI KLICK ---
if submitted:
    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.add_page()
    temp_files = []

    # 1. Stammdaten Block
    pdf.chapter_title("1. Objektdaten & Beteiligte")
    pdf.set_font("helvetica", size=9)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(
        95,
        6,
        f"Mietobjekt: {mietobjekt}",
        0,
        0,
    )
    pdf.cell(
        95,
        6,
        f"Übergabedatum: {uebergabe_datum.strftime('%d.%m.%Y')}",
        0,
        1,
    )
    pdf.cell(
        95,
        6,
        f"Vermieter: {vermieter}",
        0,
        0,
    )
    pdf.cell(
        95,
        6,
        f"Mieter: {mieter}",
        0,
        1,
    )
    pdf.ln(4)

    # 2. Zählerstände Block
    pdf.chapter_title("2. Zählerstände")
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(0, 6, "Wasser:", 0, 1)
    pdf.set_font("helvetica", size=9)
    pdf.cell(0, 5, f"- {zähler_kalt}", 0, 1)
    pdf.cell(0, 5, f"- {zähler_warm}", 0, 1)
    pdf.ln(2)

    pdf.set_font("helvetica", "B", 9)
    pdf.cell(0, 6, "Heizung:", 0, 1)
    pdf.set_font("helvetica", size=9)
    for raum, stand in heizung_staende.items():
        pdf.cell(0, 5, f"- {stand}", 0, 1)
    pdf.ln(4)

    # 3. Schlüssel Block
    pdf.chapter_title("3. Schlüsselübergabe")
    pdf.set_font("helvetica", size=9)
    pdf.cell(95, 5, f"Haustürschlüssel: {schluessel_haus}", 0, 0)
    pdf.cell(95, 5, f"Wohnungsschlüssel: {schluessel_wohnung}", 0, 1)
    pdf.cell(95, 5, f"Keller-/Dachboden: {schluessel_keller}", 0, 0)
    pdf.cell(95, 5, f"Briefkasten: {schluessel_briefkasten}", 0, 1)
    pdf.ln(4)

    # 4. Zustand Block
    pdf.chapter_title("4. Zustand der Räumlichkeiten & Mängel")
    pdf.set_font("helvetica", size=9)
    pdf.multi_cell(0, 5, zustand_allgemein)
    pdf.ln(6)

    # 5. Unterschriften-Bereich
    if pdf.get_y() > 200:
        pdf.add_page()

    pdf.chapter_title("5. Unterschriften")
    pdf.set_font("helvetica", size=9)
    pdf.set_text_color(100, 110, 120)
    pdf.cell(
        0,
        5,
        "Mit ihrer Unterschrift bestätigen die Parteien die Richtigkeit der obigen Angaben.",
        0,
        1,
    )
    pdf.ln(15)

    # Y-Position merken für die Unterschriftenlinien
    sig_y = pdf.get_y()

    # SCHRITT A: Zuerst die Linien und den Text ins PDF schreiben (Hintergrund)
    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(51, 65, 85)

    pdf.set_x(15)
    pdf.cell(90, 5, "_" * 40, 0, 0)
    pdf.set_x(110)
    pdf.cell(90, 5, "_" * 40, 0, 1)

    pdf.set_x(15)
    pdf.set_font("helvetica", size=9)
    pdf.cell(90, 5, "Unterschrift Vermieter (KARE)", 0, 0)
    pdf.set_x(110)
    pdf.cell(90, 5, "Unterschrift Mieter", 0, 1)


    # Funktion zur Bildaufbereitung & Platzierung im Vordergrund
    def add_signature_image(canvas_dict, pdf_obj, x_pos, y_pos, width):
        if (
            isinstance(canvas_dict, dict)
            and canvas_dict.get("image_data") is not None
        ):
            img_data = canvas_dict["image_data"]
            if img_data.shape[0] > 0 and img_data.shape[1] > 0:
                img = Image.fromarray(img_data.astype("uint8"), "RGBA")
                bbox = img.getbbox()
                if bbox is not None:
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])

                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".png"
                    ) as tmp:
                        background.save(tmp.name, "PNG")
                        tmp_path = tmp.name
                        temp_files.append(tmp_path)

                    canvas_w, canvas_h = img.size
                    height = (width / canvas_w) * canvas_h
                    # Bild knapp über der gezogenen Linie platzieren
                    pdf_obj.image(
                        tmp_path, x=x_pos, y=y_pos, w=width, h=height
                    )


    # SCHRITT B: Unterschriften-Bilder NACH den Linien einfügen, damit sie sichtbar bleiben
    add_signature_image(canvas_vermieter, pdf, 15, sig_y - 18, 75)
    add_signature_image(canvas_mieter, pdf, 110, sig_y - 18, 75)

    # PDF im Speicher ausgeben
    pdf_bytes = pdf.output(dest="S").encode("latin1")

    st.success("Protokoll erfolgreich erstellt!")
    st.download_button(
        label="PDF herunterladen",
        data=pdf_bytes,
        file_name=f"Wohnungsabnahmeprotokoll_{mieter.replace(' ', '_')}.pdf",
        mime="application/pdf",
    )
