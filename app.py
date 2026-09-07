import tempfile
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from fpdf import FPDF


# Custom PDF Klasse zur Definition von Kopf- und Fußzeile
class PDF(FPDF):

    def header(self):
        # Header / Logo Bereich
        self.set_font("helvetica", "B", 14)
        self.set_text_color(15, 23, 42)
        self.cell(
            0, 8, "KARE-Immobilien - Wohnungsabnahmeprotokoll", 0, 1, "L"
        )

        self.set_font("helvetica", size=9)
        self.set_text_color(100, 116, 139)
        self.cell(
            0,
            4,
            "Talstr. 32, 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de",
            0,
            1,
            "L",
        )
        self.ln(5)

        # Trennlinie
        self.set_draw_color(203, 213, 225)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        # Position am Ende der Seite
        self.set_y(-15)
        self.set_font("helvetica", size=8)
        self.set_text_color(148, 163, 184)
        self.cell(
            0,
            10,
            f"Seite {self.page_no()} | KARE-Immobilien",
            0,
            0,
            "C",
        )


st.set_page_config(
    page_title="Wohnungsabnahmeprotokoll - KARE-Immobilien", layout="centered"
)

st.title("🏡 Wohnungsabnahmeprotokoll Generator")
st.write(
    "Erfasse die Daten der Wohnungsübergabe und generiere ein sauberes PDF inklusive Unterschriften."
)

with st.form("protokoll_form"):
    st.subheader("1. Allgemeine Angaben")
    col1, col2 = st.columns(2)
    with col1:
        mieter = st.text_input("Name des Mieters", "Max Mustermann")
        objektadresse = st.text_input(
            "Objektadresse", "Musterstraße 1, 07545 Gera"
        )
    with col2:
        uebergabedatum = st.date_input("Übergabedatum")
        vermieter_vertreter = st.text_input(
            "Vertreter Vermieter", "KARE-Immobilien"
        )

    st.subheader("2. Zählerstände")
    st.markdown("**Wasserzähler**")
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        zaehler_kalt = st.text_input(
            "Kaltwasserzähler (Nummer / Stand)", "Nr. 123456 / 123.4 m³"
        )
    with col_w2:
        zaehler_warm = st.text_input(
            "Warmwasserzähler (Nummer / Stand)", "Nr. 654321 / 45.2 m³"
        )

    st.markdown("**Heizungszähler (Heizkostenverteiler)**")
    h_col1, h_col2 = st.columns(2)
    with h_col1:
        hz_wohnzimmer = st.text_input("Heizung Wohnzimmer", "Stand: 450")
        hz_kinderzimmer = st.text_input("Heizung Kinderzimmer", "Stand: 210")
        hz_flur = st.text_input("Heizung Flur", "Stand: 50")
    with h_col2:
        hz_bad = st.text_input("Heizung Bad", "Stand: 180")
        hz_kuche = st.text_input("Heizung Küche", "Stand: 120")

    st.subheader("3. Schlüsselübergabe")
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        schluessel_haustuer = st.number_input(
            "Haustürschlüssel", min_value=0, value=2
        )
    with s_col2:
        schluessel_wohnung = st.number_input(
            " Wohnungsschlüssel", min_value=0, value=3
        )
    with s_col3:
        schluessel_keller = st.number_input(
            "Keller-/Dachbodenschlüssel", min_value=0, value=1
        )

    st.subheader("4. Mängel und Zustand")
    mangel_text = st.text_area(
        "Festgestellte Mängel / Vereinbarungen",
        "Keine nennenswerten Mängel festgestellt. Die Wohnung wird in renoviertem Zustand übergeben.",
    )

    st.subheader("5. Sonstige Bemerkungen")
    bemerkungen = st.text_area("Bemerkungen", "Keine weiteren Bemerkungen.")

    st.subheader("6. Unterschriften")
    st.write(
        "Bitte unterschreibe jeweils in den Feldern. (Hinweis: Zum Speichern/Übertragen muss mindestens ein Strich gezeichnet sein)."
    )

    ucol1, ucol2 = st.columns(2)
    with ucol1:
        st.write("**Unterschrift Vermieter**")
        canvas_vermieter = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=2,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=130,
            width=250,
            drawing_mode="freedraw",
            key="canvas_vermieter",
        )

    with ucol2:
        st.write("**Unterschrift Mieter**")
        canvas_mieter = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=2,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=130,
            width=250,
            drawing_mode="freedraw",
            key="canvas_mieter",
        )

    submitted = st.form_submit_button(
        "PDF-Protokoll generieren", type="primary"
    )

