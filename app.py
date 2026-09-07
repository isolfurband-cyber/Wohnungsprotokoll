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

                self.image(temp_logo_path, x=35, y=10, w=140)
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
            {"typ": "Wasser", "bezeichnung": "Wasser Hauptzähler", "einheit": "m³"},
            {"typ": "Heizung", "bezeichnung": "Heizung", "einheit": "Einheiten"},
        ]

    with st.expander("➕ Weiteren Zähler hinzufügen"):
        z_typ = st.selectbox(
            "Zählertyp",
            ["Strom", "Wasser", "Heizung", "Gas", "Sonstige"],
            key="select_z_typ",
        )
        z_bez = st.text_input("Bezeichnung (z.B. Keller, Küche)", key="neu_zaehler_bez")
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
            z_wert = st.number_input(
                f"Zählerstand ({z['einheit']})",
                value=0.000,
                format="%.3f",
                step=0.001,
                key=f"z_wert_{i}",
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
