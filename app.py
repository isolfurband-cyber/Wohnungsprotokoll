import os
import tempfile
from datetime import datetime
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from fpdf import FPDF

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Wohnungsabnahmeprotokoll - KARE Immobilien",
    page_icon="🏠",
    layout="wide",
)


# --- PDF KLASSE ---
class PDF(FPDF):

    def header(self):
        # Header (nur auf Seite 1)
        if self.page_no() == 1:
            self.set_font("helvetica", "B", 15)
            self.set_text_color(30, 41, 59)
            self.cell(
                0, 10, "WOHNUNGSABNAHMEPROTOKOLL", 0, 1, "C"
            )  # FPDF2 compatible
            self.set_font("helvetica", "", 9)
            self.set_text_color(100, 100, 100)
            self.cell(
                0,
                5,
                "KARE-Immobilien | Talstr. 32, 07545 Gera | Tel.: 0365 / 800 49 37",
                0,
                1,
                "C",
            )
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(
            0,
            10,
            f"Seite {self.page_no()} | KARE-Immobilien - Übergabeprotokoll",
            0,
            0,
            "C",
        )

    def chapter_title(self, title):
        self.set_font("helvetica", "B", 11)
        self.set_fill_color(240, 243, 246)
        self.set_text_color(30, 41, 59)
        self.cell(0, 7, f"  {title}", 0, 1, "L", fill=True)
        self.ln(2)


# --- UI LAYOUT ---
st.title("🏠 KARE-Immobilien: Wohnungsabnahme")
st.markdown("Erfassung des Zustands und Übergabe der Wohnung.")

# 1. Stammdaten
st.subheader("📋 1. Stammdaten & Vertragsparteien")
col1, col2 = st.columns(2)

with col1:
    wohnung = st.text_input(
        "Wohnungsanschrift / Objekt", placeholder="z.B. Talstraße 32, 07545 Gera"
    )
    vermieter = st.text_input(
        "Vermieter / Vertreter", value="KARE-Immobilien"
    )
    u_datum = st.date_input(
        "Übergabedatum", value=datetime.today()
    ).strftime("%d.%m.%Y")

with col2:
    mieter = st.text_input(
        "Name des Mieters", placeholder="Vor- und Nachname"
    )
    einzug_auszug = st.selectbox(
        "Art der Übergabe", ["Auszug (Rückgabe)", "Einzug (Übergabe)"]
    )

st.divider()

# 2. Zählerstände
st.subheader("⚡ 2. Zählerstände")
col_z1, col_z2 = st.columns(2)

with col_z1:
    z_kalt = st.text_input(
        "Kaltwasserzähler", placeholder="Zst.-Nr. / Stand (m³)"
    )
    z_warm = st.text_input(
        "Warmwasserzähler", placeholder="Zst.-Nr. / Stand (m³)"
    )

with col_z2:
    st.markdown("**Heizungszähler (5 Stück):**")
    hz_wohnen = st.text_input(
        "Wohnzimmer", placeholder="Zst.-Nr. & Stand", key="hz_wohnen"
    )
    hz_kind = st.text_input(
        "Kinderzimmer", placeholder="Zst.-Nr. & Stand", key="hz_kind"
    )
    hz_flur = st.text_input("Flur", placeholder="Zst.-Nr. & Stand", key="hz_flur")
    hz_bad = st.text_input("Bad", placeholder="Zst.-Nr. & Stand", key="hz_bad")
    hz_kueche = st.text_input(
        "Küche", placeholder="Zst.-Nr. & Stand", key="hz_kueche"
    )

st.divider()

# 3. Räume & Zustand
st.subheader("🛋️ 3. Räume & Zustand")
raeume = ["Wohnzimmer", "Kinderzimmer", "Schlafzimmer", "Küche", "Bad", "Flur"]
raum_status = {}

for raum in raeume:
    with st.expander(f"Raum: {raum}"):
        c1, c2 = st.columns([1, 2])
        with c1:
            zustand = st.selectbox(
                "Zustand", ["Einwandfrei", "Mängel vorhanden"], key=f"z_{raum}"
            )
        with c2:
            details = st.text_input(
                "Mängel / Bemerkungen",
                placeholder="z.B. Tapete beschädigt",
                key=f"d_{raum}",
            )
        raum_status[raum] = {"zustand": zustand, "details": details}

st.divider()

# 4. Schlüsselübergabe
st.subheader("🔑 4. Schlüsselübergabe")
col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    s_haustuer = st.number_input(
        "Haustürschlüssel", min_value=0, value=2, step=1
    )
with col_s2:
    s_wohnung = st.number_input(
        "Wohnungstüren", min_value=0, value=2, step=1
    )
with col_s3:
    s_keller = st.number_input(
        "Keller / Sonstige", min_value=0, value=1, step=1
    )

st.divider()

# 5. Allgemeine Mängel / Notizen
st.subheader("📝 5. Allgemeine Bemerkungen & Vereinbarungen")
bemerkungen = st.text_area(
    "Zusätzliche Vereinbarungen oder Fristen zur Mängelbeseitigung"
)

st.divider()

# 6. UNTERSCHRIFTEN
with st.container():
    st.subheader("✍️ 6. Unterschriften")
    st.write(
        "Bitte unterschreiben Sie mit dem Finger oder einem Stift direkt im Feld."
    )

    col_sig1, col_sig2 = st.columns(2)

    with col_sig1:
        st.write("**Vermieter (KARE)**")
        canvas_vermieter = st_canvas(
            fill_color="rgba(255, 255, 255, 1)",
            stroke_width=3,
            stroke_color="#000000",
            background_color="#FFFFFF",
            update_streamlit=True,
            height=130,
            width=280,
            drawing_mode="freedraw",
            key="canvas_vermieter",
        )

    with col_sig2:
        st.write("**Mieter**")
        canvas_mieter = st_canvas(
            fill_color="rgba(255, 255, 255, 1)",
            stroke_width=3,
            stroke_color="#000000",
            background_color="#FFFFFF",
            update_streamlit=True,
            height=130,
            width=280,
            drawing_mode="freedraw",
            key="canvas_mieter",
        )

st.write("")