if submitted:
    temp_files = []
    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Inhalt formatieren
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, "1. Allgemeine Angaben", 0, 1)

    pdf.set_font("helvetica", size=10)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(
        50,
        6,
        "Objektadresse:",
        0,
    )
    pdf.cell(0, 6, objektadresse, 0, 1)
    pdf.cell(50, 6, "Name des Mieters:", 0, 0)
    pdf.cell(0, 6, mieter, 0, 1)
    pdf.cell(50, 6, "Übergabedatum:", 0, 0)
    pdf.cell(0, 6, uebergabedatum.strftime("%d.%m.%Y"), 0, 1)
    pdf.cell(50, 6, "Vertreter Vermieter:", 0, 0)
    pdf.cell(0, 6, vermieter_vertreter, 0, 1)
    pdf.ln(4)

    # 2. Zählerstände
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, "2. Zählerstände", 0, 1)

    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 6, "Wasserzähler", 0, 1)
    pdf.set_font("helvetica", size=10)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(50, 6, "Kaltwasserzähler:", 0, 0)
    pdf.cell(0, 6, zaehler_kalt, 0, 1)
    pdf.cell(50, 6, "Warmwasserzähler:", 0, 0)
    pdf.cell(0, 6, zaehler_warm, 0, 1)
    pdf.ln(2)

    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, "Heizungszähler (Heizkostenverteiler)", 0, 1)
    pdf.set_font("helvetica", size=10)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(50, 6, "Wohnzimmer:", 0, 0)
    pdf.cell(0, 6, hz_wohnzimmer, 0, 1)
    pdf.cell(50, 6, "Kinderzimmer:", 0, 0)
    pdf.cell(0, 6, hz_kinderzimmer, 0, 1)
    pdf.cell(50, 6, "Flur:", 0, 0)
    pdf.cell(0, 6, hz_flur, 0, 1)
    pdf.cell(50, 6, "Bad:", 0, 0)
    pdf.cell(0, 6, hz_bad, 0, 1)
    pdf.cell(50, 6, "Küche:", 0, 0)
    pdf.cell(0, 6, hz_kuche, 0, 1)
    pdf.ln(4)

    # 3. Schlüsselübergabe
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, "3. Schlüsselübergabe", 0, 1)
    pdf.set_font("helvetica", size=10)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(50, 6, "Haustürschlüssel:", 0, 0)
    pdf.cell(0, 6, str(schluessel_haustuer), 0, 1)
    pdf.cell(50, 6, "Wohnungsschlüssel:", 0, 0)
    pdf.cell(0, 6, str(schluessel_wohnung), 0, 1)
    pdf.cell(50, 6, "Keller-/Dachboden:", 0, 0)
    pdf.cell(0, 6, str(schluessel_keller), 0, 1)
    pdf.ln(4)

    # 4. Mängel
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, "4. Mängel und Zustand", 0, 1)
    pdf.set_font("helvetica", size=10)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(0, 6, mangel_text)
    pdf.ln(4)

    # 5. Bemerkungen
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, "5. Sonstige Bemerkungen", 0, 1)
    pdf.set_font("helvetica", size=10)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(0, 6, bemerkungen)
    pdf.ln(6)

    # 6. Unterschriften
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, "6. Unterschriften", 0, 1)
    pdf.set_font("helvetica", size=9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(
        0, 6, "Mit Ihrer Unterschrift bestätigen die Parteien die Richtigkeit.", 0, 1
    )
    pdf.ln(15)

    line_y = pdf.get_y() + 22


    def process_signature(canvas_result, pdf_obj, x_pos, target_y, width):
        if (
            isinstance(canvas_result, dict)
            and canvas_result.get("image_data") is not None
        ):
            img_data = canvas_result["image_data"]
            if img_data is not None and img_data.size > 0:
                img_array = img_data.astype("uint8")
                pil_img = Image.fromarray(img_array, mode="RGBA")

                # Transparenz-Maske für weißen Hintergrund erzeugen
                data = np.array(pil_img)
                r, g, b = data[:, :, 0], data[:, :, 1], data[:, :, 2]
                white_areas = (r > 240) & (g > 240) & (b > 240)
                data[:, :, 3] = np.where(white_areas, 0, 255)

                processed_img = Image.fromarray(data, mode="RGBA")

                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    processed_img.save(tmp.name, "PNG")
                    tmp_path = tmp.name
                    temp_files.append(tmp_path)

                w_orig, h_orig = processed_img.size
                if w_orig > 0:
                    height = (width / w_orig) * h_orig
                    pdf_obj.image(
                        tmp_path,
                        x=x_pos,
                        y=target_y - height - 2,
                        w=width,
                        h=height,
                    )


    process_signature(canvas_vermieter, pdf, 15, line_y, 75)
    process_signature(canvas_mieter, pdf, 115, line_y, 75)

    pdf.set_y(line_y)
    pdf.set_font("helvetica", "B", 9)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(95, 5, "________________________________________", 0, 0)
    pdf.cell(95, 5, "________________________________________", 0, 1)
    pdf.set_font("helvetica", size=9)
    pdf.cell(95, 5, "Unterschrift Vermieter (KARE-Immobilien)", 0, 0)
    pdf.cell(95, 5, "Unterschrift Mieter", 0, 1)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        tmp_pdf_path = tmp_file.name

    with open(tmp_pdf_path, "rb") as f:
        pdf_bytes = f.read()

    st.success("Protokoll erfolgreich generiert!")
    st.download_button(
        label="📥 PDF Herunterladen",
        data=pdf_bytes,
        file_name=f"Protokoll_{mieter.replace(' ', '_')}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )
