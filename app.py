from datetime import datetime
import os
import tempfile
from fpdf import FPDF
import numpy as np
from PIL import Image, ImageOps, ImageDraw
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# 1. Seitenkonfiguration
st.set_page_config(
    page_title="Wohnungsabnahme", page_icon="🏠", layout="centered"
)

# 2. Modernes CSS Styling einfügen
st.markdown(
    """
<style>
    /* Blendet das Streamlit-Menü und Footer aus */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Etwas weniger Abstand oben, damit es auf dem iPad besser passt */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
    }
    
    /* Primärer Button bekommt abgerundete Ecken und wirkt moderner */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        height: 3rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Hilfsfunktion für abgerundete Ecken am Logo
def add_rounded_corners(image_path, radius=20):
    img = Image.open(image_path).convert("RGBA")
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)

    rounded_img = Image.new("RGBA", img.size)
    rounded_img.paste(img, (0, 0), mask=mask)
    return rounded_img


# 3. Klasse für das PDF-Layout mit grünem Rahmen
class ModernPDF(FPDF):

    def draw_page_border(self):
        self.set_draw_color(46, 125, 50)
        self.set_line_width(0.8)
        self.rect(4, 4, 202, 289, style="D")

    def header(self):
        self.draw_page_border()

        if self.page_no() == 1:
            logo_path = "kare_logo.png"
            if os.path.exists(logo_path):
                rounded_logo = add_rounded_corners(logo_path, radius=25)
                temp_logo_path = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".png"
                ).name
                rounded_logo.save(temp_logo_path)

                self.image(temp_logo_path, x=35, y=10, w=1140)
                self.ln(38)
            else:
                self.set_font("helvetica", "B", 10)
                self.cell(0, 5, "KARE-Immobilien Protokoll", 0, 1, "L")
                self.ln(5)
        else:
            self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "", 8)
        self.set_text_color(120, 120, 120)
        self.line(14, self.get_y() - 2, 196, self.get_y() - 2)
        self.cell(
            0,
            8,
            f"Erstellt am {datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')}  -  Seite {self.page_no()}",
            0,
            0,
            "C",
        )

    def chapter_title(self, title):
        self.ln(4)
        self.set_font("helvetica", "B", 11)
        self.set_text_color(30, 41, 59)
        self.cell(0, 7, title, 0, 1, "L")
        self.set_draw_color(30, 41, 59)
        self.set_line_width(0.6)
        self.line(10, self.get_y(), 50, self.get_y())
        self.ln(4)


# --- HEADER BEREICH IN DER APP ---
logo_path = "kare_logo.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=400)
else:
    st.warning(
        "⚠️ Hinweis: Die Datei 'kare_logo.png' wurde nicht im App-Ordner gefunden."
    )
    st.markdown(
        "<h1 style='text-align: center;'>🏠 KARE-Immobilien Protokoll</h1>",
        unsafe_allow_html=True,
    )

st.write("")

# --- ABSCHNITT 0: PROTOKOLL ART ---
with st.container(border=True):
    st.subheader("📑 Art des Protokolls")
    protokoll_typ = st.radio(
        "Wähle die Art des Protokolls:",
        ["Wohnungsübergabeprotokoll", "Wohnungsabnahmeprotokoll"],
        horizontal=True,
        label_visibility="collapsed",
    )

# --- ABSCHNITT 1: STAMMDATEN ---
with st.container(border=True):
    st.subheader("👤 1. Stammdaten")
    col1, col2 = st.columns(2)
    with col1:
        wohnung = st.text_input("Adresse der Wohnung (Straße, Hausnr.)")
        ort = st.text_input("Ort, PLZ")
        mieter = st.text_input("Name des Mieters")

        mietbeginn = st.text_input(
            "Mietbeginn", placeholder="TT.MM.JJJJ", key="mietbeginn_text"
        )

        mietende = ""
        if protokoll_typ == "Wohnungsabnahmeprotokoll":
            mietende = st.text_input(
                "Mietende", placeholder="TT.MM.JJJJ", key="mietende_text"
            )

    with col2:
        vermieter = st.text_input("Name des Vermieters", value="KARE-Immobilien")
        etage = st.text_input("Etage (z.B. 2. Obergeschoss)")
        quadratmeter = st.number_input(
            "Wohnfläche (m²)", value=0.0, format="%.2f", step=1.0
        )
        datum = st.date_input(
            "Datum der Begehung/Übergabe",
            format="DD.MM.YYYY",
            key="begehung_datum",
        )

    neue_adresse_mieter = ""
    if protokoll_typ == "Wohnungsabnahmeprotokoll":
        st.write("")
        st.write("**Neue Anschrift des ausziehenden Mieters**")
        neue_adresse_mieter = st.text_area(
            "Neue Adresse (Straße, PLZ, Ort)",
            placeholder="Wird für die Kautionsrückzahlung benötigt...",
            label_visibility="collapsed",
        )

# --- ABSCHNITT 2: KAUTION & SCHLÜSSEL ---
with st.container(border=True):
    st.subheader("💶 2. Kaution & 🔑 Schlüssel")

    kaution_betrag = 0.0
    kaution_status = ""
    kaution_raten_anzahl = 0
    kaution_raten_notiz = ""
    kaution_einbehalt = ""
    kaution_einbehalt_betrag = 0.0

    if protokoll_typ == "Wohnungsübergabeprotokoll":
        col_k1, col_k2 = st.columns(2)
        with col_k1:
            kaution_betrag = st.number_input(
                "Kautionssumme (€)", value=0.00, format="%.2f", step=50.00
            )
        with col_k2:
            kaution_status = st.selectbox(
                "Status der Kaution",
                [
                    "Noch nicht gezahlt / überwiesen",
                    "Bereits gezahlt / überwiesen",
                    "Bar übergeben",
                    "Ratenzahlung",
                ],
            )

        if kaution_status == "Ratenzahlung":
            st.write("")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                kaution_raten_anzahl = st.number_input(
                    "Anzahl der Raten", min_value=1, value=3, step=1
                )
            with col_r2:
                kaution_raten_notiz = st.text_input(
                    "Details zur Ratenzahlung",
                    placeholder="z.B. jeweils zum 1. des Monats...",
                )
    else:
        st.write("🛡️ **Einbehalt der Kaution**")
        col_e1, col_e2 = st.columns([1, 2])
        with col_e1:
            kaution_einbehalt_betrag = st.number_input(
                "Einbehalt in €",
                value=0.00,
                format="%.2f",
                step=50.00,
                key="einbehalt_betrag_input",
            )
        with col_e2:
            kaution_einbehalt = st.text_input(
                "Grund / Forderungen für den Einbehalt",
                placeholder="z.B. Nachzahlung Nebenkosten, offene Reparaturen...",
                key="einbehalt_grund_input",
            )

    st.divider()
    st.write("**Übergebene Schlüssel**")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        s_wohnung = st.number_input("Wohnung", min_value=0, value=0, step=1)
        s_haustür = st.number_input("Haustür", min_value=0, value=0, step=1)
    with col_s2:
        s_zimmer = st.number_input("Zimmer", min_value=0, value=0, step=1)
        s_briefkasten = st.number_input("Briefkasten", min_value=0, value=0, step=1)
    with col_s3:
        s_keller = st.number_input("Keller", min_value=0, value=0, step=1)
        s_generalschlüssel = st.number_input(
            "Generalschlüssel", min_value=0, value=0, step=1
        )

    if "weitere_schluessel" not in st.session_state:
        st.session_state.weitere_schluessel = []

    with st.expander("➕ Weitere Schlüssel hinzufügen"):
        col_ns1, col_ns2, col_ns3 = st.columns([2, 1, 1])
        with col_ns1:
            ns_bez = st.text_input("Bezeichnung (z.B. Dachboden, Garage)")
        with col_ns2:
            ns_anzahl = st.number_input(
                "Anzahl", min_value=1, value=1, step=1, key="ns_anz"
            )
        with col_ns3:
            st.write("")
            st.write("")
            if st.button("Hinzufügen", use_container_width=True):
                if ns_bez:
                    st.session_state.weitere_schluessel.append(
                        {"bezeichnung": ns_bez, "anzahl": ns_anzahl}
                    )
                    st.rerun()

    if st.session_state.weitere_schluessel:
        for idx, item in enumerate(st.session_state.weitere_schluessel):
            col_del1, col_del2 = st.columns([4, 1])
            with col_del1:
                st.info(f"🔑 {item['bezeichnung']}: **{item['anzahl']} Stück**")
            with col_del2:
                if st.button("❌ Löschen", key=f"del_schl_{idx}"):
                    st.session_state.weitere_schluessel.pop(idx)
                    st.rerun()

# --- ABSCHNITT 3: ZÄHLERSTÄNDE ---
with st.container(border=True):
    st.subheader("⚡ 3. Zählerstände")

    if "zaehler_liste" not in st.session_state:
        st.session_state.zaehler_liste = [
            {"typ": "Strom", "bezeichnung": "Strom Hauptzähler", "einheit": "kWh"},
            {"typ": "Wasser", "bezeichnung": "Kaltwasserzähler", "einheit": "m³"},
            {"typ": "Wasser", "bezeichnung": "Warmwasserzähler", "einheit": "m³"},
            {"typ": "Heizung", "bezeichnung": "Heizung (Wohnzimmer)", "einheit": "Einheiten"},
            {"typ": "Heizung", "bezeichnung": "Heizung (Bad)", "einheit": "Einheiten"},
            {"typ": "Heizung", "bezeichnung": "Heizung (Küche)", "einheit": "Einheiten"},
            {"typ": "Heizung", "bezeichnung": "Heizung (Schlafzimmer)", "einheit": "Einheiten"},
            {"typ": "Heizung", "bezeichnung": "Heizung (Flur)", "einheit": "Einheiten"},
        ]

    with st.expander("➕ Weiteren Zähler hinzufügen"):
        z_typ = st.selectbox(
            "Zählertyp",
            ["Strom", "Wasser", "Heizung", "Gas", "Sonstige"],
            key="select_z_typ",
        )
        z_bez = st.text_input("Bezeichnung (z.B. Gäste-WC, Garage)", key="neu_zaehler_bez")
        z_einheit = st.text_input(
            "Maßeinheit (z.B. kWh, m³, Liter)", value="kWh", key="neu_zaehler_einheit"
        )
        if st.button("Zähler speichern", key="btn_add_z"):
            if z_bez:
                st.session_state.zaehler_liste.append({
                    "typ": z_typ,
                    "bezeichnung": z_bez,
                    "einheit": z_einheit,
                })
                st.rerun()

    zaehler_daten = []
    for i, z in enumerate(st.session_state.zaehler_liste):
        st.write(f"**{z['typ']}** – {z['bezeichnung']}")
        col_z1, col_z2 = st.columns(2)
        with col_z1:
            z_nr = st.text_input(
                "Zählernummer",
                key=f"z_nr_{i}",
                placeholder="Zählernummer eingeben...",
            )
        with col_z2:
            # Als Textfeld, damit exakt z.B. "0,000" oder "1234,567" ohne automatische Tausenderpunkte eingegeben werden kann
            z_wert = st.text_input(
                f"Zählerstand ({z['einheit']})",
                value="0,000",
                key=f"z_wert_{i}",
                placeholder="z.B. 1234,567",
            )

        zaehler_daten.append({
            "typ": z["typ"],
            "bezeichnung": z["bezeichnung"],
            "nummer": z_nr,
            "stand": z_wert,
            "einheit": z["einheit"],
        })
        if i < len(st.session_state.zaehler_liste) - 1:
            st.write("")

# --- ABSCHNITT 4: ZUSTAND DER RÄUME ---
with st.container(border=True):
    st.subheader("🛋️ 4. Zustand der Räume")

    if "boden_optionen" not in st.session_state:
        st.session_state.boden_optionen = [
            "Parkett",
            "Laminat",
            "Auslegware",
            "Fliesen",
            "Designbelag",
            "PVC",
            "ohne Belag",
        ]

    if "raeume_liste" not in st.session_state:
        st.session_state.raeume_liste = [
            "Flur",
            "Küche",
            "Badezimmer",
            "Wohnzimmer",
            "Schlafzimmer",
            "Keller",
            "Balkon",
            "Abstellraum",
        ]

    col_neu1, col_neu2 = st.columns([3, 1])
    with col_neu1:
        neuer_raum_name = st.text_input(
            "Neuen Raum hinzufügen",
            placeholder="z.B. Gäste-WC, Dachboden...",
            label_visibility="collapsed",
            key="neu_raum_input",
        )
    with col_neu2:
        if st.button("➕ Hinzufügen", key="btn_add_raum", use_container_width=True):
            if (
                neuer_raum_name
                and neuer_raum_name not in st.session_state.raeume_liste
            ):
                st.session_state.raeume_liste.append(neuer_raum_name)
                st.rerun()

    st.write("")
    zustaende = {}
    for raum in st.session_state.raeume_liste:
        with st.expander(f"📍 {raum}"):
            zustand = st.radio(
                f"Allgemeiner Zustand für {raum}",
                ["Einwandfrei", "Leichte Mängel", "Schwere Mängel"],
                key=f"zustand_{raum}",
                horizontal=True,
            )

            col_r1, col_r2 = st.columns(2)
            with col_r1:
                waende_dechen = st.selectbox(
                    "Wände & Decken",
                    ["gemalert (i.O.)", "nicht gemalert", "scheckig"],
                    key=f"waende_{raum}",
                )
            with col_r2:
                duebelloecher = st.number_input(
                    "Anzahl Dübellöcher",
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"duebel_{raum}",
                )

            col_r3, col_r4 = st.columns(2)
            with col_r3:
                boden_dropdown = st.selectbox(
                    "Bodenbelag",
                    st.session_state.boden_optionen,
                    key=f"boden_dropdown_{raum}",
                )
                neuer_boden = st.text_input(
                    "Neuen Bodenbelag dauerhaft hinzufügen",
                    placeholder="Eintragen & Enter drücken...",
                    key=f"neuer_boden_{raum}",
                )

                if neuer_boden and neuer_boden not in st.session_state.boden_optionen:
                    st.session_state.boden_optionen.append(neuer_boden)
                    st.rerun()

                boden_belag = (
                    neuer_boden.strip() if neuer_boden.strip() else boden_dropdown
                )

            with col_r4:
                boden_zustand = st.selectbox(
                    "Zustand Fußboden",
                    ["i.O.", "abgewohnt", "beschädigt"],
                    key=f"boden_zustand_{raum}",
                )

            fliesen_gerissen_ja = False
            fliesen_anzahl_risse = 0
            if "fliesen" in boden_belag.lower():
                st.write("🧱 **Fliesen-Prüfung**")
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    fliesen_gerissen_ja = st.checkbox(
                        "Fliesen gerissen?", key=f"fliesen_riss_{raum}"
                    )
                with col_f2:
                    if fliesen_gerissen_ja:
                        fliesen_anzahl_risse = st.number_input(
                            "Anzahl gerissener Fliesen",
                            min_value=1,
                            value=1,
                            step=1,
                            key=f"fliesen_anz_{raum}",
                        )

            schadstellen_ja = st.checkbox(
                "Allgemeine Schadstellen vorhanden", key=f"schad_ja_{raum}"
            )
            schadstellen_gr = ""
            schadstellen_beschr = ""
            if schadstellen_ja:
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    schadstellen_gr = st.text_input(
                        "Größe der Schadstelle",
                        placeholder="z.B. 5x5 cm",
                        key=f"schad_gr_{raum}",
                    )
                with col_s2:
                    schadstellen_beschr = st.text_input(
                        "Beschreibung Schadstelle",
                        placeholder="z.B. Kratzer, Riss",
                        key=f"schad_beschr_{raum}",
                    )

            kommentar = st.text_area(
                f"Allgemeine Bemerkungen zu {raum}:", key=f"kom_{raum}", height=68
            )

            fotos = st.file_uploader(
                f"Beweisfotos für {raum} anhängen (mehrere möglich)",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                key=f"foto_{raum}",
            )

            zustaende[raum] = {
                "zustand": zustand,
                "waende_dechen": waende_dechen,
                "duebelloecher": duebelloecher,
                "boden_belag": boden_belag,
                "boden_zustand":boden_zustand,
                "fliesen_gerissen_ja": fliesen_gerissen_ja,
                "fliesen_anzahl_risse": fliesen_anzahl_risse,
                "schadstellen_ja": schadstellen_ja,
                "schadstellen_gr": schadstellen_gr,
                "schadstellen_beschr": schadstellen_beschr,
                "kommentar": kommentar,
                "fotos": fotos,
            }

# --- ABSCHNITT 5: BEMERKUNGEN ---
with st.container(border=True):
    st.subheader("📝 5. Sonstige Bemerkungen")
    sonstige_bemerkungen = st.text_area(
        "Zusätzliche Vereinbarungen oder Bemerkungen",
        placeholder=(
            "z.B. Schönheitsreparaturen bis zum 15.04. vereinbart, Küche wird"
            " übernommen..."
        ),
        label_visibility="collapsed",
        height=100,
    )

# --- ABSCHNITT 6: UNTERSCHRIFTEN ---
with st.container(border=True):
    st.subheader("✍️ 6. Unterschriften")
    st.write(
        "Bitte unterschreiben Sie mit dem Finger oder einem Stift direkt im Feld."
    )

    col_sig1, col_sig2 = st.columns(2)

    with col_sig1:
        st.write("**Vermieter (KARE)**")
        canvas_vermieter = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=3,
            stroke_color="#000000",
            background_color="#f0f2f6",
            height=150,
            width=280,
            drawing_mode="freedraw",
            key="canvas_vermieter",
        )

    with col_sig2:
        st.write("**Mieter**")
        canvas_mieter = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=3,
            stroke_color="#000000",
            background_color="#f0f2f6",
            height=150,
            width=280,
            drawing_mode="freedraw",
            key="canvas_mieter",
        )

st.write("")

# --- SPEICHERN BUTTON & PDF GENERIERUNG ---
if st.button(
    "📄 Protokoll generieren & herunterladen",
    type="primary",
    use_container_width=True,
):
    if not wohnung or not mieter:
        st.error("Bitte fülle mindestens die Adresse und den Namen des Mieters aus!")
    else:
        st.success(
            "Protokoll wurde erfolgreich erstellt! Der Download startet gleich."
        )
        st.balloons()

        # PDF Erstellung starten (ModernPDF Klasse nutzen)
        pdf = ModernPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=10)

        # Dokumententitel (Groß & Modern)
        pdf.set_font("helvetica", "B", 15)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 8, protokoll_typ.upper(), 0, 1, "C")
        pdf.ln(5)

        # 1. Stammdaten
        pdf.chapter_title("1. Stammdaten")
        pdf.set_font("helvetica", size=10)
        pdf.set_text_color(51, 65, 85)

        pdf.cell(45, 6, "Objektadresse:", 0, 0)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(
            0,
            6,
            f"{wohnung.encode('latin-1', 'replace').decode('latin-1')}, {ort.encode('latin-1', 'replace').decode('latin-1')}",
            0,
            1,
        )

        pdf.set_font("helvetica", size=10)
        pdf.cell(45, 6, "Etage / Fläche:", 0, 0)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(
            0,
            6,
            f"{etage.encode('latin-1', 'replace').decode('latin-1')}  |  {quadratmeter} m²",
            0,
            1,
        )

        pdf.set_font("helvetica", size=10)
        pdf.cell(45, 6, "Mieter:", 0, 0)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 6, mieter.encode("latin-1", "replace").decode("latin-1"), 0, 1)

        pdf.set_font("helvetica", size=10)
        pdf.cell(45, 6, "Vermieter:", 0, 0)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(
            0, 6, vermieter.encode("latin-1", "replace").decode("latin-1"), 0, 1
        )

        pdf.set_font("helvetica", size=10)
        pdf.cell(45, 6, "Mietbeginn:", 0, 0)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(
            0,
            6,
            mietbeginn.encode("latin-1", "replace").decode("latin-1")
            if mietbeginn
            else "-",
            0,
            1,
        )

        if protokoll_typ == "Wohnungsabnahmeprotokoll" and mietende:
            pdf.set_font("helvetica", size=10)
            pdf.cell(45, 6, "Mietende:", 0, 0)
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(
                0,
                6,
                mietende.encode("latin-1", "replace").decode("latin-1"),
                0,
                1,
            )

        pdf.set_font("helvetica", size=10)
        pdf.cell(45, 6, "Datum der Begehung:", 0, 0)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 6, datum.strftime("%d.%m.%Y"), 0, 1)

        if protokoll_typ == "Wohnungsabnahmeprotokoll" and neue_adresse_mieter:
            pdf.set_font("helvetica", size=10)
            pdf.cell(45, 6, "Neue Anschrift Mieter:", 0, 0)
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(
                0,
                6,
                neue_adresse_mieter.encode("latin-1", "replace").decode("latin-1"),
                0,
                1,
            )
        pdf.ln(4)

        # 2. Kaution & Schlüssel
        pdf.chapter_title("2. Kaution & Schlüssel")
        pdf.set_font("helvetica", size=10)
        pdf.set_text_color(51, 65, 85)

        if protokoll_typ == "Wohnungsübergabeprotokoll":
            pdf.cell(45, 6, "Kautionssumme:", 0, 0)
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(
                0,
                6,
                f"{kaution_betrag:.2f} EUR  ({kaution_status})"
                .encode("latin-1", "replace")
                .decode("latin-1"),
                0,
                1,
            )

            if kaution_status == "Ratenzahlung":
                pdf.set_font("helvetica", size=10)
                pdf.cell(45, 6, "Ratenvereinbarung:", 0, 0)
                pdf.set_font("helvetica", "B", 10)
                raten_info = f"{kaution_raten_anzahl} Raten"
                if kaution_raten_notiz:
                    raten_info += f" ({kaution_raten_notiz})"
                pdf.cell(
                    0,
                    6,
                    raten_info.encode("latin-1", "replace").decode("latin-1"),
                    0,
                    1,
                )
        else:
            grund_text = (
                kaution_einbehalt.encode("latin-1", "replace").decode("latin-1")
                if kaution_einbehalt
                else "Keine Angabe"
            )
            pdf.cell(45, 6, "Kautions-Einbehalt:", 0, 0)
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(0, 6, f"{kaution_einbehalt_betrag:.2f} EUR", 0, 1)
            pdf.set_font("helvetica", size=10)
            pdf.cell(45, 6, "Grund:", 0, 0)
            pdf.set_font("helvetica", "I", 10)
            pdf.cell(0, 6, grund_text, 0, 1)

        pdf.ln(2)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 6, "Übergebene Schlüssel:", 0, 1)
        pdf.set_font("helvetica", size=10)
        if s_wohnung > 0:
            pdf.cell(0, 5, f"  - Wohnungsschlüssel: {s_wohnung} Stk.", 0, 1)
        if s_haustür > 0:
            pdf.cell(0, 5, f"  - Haustürschlüssel: {s_haustür} Stk.", 0, 1)
        if s_zimmer > 0:
            pdf.cell(0, 5, f"  - Zimmerschlüssel: {s_zimmer} Stk.", 0, 1)
        if s_briefkasten > 0:
            pdf.cell(0, 5, f"  - Briefkastenschlüssel: {s_briefkasten} Stk.", 0, 1)
        if s_keller > 0:
            pdf.cell(0, 5, f"  - Kellerschlüssel: {s_keller} Stk.", 0, 1)
        if s_generalschlüssel > 0:
            pdf.cell(0, 5, f"  - Generalschlüssel: {s_generalschlüssel} Stk.", 0, 1)

        for item in st.session_state.weitere_schluessel:
            pdf.cell(
                0,
                5,
                f"  - {item['bezeichnung'].encode('latin-1', 'replace').decode('latin-1')}: {item['anzahl']} Stk.",
                0,
                1,
            )
        pdf.ln(4)

        # 3. Zählerstände (direkt als Text übernommen)
        pdf.chapter_title("3. Zählerstände")
        pdf.set_font("helvetica", size=10)
        for z in zaehler_daten:
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(30, 6, f"{z['typ']}:", 0, 0)
            pdf.set_font("helvetica", size=10)
            pdf.cell(70, 6, f"{z['bezeichnung']} (Nr: {z['nummer']})", 0, 0)
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(
                0,
                6,
                f"Stand: {z['stand']} {z['einheit']}"
                .encode("latin-1", "replace")
                .decode("latin-1"),
                0,
                1,
            )
        pdf.ln(4)

        # 4. Zustand der Räume & Fotos
        pdf.chapter_title("4. Zustand der Räume und Beweisfotos")

        temp_files = []

        for raum, daten in zustaende.items():
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(30, 41, 59)
            pdf.cell(40, 6, f"- {raum}:", 0, 0)

            pdf.set_font("helvetica", "B", 10)
            if daten["zustand"] == "Einwandfrei":
                pdf.set_text_color(16, 185, 129)
            elif daten["zustand"] == "Leichte Mängel":
                pdf.set_text_color(217, 119, 6)
            else:
                pdf.set_text_color(220, 38, 38)

            pdf.cell(0, 6, daten["zustand"], 0, 1)
            pdf.set_text_color(51, 65, 85)

            pdf.set_font("helvetica", size=9)
            pdf.cell(10, 5, "", 0, 0)
            boden_text = f"Boden: {daten['boden_belag'] if daten['boden_belag'] else 'Keine Angabe'} ({daten['boden_zustand']})"
            waende_text = f"Wände/Decken: {daten['waende_dechen']} | Dübellöcher: {daten['duebelloecher']}"
            pdf.cell(
                0,
                5,
                boden_text.encode("latin-1", "replace").decode("latin-1"),
                0,
                1,
            )

            pdf.cell(10, 5, "", 0, 0)
            pdf.cell(
                0,
                5,
                waende_text.encode("latin-1", "replace").decode("latin-1"),
                0,
                1,
            )

            if daten["fliesen_gerissen_ja"]:
                pdf.cell(10, 5, "", 0, 0)
                fliesen_riss_str = (
                    f"Fliesen-Risse: Ja, Anzahl: {daten['fliesen_anzahl_risse']}"
                )
                pdf.set_text_color(220, 38, 38)
                pdf.cell(
                    0,
                    5,
                    fliesen_riss_str.encode("latin-1", "replace").decode(
                        "latin-1"
                    ),
                    0,
                    1,
                )
                pdf.set_text_color(51, 65, 85)

            if daten["schadstellen_ja"]:
                pdf.cell(10, 5, "", 0, 0)
                schad_str = f"Schadstelle: {daten['schadstellen_beschr']} (Größe: {daten['schadstellen_gr']})"
                pdf.set_text_color(220, 38, 38)
                pdf.cell(
                    0,
                    5,
                    schad_str.encode("latin-1", "replace").decode("latin-1"),
                    0,
                    1,
                )
                pdf.set_text_color(51, 65, 85)

            if daten["kommentar"]:
                pdf.set_font("helvetica", "I", 9)
                pdf.cell(10, 5, "", 0, 0)
                pdf.multi_cell(
                    0,
                    5,
                    f"Bemerkung: {daten['kommentar'].encode('latin-1', 'replace').decode('latin-1')}",
                )

            if daten["fotos"]:
                pdf.ln(2)
                start_x = 22
                start_y = pdf.get_y()
                img_width = 70
                img_gap = 6
                max_height_in_row = 0

                for idx, foto in enumerate(daten["fotos"]):
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".jpg"
                    ) as tmp_img:
                        tmp_img.write(foto.getbuffer())
                        tmp_img_path = tmp_img.name
                        temp_files.append(tmp_img_path)

                    if idx > 0 and idx % 2 == 0:
                        start_y += max_height_in_row + 4
                        start_x = 22
                        max_height_in_row = 0

                    try:
                        with Image.open(tmp_img_path) as pil_img:
                            w_orig, h_orig = pil_img.size
                            calc_height = (img_width / w_orig) * h_orig
                            if calc_height > max_height_in_row:
                                max_height_in_row = calc_height
                    except Exception:
                        calc_height = 50

                    if start_y + calc_height > 265:
                        pdf.add_page()
                        start_y = pdf.get_y() + 5
                        start_x = 22

                    try:
                        current_x = start_x + ((idx % 2) * (img_width + img_gap))
                        pdf.image(tmp_img_path, x=current_x, y=start_y, w=img_width)
                    except Exception:
                        pass

                    pdf.set_y(start_y + max_height_in_row + 5)

            pdf.ln(3)

        # 5. Sonstige Bemerkungen
        pdf.chapter_title("5. Sonstige Bemerkungen")
        pdf.set_font("helvetica", size=10)
        if sonstige_bemerkungen:
            pdf.multi_cell(
                0,
                5,
                sonstige_bemerkungen.encode("latin-1", "replace").decode(
                    "latin-1"
                ),
            )
        else:
            pdf.cell(0, 5, "Keine weiteren Bemerkungen.", 0, 1)
        pdf.ln(4)

        # 6. Unterschriften
        if pdf.get_y() > 220:
            pdf.add_page()

        pdf.chapter_title("6. Unterschriften")
        pdf.set_font("helvetica", size=9)
        pdf.set_text_color(100, 110, 120)
        pdf.cell(
            0,
            5,
            (
                "Mit ihrer Unterschrift bestätigen die Parteien die Richtigkeit der"
                " oben genannten Angaben."
            ),
            0,
            1,
        )
        pdf.ln(6)

        sig_y = pdf.get_y()

        if (
            canvas_vermieter.image_data is not None
            and canvas_vermieter.json_data["objects"]
        ):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_sig1:
                img_data = canvas_vermieter.image_data.astype(np.uint8)
                img = Image.fromarray(img_data).convert("RGBA")

                datas = img.getdata()
                new_data = []
                for item in datas:
                    if item[0] > 235 and item[1] > 235 and item[2] > 235:
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append(item)
                img.putdata(new_data)

                img.save(tmp_sig1.name, "PNG")
                tmp_sig1_path = tmp_sig1.name
                temp_files.append(tmp_sig1_path)

            pdf.image(tmp_sig1_path, x=15, y=sig_y, w=75)

        if (
            canvas_mieter.image_data is not None
            and canvas_mieter.json_data["objects"]
        ):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_sig2:
                img_data = canvas_mieter.image_data.astype(np.uint8)
                img = Image.fromarray(img_data).convert("RGBA")

                datas = img.getdata()
                new_data = []
                for item in datas:
                    if item[0] > 235 and item[1] > 235 and item[2] > 235:
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append(item)
                img.putdata(new_data)

                img.save(tmp_sig2.name, "PNG")
                tmp_sig2_path = tmp_sig2.name
                temp_files.append(tmp_sig2_path)

            pdf.image(tmp_sig2_path, x=115, y=sig_y, w=75)

        pdf.set_y(sig_y + 35)
        pdf.set_font("helvetica", size=9)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(95, 5, "___________________________________", 0, 0, "L")
        pdf.cell(95, 5, "___________________________________", 0, 1, "L")
        pdf.cell(95, 5, "Unterschrift Vermieter (KARE)", 0, 0, "L")
        pdf.cell(
            95,
            5,
            f"Unterschrift Mieter ({mieter.encode('latin-1', 'replace').decode('latin-1')})",
            0,
            1,
            "L",
        )

        # PDF Ausgabe und Download-Bereitstellung
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            pdf.output(tmp_pdf.name)
            tmp_pdf_path = tmp_pdf.name
            temp_files.append(tmp_pdf_path)

        with open(tmp_pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📥 PDF herunterladen",
                data=pdf_file,
                file_name=f"Protokoll_{mieter.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )

        # Temporäre Dateien aufräumen
        for file_path in temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
