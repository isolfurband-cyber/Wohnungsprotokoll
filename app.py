from datetime import datetime
import os
from io import BytesIO
import base64
from PIL import Image
import numpy as np
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from weasyprint import HTML

st.set_page_config(
    page_title="KARE-Immobilien Handwerker- & Baustellenprotokoll",
    page_icon="🔨",
    layout="wide",
)

st.title("KARE-Immobilien – Baustellen- & Handwerkerprotokoll")
st.markdown(
    "Abnahme von Handwerkerleistungen, Baudokumentation und Erfassung von"
    " Restarbeiten oder Mängeln vor Rechnungsfreigabe."
)

with st.form("handwerker_form"):
    st.header("1. Stammdaten & Objekt")
    col1, col2 = st.columns(2)
    with col1:
        objekt_adresse = st.text_input(
            "Objektadresse / Liegenschaft", "Talstr. 32, 07545 Gera"
        )
        gewerk = st.selectbox(
            "Gewerk / Handwerksbetrieb",
            [
                "Sanitär / Heizung",
                "Elektroinstallation",
                "Maler / Tapezierer",
                "Tischler / Fenster & Türen",
                "Dachdecker / Bauklempner",
                "Fassadenbau / Wärmedämmung",
                "Bodenleger / Fliesenleger",
                "Allgemeiner Hausmeister- / Reparaturservice",
                "Sonstiges Gewerk",
            ],
        )
        handwerker_firma = st.text_input(
            "Name der Handwerksfirma / Auftragnehmer", ""
        )
    with col2:
        datum = st.date_input("Datum der Begehung / Abnahme", datetime.now())
        bearbeiter = st.text_input(
            "Abnahme durch (KARE-Immobilien)", "KARE-Immobilien"
        )
        anwesend_firma = st.text_input(
            "Anwesender Vertreter der Firma (optional)", ""
        )

    st.header("2. Leistungsumfang & Abnahmestatus")
    art_begehung = st.selectbox(
        "Art der Prüfung",
        [
            "Zwischenstand / Baustellenbegehung",
            "Mängelfeststellung",
            "Offizielle Abnahme (Werkleistung)",
            "Endabnahme nach Sanierung",
        ],
    )
    beschreibung = st.text_area(
        "Gegenstand der Arbeiten / Ausgeführte Leistungen",
        placeholder=(
            "z.B. Erneuerung der Steigleitungen im Kellergeschoss und"
            " Installation neuer Wasserzähler..."
        ),
    )

    abnahme_status = st.radio(
        "Ergebnis der Abnahme",
        [
            "Mängelfreie Abnahme (Leistung voll erbracht)",
            "Abnahme unter Vorbehalt (Mängel / Restarbeiten vorhanden)",
            "Abnahme verweigert (wesentliche Mängel)",
        ],
    )

    st.header("3. Mängel & Restarbeiten")
    maengel_text = st.text_area(
        "Festgestellte Mängel / Offene Restarbeiten (falls vorhanden)",
        placeholder=(
            "z.B. Silikonfuge im Bad beschädigt, Verkleidung sitzt nicht bündig..."
        ),
    )

    col_mass, col_frist = st.columns(2)
    with col_mass:
        massnahme = st.text_input(
            "Nacherfüllung / Vereinbarte Maßnahme",
            "Nachbesserung der aufgeführten Mängel.",
        )
    with col_frist:
        frist = st.date_input(
            "Frist zur Mängelbeseitigung", datetime.now()
        )

    st.header("4. Fotodokumentation")
    uploaded_files = st.file_uploader(
        "Fotos der Baustelle / Mängel hochladen (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )

    protokoll_bestätigt = st.checkbox(
        "Hiermit wird die sachliche Richtigkeit des Protokolls bestätigt."
    )

    submit_button = st.form_submit_button(
        label="Handwerkerprotokoll als PDF generieren"
    )

# Digitale Signaturen außerhalb des Forms mit update_streamlit=True
st.header("5. Digitale Signaturen")
col_sig_info1, col_sig_info2 = st.columns(2)
with col_sig_info1:
    st.write("**Unterschrift Handwerker / Auftragnehmer**")
    canvas_handwerker = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#f8fafc",
        height=130,
        width=350,
        drawing_mode="freedraw",
        update_streamlit=True,
        key="canvas_handwerker_protokoll",
    )