# --- PDF GENERIERUNG & DOWNLOAD ---
if st.button(
    "📄 Protokoll generieren & herunterladen",
    type="primary",
    use_container_width=True,
):
    if not wohnung or not mieter:
        st.error(
            "Bitte fülle mindestens die Wohnungsanschrift und den Namen des Mieters aus!"
        )
    else:
        pdf = PDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()
        pdf.set_font("helvetica", size=9)

        # Stammdaten ins PDF schreiben
        pdf.chapter_title("1. Stammdaten")
        pdf.cell(
            50, 6, "Objekt / Anschrift:", 0, 0
        )  # FPDF2 signature compatible
        pdf.cell(0, 6, wohnung, 0, 1)
        pdf.cell(50, 6, "Mieter:", 0, 0)
        pdf.cell(0, 6, mieter, 0, 1)
        pdf.cell(50, 6, "Vermieter:", 0, 0)
        pdf.cell(0, 6, vermieter, 0, 1)
        pdf.cell(50, 6, "Übergabe-Art:", 0, 0)
        pdf.cell(0, 6, einzug_auszug, 0, 1)
        pdf.cell(50, 6, "Datum:", 0, 0)
        pdf.cell(0, 6, u_datum, 0, 1)
        pdf.ln(3)

        # Zählerstände
        pdf.chapter_title("2. Zählerstände")
        pdf.cell(50, 6, "Kaltwasserzähler:", 0, 0)
        pdf.cell(0, 6, z_kalt or "Keine Angabe", 0, 1)
        pdf.cell(50, 6, "Warmwasserzähler:", 0, 0)
        pdf.cell(0, 6, z_warm or "Keine Angabe", 0, 1)
        pdf.cell(50, 6, "Heizung Wohnzimmer:", 0, 0)
        pdf.cell(0, 6, hz_wohnen or "-", 0, 1)
        pdf.cell(50, 6, "Heizung Kinderzimmer:", 0, 0)
        pdf.cell(0, 6, hz_kind or "-", 0, 1)
        pdf.cell(50, 6, "Heizung Flur:", 0, 0)
        pdf.cell(0, 6, hz_flur or "-", 0, 1)
        pdf.cell(50, 6, "Heizung Bad:", 0, 0)
        pdf.cell(0, 6, hz_bad or "-", 0, 1)
        pdf.cell(50, 6, "Heizung Küche:", 0, 0)
        pdf.cell(0, 6, hz_kueche or "-", 0, 1)
        pdf.ln(3)

        # Räume & Zustand
        pdf.chapter_title("3. Zustand der Räume")
        for raum, daten in raum_status.items():
            status_text = (
                f"{daten['zustand']}"
                + (
                    f" – Bemerkung: {daten['details']}"
                    if daten["details"]
                    else ""
                )
            )
            pdf.cell(45, 6, f"{raum}:", 0, 0)
            pdf.cell(0, 6, status_text, 0, 1)
        pdf.ln(3)

        # Schlüssel
        pdf.chapter_title("4. Schlüsselübergabe")
        pdf.cell(50, 6, "Haustürschlüssel:", 0, 0)
        pdf.cell(0, 6, str(s_haustuer), 0, 1)
        pdf.cell(50, 6, "Wohnungstürschlüssel:", 0, 0)
        pdf.cell(0, 6, str(s_wohnung), 0, 1)
        pdf.cell(50, 6, "Keller / Sonstige:", 0, 0)
        pdf.cell(0, 6, str(s_keller), 0, 1)
        pdf.ln(3)

        # Bemerkungen
        if bemerkungen.strip():
            pdf.chapter_title("5. Allgemeine Bemerkungen")
            pdf.multi_cell(0, 6, bemerkungen)
            pdf.ln(3)

        # Prüfen ob wir für die Unterschriften eine neue Seite brauchen
        if pdf.get_y() > 220:
            pdf.add_page()

        # 6. Unterschriften aufs PDF drucken
        pdf.chapter_title("6. Unterschriften")
        pdf.ln(2)
        pdf.set_font("helvetica", "", 8)
        pdf.multi_cell(
            0,
            4,
            "Mit den nachfolgenden Unterschriften wird der oben genannte Zustand der Räume und die ordnungsgemäße Übergabe bestätigt.",
        )
        pdf.ln(4)

        sig_y = pdf.get_y()

        # Boxen zeichnen
        pdf.set_xy(15, sig_y)
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(85, 6, "Vermieter (KARE-Immobilien)", 0, 1, "L")
        pdf.rect(15, sig_y + 6, 85, 28)

        pdf.set_xy(110, sig_y)
        pdf.cell(85, 6, "Mieter", 0, 1, "L")
        pdf.rect(110, sig_y + 6, 85, 28)

        temp_files = []

        # Vermieter-Unterschrift verarbeiten
        if (
            canvas_vermieter.image_data is not None
            and canvas_vermieter.image_data.size > 0
        ):
            img_data_v = canvas_vermieter.image_data
            if np.any(img_data_v[:, :, :3] < 255):
                img_v = Image.fromarray(
                    img_data_v.astype("uint8"), mode="RGBA"
                ).convert("RGB")
                v_path = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".png"
                ).name
                img_v.save(v_path, "PNG")
                temp_files.append(v_path)
                pdf.image(v_path, x=16, y=sig_y + 7, w=83, h=26)

        # Mieter-Unterschrift verarbeiten
        if (
            canvas_mieter.image_data is not None
            and canvas_mieter.image_data.size > 0
        ):
            img_data_m = canvas_mieter.image_data
            if np.any(img_data_m[:, :, :3] < 255):
                img_m = Image.fromarray(
                    img_data_m.astype("uint8"), mode="RGBA"
                ).convert("RGB")
                m_path = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".png"
                ).name
                img_m.save(m_path, "PNG")
                temp_files.append(m_path)
                pdf.image(m_path, x=111, y=sig_y + 7, w=83, h=26)

        # PDF Datei erzeugen und Download bereitstellen
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            pdf.output(tmp_pdf.name)
            with open(tmp_pdf.name, "rb") as f:
                st.success(
                    "Protokoll wurde erfolgreich erstellt! Klicke unten zum Download."
                )
                st.download_button(
                    label="📥 PDF-Protokoll herunterladen",
                    data=f,
                    file_name=f"Wohnungsprotokoll_{mieter.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

        # Cleanup temporäre Bilddateien
        for tf in temp_files:
            if os.path.exists(tf):
                try:
                    os.remove(tf)
                except:
                    pass