with col_sig_info2:
    st.write("**Unterschrift KARE-Immobilien**")
    canvas_kare = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#f8fafc",
        height=130,
        width=350,
        drawing_mode="freedraw",
        update_streamlit=True,
        key="canvas_kare_handwerker",
    )

if submit_button:
    if not protokoll_bestätigt:
        st.error(
            "Bitte bestätige das Protokoll über die Checkbox, bevor du das PDF"
            " generierst."
        )
    else:
        images_html = ""
        if uploaded_files:
            images_html = "<h3>Fotodokumentation</h3><div class='photo-grid'>"
            for idx, file in enumerate(uploaded_files):
                img = Image.open(file)
                if img.mode in ("RGBA", "LA") or (
                    img.mode == "P" and "transparency" in img.info
                ):
                    img = img.convert("RGB")

                buffered = BytesIO()
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                images_html += f"""
                <div class='photo-box'>
                    <img src='data:image/jpeg;base64,{img_str}' style='width:100%; max-height:180px; object-fit:cover; border-radius:4px;'/>
                    <p style='font-size:9pt; color:#555; text-align:center; margin-top:4px;'>Foto {idx+1}: {file.name}</p>
                </div>
                """
            images_html += "</div>"

        # Unterschriften zuverlässig über JSON-Objekte & Bilddaten verarbeiten
        sig_handwerker_html = "____________________________________<br>Handwerker / Auftragnehmer"
        try:
            if (
                canvas_handwerker is not None
                and isinstance(canvas_handwerker, dict)
                and "json_data" in canvas_handwerker
                and canvas_handwerker["json_data"] is not None
                and "objects" in canvas_handwerker["json_data"]
                and len(canvas_handwerker["json_data"]["objects"]) > 0
                and "image_data" in canvas_handwerker
                and canvas_handwerker["image_data"] is not None
            ):
                img_data1 = canvas_handwerker["image_data"].astype("uint8")
                pil_img1 = Image.fromarray(img_data1, mode="RGBA")
                background1 = Image.new("RGB", pil_img1.size, (255, 255, 255))
                if len(pil_img1.split()) == 4:
                    background1.paste(pil_img1, mask=pil_img1.split()[3])
                else:
                    background1.paste(pil_img1)

                sig_buf1 = BytesIO()
                background1.save(sig_buf1, format="PNG")
                sig_str1 = base64.b64encode(sig_buf1.getvalue()).decode()
                sig_handwerker_html = f"<img src='data:image/png;base64,{sig_str1}' style='max-height:60px;'/><br>____________________________________<br>Handwerker / Auftragnehmer"
        except Exception:
            pass

        sig_kare_html = "____________________________________<br>KARE-Immobilien"
        try:
            if (
                canvas_kare is not None
                and isinstance(canvas_kare, dict)
                and "json_data" in canvas_kare
                and canvas_kare["json_data"] is not None
                and "objects" in canvas_kare["json_data"]
                and len(canvas_kare["json_data"]["objects"]) > 0
                and "image_data" in canvas_kare
                and canvas_kare["image_data"] is not None
            ):
                img_data2 = canvas_kare["image_data"].astype("uint8")
                pil_img2 = Image.fromarray(img_data2, mode="RGBA")
                background2 = Image.new("RGB", pil_img2.size, (255, 255, 255))
                if len(pil_img2.split()) == 4:
                    background2.paste(pil_img2, mask=pil_img2.split()[3])
                else:
                    background2.paste(pil_img2)

                sig_buf2 = BytesIO()
                background2.save(sig_buf2, format="PNG")
                sig_str2 = base64.b64encode(sig_buf2.getvalue()).decode()
                sig_kare_html = f"<img src='data:image/png;base64,{sig_str2}' style='max-height:60px;'/><br>____________________________________<br>KARE-Immobilien"
        except Exception:
            pass

        html_content = f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 15mm;
                background-color: #ffffff;
                @bottom-right {{
                    content: "Seite " counter(page) " von " counter(pages);
                    font-size: 8pt;
                    color: #666;
                }}
                @bottom-left {{
                    content: "KARE-Immobilien · Talstr. 32 · 07545 Gera";
                    font-size: 8pt;
                    color: #666;
                }}
            }}
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #333333;
                line-height: 1.4;
                font-size: 10pt;
                margin: 0;
                padding: 0;
            }}
            .header {{
                border-bottom: 2px solid #0284c7;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .header h1 {{
                color: #0284c7;
                font-size: 20pt;
                margin: 0 0 5px 0;
            }}
            .header p {{
                margin: 0;
                color: #555;
                font-size: 9pt;
            }}
            h2 {{
                color: #0284c7;
                font-size: 12pt;
                border-bottom: 1px solid #cbd5e1;
                padding-bottom: 4px;
                margin-top: 15px;
                margin-bottom: 8px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 10px;
            }}
            th, td {{
                padding: 5px 8px;
                border: 1px solid #cbd5e1;
                vertical-align: top;
            }}
            th {{
                background-color: #f0f9ff;
                color: #0369a1;
                text-align: left;
                width: 30%;
            }}
            td {{
                width: 70%;
            }}
            .photo-grid {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 10px;
            }}
            .photo-box {{
                width: 48%;
                border: 1px solid #cbd5e1;
                padding: 5px;
                background: #f8fafc;
                margin-bottom: 10px;
                page-break-inside: avoid;
            }}
            .signature-section {{
                margin-top: 25px;
                page-break-inside: avoid;
            }}
            .sig-box {{
                width: 45%;
                display: inline-block;
                margin-top: 20px;
                text-align: center;
            }}
        </style>
        </head>
        <body>
            <div class="header">
                <h1>KARE-Immobilien</h1>
                <p>Talstr. 32, 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de</p>
                <h2 style="border:none; color:#0f172a; margin-top:10px; font-size:15pt;">Baustellen- und Handwerkerprotokoll</h2>
            </div>

            <h2>1. Stammdaten & Objekt</h2>
            <table>
                <tr><th>Objektadresse</th><td>{objekt_adresse}</td></tr>
                <tr><th>Gewerk</th><td>{gewerk}</td></tr>
                <tr><th>Handwerksfirma</th><td>{handwerker_firma} (Vertreter: {anwesend_firma})</td></tr>
                <tr><th>Datum & Art</th><td>{datum.strftime('%d.%m.%Y')} – {art_begehung}</td></tr>
                <tr><th>Abnahme durch</th><td>{bearbeiter}</td></tr>
            </table>

            <h2>2. Leistung & Abnahmestatus</h2>
            <table>
                <tr><th>Leistungsbeschreibung</th><td>{beschreibung}</td></tr>
                <tr><th>Abnahmeergebnis</th><td><b>{abnahme_status}</b></td></tr>
                <tr><th>Mängel / Restarbeiten</th><td>{maengel_text if maengel_text else "Keine Mängel festgestellt."}</td></tr>
                <tr><th>Vereinbarte Maßnahme</th><td>{massnahme}</td></tr>
                <tr><th>Frist zur Mängelbeseitigung</th><td>{frist.strftime('%d.%m.%Y')}</td></tr>
            </table>

            {images_html}

            <div class="signature-section">
                <p style="margin-bottom:15px; font-size:9pt;">Bestätigung der aufgeführten Leistungen und Mängel.</p>
                <div style="width: 100%;">
                    <div class="sig-box" style="float: left;">
                        {sig_handwerker_html}
                    </div>
                    <div class="sig-box" style="float: right;">
                        {sig_kare_html}
                    </div>
                </div>
                <div style="clear: both;"></div>
            </div>
        </body>
        </html>
        """

        pdf_path = "handwerker_protokoll.pdf"
        HTML(string=html_content).write_pdf(pdf_path)

        with open(pdf_path, "rb") as pdf_file:
            PDFbyte = pdf_file.read()

        st.success("Handwerkerprotokoll erfolgreich als PDF erstellt!")
        st.download_button(
            label="📄 Handwerkerprotokoll als PDF herunterladen",
            data=PDFbyte,
            file_name=(
                f"Handwerker_{datum.strftime('%Y%m%d')}_{gewerk.split('/')[0].strip()}.pdf"
            ),
            mime="application/octet-stream",
        )
