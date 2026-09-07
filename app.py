import os
import tempfile
from datetime import date
from fpdf import FPDF
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# --- SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="KARE-Immobilien Protokoll-Manager",
    page_icon="🏠",
    layout="wide",
)


# --- FPDF KLASSE MIT HEADER & FOOTER ---
class ModernPDF(FPDF):

    def header(self):
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 25, "F")

        self.set_font("helvetica", "B", 12)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 6)
        self.cell(
            0,
            6,
            "KARE-Immobilien  |  Wohnungs- & Übergabeprotokoll",
            0,
            0,
            "L",
        )

        self.set_font("helvetica", "", 8)
        self.set_xy(10, 13)
        self.cell(
            0,
            5,
            "Talstr. 32, 07545 Gera  |  Tel.: 0365 / 800 49 37  |  E-Mail: Info@KARE-Immobilien.de",
            0,
            0,
            "L",
        )
        self.ln(22)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(
            0,
            10,
            f"Seite {self.page_no()}/{{nb}} - KARE-Immobilien Gera",
            0,
            0,
            "C",
        )

    def chapter_title(self, title):
        self.set_font("helvetica", "B", 11)
        self.set_text_color(15, 23, 42)
        self.set_fill_color(241, 245, 249)
        self.cell(0, 7, f"  {title}", 0, 1, "L", 1)
        self.ln(3)


# --- SEITEN-TITEL ---
st.title("🏠 KARE-Immobilien Protokoll-Generator")
st.markdown(
    "Erstellung von Übergabe- und Abnahmeprotokollen inklusive Zählern, Raumzuständen, Fotos und digitaler Unterschrift."
)
st.markdown("---")

protokoll_typ = st.selectbox(
    "Protokoll-Art auswählen:",
    ["Wohnungsübergabeprotokoll", "Wohnungsabnahmeprotokoll"],
)

# --- SESSION STATE INITIALISIERUNG ---
if "weitere_schluessel" not in st.session_state:
    st.session_state.weitere_schluessel = []

default_zaehler = [
    {
        "typ": "Strom",
        "bezeichnung": "Hauptzähler",
        "nummer": "",
        "stand": 0.0,
        "einheit": "kWh",
    },
    {
        "typ": "Kaltwasser",
        "bezeichnung": "Wohnung",
        "nummer": "",
        "stand": 0.0,
        "einheit": "m³",
    },
    {
        "typ": "Warmwasser",
        "bezeichnung": "Wohnung",
        "nummer": "",
        "stand": 0.0,
        "einheit": "m³",
    },
    {
        "typ": "Heizung",
        "bezeichnung": "Wohnzimmer",
        "nummer": "",
        "stand": 0.0,
        "einheit": "Units",
    },
    {
        "typ": "Heizung",
        "bezeichnung": "Kinderzimmer",
        "nummer": "",
        "stand": 0.0,
        "einheit": "Units",
    },
    {
        "typ": "Heizung",
        "bezeichnung": "Flur",
        "nummer": "",
        "stand": 0.0,
        "einheit": "Units",
    },
    {
        "typ": "Heizung",
        "bezeichnung": "Bad",
        "nummer": "",
        "stand": 0.0,
        "einheit": "Units",
    },
    {
        "typ": "Heizung",
        "bezeichnung": "Küche",
        "nummer": "",
        "stand": 0.0,
        "einheit": "Units",
    },
]

if "zaehler_liste" not in st.session_state:
    st.session_state.zaehler_liste = default_zaehler
else:
    for z in st.session_state.zaehler_liste:
        if "nummer" not in z:
            z["nummer"] = ""
        if "stand" not in z:
            z["stand"] = 0.0
        if "typ" not in z:
            z["typ"] = "Strom"
        if "bezeichnung" not in z:
            z["bezeichnung"] = ""
        if "einheit" not in z:
            z["einheit"] = "Units"

# --- ABSCHNITT 1: STAMMDATEN ---
with st.container():
    st.subheader("📋 1. Stammdaten")
    col1, col2 = st.columns(2)

    with col1:
        wohnung = st.text_input("Objektadresse (Straße & Hausnummer)", "Talstr. 32")
        ort = st.text_input("PLZ und Ort", "07545 Gera")
        etage = st.text_input("Etage / Lage", "2. Obergeschoss links")
        quadratmeter = st.number_input(
            "Wohnfläche (m²)", min_value=1.0, max_value=500.0, value=65.0
        )
        vermieter = st.text_input(
            "Vermieter / Vertreter", "KARE-Immobilien (Hausverwaltung)"
        )

    with col2:
        mieter = st.text_input("Mieter (Name / Namen)", "")
        mietbeginn = st.date_input("Mietbeginn", date.today())

        if protokoll_typ == "Wohnungsabnahmeprotokoll":
            mietende = st.date_input("Mietende", date.today())
            neue_adresse_mieter = st.text_input(
                "Neue Anschrift des Mieters (optional)", ""
            )
        else:
            mietende = None
            neue_adresse_mieter = ""

        datum = st.date_input("Datum der Begehung", date.today())

st.markdown("---")

# --- ABSCHNITT 2: KAUTION & SCHLÜSSEL ---
with st.container():
    st.subheader("🔑 2. Kaution & Schlüssel")
    col_k1, col_k2 = st.columns(2)

    if protokoll_typ == "Wohnungsübergabeprotokoll":
        with col_k1:
            kaution_betrag = st.number_input(
                "Kautionssumme (€)", min_value=0.0, value=1200.0, step=50.0
            )
        with col_k2:
            kaution_status = st.selectbox(
                "Status der Kaution",
                [
                    "Bereits vollständig gezahlt",
                    "Wird in Raten gezahlt",
                    "Überweisung steht aus",
                ],
            )
            kaution_raten_notiz = ""
            kaution_raten_anzahl = 1
            if kaution_status == "Wird in Raten gezahlt":
                kaution_raten_anzahl = st.number_input(
                    "Anzahl der Raten", min_value=1, max_value=6, value=3
                )
                kaution_raten_notiz = st.text_input(
                    "Details zur Ratenzahlung",
                    "3 monatige Raten à 400 EUR ab Mietbeginn",
                )
        kaution_einbehalt = ""
        kaution_einbehalt_betrag = 0.0
    else:
        with col_k1:
            kaution_einbehalt_betrag = st.number_input(
                "Einbehalt von der Kaution (€)",
                min_value=0.0,
                value=0.0,
                step=50.0,
            )
        with col_k2:
            kaution_einbehalt = st.text_area(
                "Grund für Kautions-Einbehalt (Schäden, Nachzahlungen etc.)",
                "",
            )
        kaution_betrag = 0.0
        kaution_status = ""

    st.markdown("#### Übergabe der Schlüssel")
    c_s1, c_s2, c_s3, c_s4, c_s5 = st.columns(5)
    with c_s1:
        s_wohnung = st.number_input("Wohnung", min_value=0, value=2)
    with c_s2:
        s_haustür = st.number_input("Haustür", min_value=0, value=2)
    with c_s3:
        s_zimmer = st.number_input("Zimmer", min_value=0, value=0)
    with c_s4:
        s_briefkasten = st.number_input("Briefkasten", min_value=0, value=1)
    with c_s5:
        s_keller = st.number_input("Keller", min_value=0, value=1)

    st.write("**Weitere Schlüssel / Transponder:**")
    for idx, item in enumerate(st.session_state.weitere_schluessel):
        col_del1, col_del2 = st.columns([4, 1])
        with col_del1:
            st.text(f"- {item['bezeichnung']}: {item['anzahl']} Stk.")
        with col_del2:
            if st.button("Löschen", key=f"del_key_{idx}"):
                st.session_state.weitere_schluessel.pop(idx)
                st.rerun()

    with st.form("neuer_schluessel_form", clear_on_submit=True):
        col_ns1, col_ns2, col_ns3 = st.columns([3, 1, 1])
        with col_ns1:
            ns_bez = st.text_input(
                "Bezeichnung (z.B. Dachboden, Garage)", key="ns_bez"
            )
        with col_ns2:
            ns_anz = st.number_input(
                "Anzahl", min_value=1, value=1, key="ns_anz"
            )
        with col_ns3:
            st.text("")
            st.text("")
            add_key_btn = st.form_submit_button("Hinzufügen")
        if add_key_btn and ns_bez:
            st.session_state.weitere_schluessel.append(
                {"bezeichnung": ns_bez, "anzahl": ns_anz}
            )
            st.rerun()

st.markdown("---")

# --- ABSCHNITT 3: ZÄHLERSTÄNDE ---
with st.container():
    st.subheader("⚡ 3. Zählerstände")
    st.write(
        "Passe die Zählerstände an oder füge bei Bedarf weitere Zähler hinzu."
    )

    zaehler_daten = []
    for idx, z in enumerate(st.session_state.zaehler_liste):
        col_z1, col_z2, col_z3, col_z4 = st.columns([2, 2, 2, 1])
        with col_z1:
            z_typ = st.selectbox(
                "Art",
                ["Strom", "Kaltwasser", "Warmwasser", "Heizung", "Gas"],
                index=(
                    [
                        "Strom",
                        "Kaltwasser",
                        "Warmwasser",
                        "Heizung",
                        "Gas",
                    ].index(z.get("typ", "Strom"))
                    if z.get("typ", "Strom")
                    in ["Strom", "Kaltwasser", "Warmwasser", "Heizung", "Gas"]
                    else 0
                ),
                key=f"zt_{idx}",
            )
        with col_z2:
            z_bez = st.text_input(
                "Ort / Bezeichnung", value=z.get("bezeichnung", ""), key=f"zb_{idx}"
            )
        with col_z3:
            z_nr = st.text_input(
                "Zählernummer", value=z.get("nummer", ""), key=f"zn_{idx}"
            )
        with col_z4:
            z_stand = st.number_input(
                f"Stand ({z.get('einheit', 'Units')})",
                value=float(z.get("stand", 0.0)),
                format="%.3f",
                key=f"zs_{idx}",
            )

        zaehler_daten.append(
            {
                "typ": z_typ,
                "bezeichnung": z_bez,
                "nummer": z_nr,
                "stand": z_stand,
                "einheit": z.get("einheit", "Units"),
            }
        )

st.markdown("---")

# --- ABSCHNITT 4: ZUSTAND DER RÄUME ---
with st.container():
    st.subheader("🏡 4. Zustand der Räume und Beweisfotos")

    raeume_liste = [
        "Flur / Diele",
        "Wohnzimmer",
        "Schlafzimmer",
        "Kinderzimmer",
        "Küche",
        "Badezimmer",
        "Keller / Abstellraum",
    ]
    zustaende = {}

    for raum in raeume_liste:
        with st.expander(f"Zustand: {raum}", expanded=(raum == "Flur / Diele")):
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                zustand = st.selectbox(
                    "Allgemeiner Zustand",
                    ["Einwandfrei", "Leichte Mängel", "Erhebliche Mängel"],
                    key=f"zustand_{raum}",
                )
                boden_belag = st.selectbox(
                    "Bodenbelag",
                    ["Parkett", "Laminat", "Fliesen", "Vinyl", "Teppich", "Sonstiges"],
                    key=f"boden_{raum}",
                )
                boden_zustand = st.selectbox(
                    "Zustand Boden",
                    ["Unbeschädigt", "Kratzer / Abnutzung", "Beschädigt"],
                    key=f"boden_zustand_{raum}",
                )

            with col_r2:
                waende_dechen = st.selectbox(
                    "Wände / Decken",
                    [
                        "Frisch gestrichen",
                        "Normaler Zustand",
                        "Renovierungsbedürftig",
                    ],
                    key=f"waende_{raum}",
                )
                duebelloecher = st.selectbox(
                    "Dübellöcher / Bohrungen",
                    ["Keine", "Fachmännisch verschlossen", "Offen / Sichtbar"],
                    key=f"duebel_{raum}",
                )

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                fliesen_gerissen_ja = st.checkbox(
                    "Risse in Fliesen vorhanden?", key=f"fliesen_{raum}"
                )
                fliesen_anzahl_risse = 0
                if fliesen_gerissen_ja:
                    fliesen_anzahl_risse = st.number_input(
                        "Anzahl beschädigter Fliesen",
                        min_value=1,
                        value=1,
                        key=f"f_anz_{raum}",
                    )
            with col_m2:
                schadstellen_ja = st.checkbox(
                    "Sonstige Schadstellen (Türen, Fenster, Sanitär)?",
                    key=f"schaden_{raum}",
                )
                schadstellen_beschr = ""
                schadstellen_gr = "Klein"
                if schadstellen_ja:
                    schadstellen_beschr = st.text_input(
                        "Beschreibung des Schadens", key=f"schaden_bez_{raum}"
                    )
                    schadstellen_gr = st.selectbox(
                        "Schadensumfang",
                        ["Klein", "Mittel", "Groß"],
                        key=f"schaden_gr_{raum}",
                    )

            kommentar = st.text_area(
                f"Bemerkungen zu {raum}", key=f"kommentar_{raum}"
            )
            fotos = st.file_uploader(
                f"Beweisfotos für {raum} hochladen (max. mehrere)",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                key=f"fotos_{raum}",
            )

            zustaende[raum] = {
                "zustand": zustand,
                "boden_belag":boden_belag,
                "boden_zustand": boden_zustand,
                "waende_dechen": waende_dechen,
                "duebelloecher": duebelloecher,
                "fliesen_gerissen_ja": fliesen_gerissen_ja,
                "fliesen_anzahl_risse": fliesen_anzahl_risse,
                "schadstellen_ja": schadstellen_ja,
                "schadstellen_beschr": schadstellen_beschr,
                "schadstellen_gr": schadstellen_gr,
                "kommentar": kommentar,
                "fotos": fotos,
            }

st.markdown("---")

# --- ABSCHNITT 5: SONSTIGE BEMERKUNGEN ---
with st.container():
    st.subheader("💬 5. Sonstige Vereinbarungen & Bemerkungen")
    sonstige_bemerkungen = st.text_area(
        "Hier Platz für Sonderabsprachen, Restarbeiten (z.B. Übergabe von Farbtöpfen, Fristen für Nacharbeiten):",
        "",
    )

st.markdown("---")

# --- ABSCHNITT 6: UNTERSCHRIFTEN ---
with st.container():
    st.subheader("✍️ 6. Unterschriften")
    st.write(
        "Bitte unterschreiben Sie mit dem Finger oder einem Stift direkt im Feld."
    )

    col_sig1, col_sig2 = st.columns(2)

    with col_sig1:
        st.write("**Vermieter (KARE)**")
        canvas_vermieter_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=3,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=150,
            width=280,
            drawing_mode="freedraw",
            key="canvas_vermieter",
        )

    with col_sig2:
        st.write("**Mieter**")
        canvas_mieter_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=3,
            stroke_color="#000000",
            background_color="#FFFFFF",
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

        pdf = ModernPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=10)

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
        pdf.cell(0, 6, mietbeginn.strftime("%d.%m.%Y"), 0, 1)

        if protokoll_typ == "Wohnungsabnahmeprotokoll" and mietende:
            pdf.set_font("helvetica", size=10)
            pdf.cell(45, 6, "Mietende:", 0, 0)
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(0, 6, mietende.strftime("%d.%m.%Y"), 0, 1)

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

            if kaution_status == "Wird in Raten gezahlt":
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

        for item in st.session_state.weitere_schluessel:
            pdf.cell(
                0,
                5,
                f"  - {item['bezeichnung'].encode('latin-1', 'replace').decode('latin-1')}: {item['anzahl']} Stk.",
                0,
                1,
            )
        pdf.ln(4)

        # 3. Zählerstände
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
                f"Stand: {z['stand']:.3f} {z['einheit']}"
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
                sonstige_bemerkungen.encode("latin-1", "replace").decode("latin-1"),
            )
        else:
            pdf.cell(0, 5, "Keine weiteren Bemerkungen.", 0, 1)
        pdf.ln(4)

        # 6. Unterschriften (PDF-Ausgabe mit sicherem Try-Except Block)
        if pdf.get_y() > 210:
            pdf.add_page()

        pdf.chapter_title("6. Unterschriften")
        pdf.ln(5)

        sig_y = pdf.get_y()

        # Vermieter Unterschrift sicher auslesen
        try:
            if (
                canvas_vermieter_result is not None
                and hasattr(canvas_vermieter_result, "image_data")
                and canvas_vermieter_result.image_data is not None
            ):
                img_v = Image.fromarray(
                    canvas_vermieter_result.image_data.astype("uint8"),
                    mode="RGBA",
                )
                bg = Image.new("RGBA", img_v.size, (255, 255, 255, 255))
                img_v = Image.alpha_composite(bg, img_v).convert("RGB")

                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".png"
                ) as tmp_sig_v:
                    img_v.save(tmp_sig_v.name)
                    temp_files.append(tmp_sig_v.name)
                    pdf.image(tmp_sig_v.name, x=15, y=sig_y, w=80)
        except Exception:
            pass

        # Mieter Unterschrift sicher auslesen
        try:
            if (
                canvas_mieter_result is not None
                and hasattr(canvas_mieter_result, "image_data")
                and canvas_mieter_result.image_data is not None
            ):
                img_m = Image.fromarray(
                    canvas_mieter_result.image_data.astype("uint8"), mode="RGBA"
                )
                bg = Image.new("RGBA", img_m.size, (255, 255, 255, 255))
                img_m = Image.alpha_composite(bg, img_m).convert("RGB")

                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".png"
                ) as tmp_sig_m:
                    img_m.save(tmp_sig_m.name)
                    temp_files.append(tmp_sig_m.name)
                    pdf.image(tmp_sig_m.name, x=115, y=sig_y, w=80)
        except Exception:
            pass

        pdf.set_y(sig_y + 35)
        pdf.set_font("helvetica", "", 9)
        pdf.cell(
            90,
            5,
            "_________________________________________",
            0,
            0,
            "L",
        )
        pdf.cell(
            90,
            5,
            "_________________________________________",
            0,
            1,
            "L",
        )
        pdf.cell(
            90,
            5,
            f"Vermieter ({vermieter})".encode("latin-1", "replace").decode("latin-1"),
            0,
            0,
            "L",
        )
        pdf.cell(
            90,
            5,
            f"Mieter ({mieter})".encode("latin-1", "replace").decode("latin-1"),
            0,
            1,
            "L",
        )

        pdf_output = pdf.output(dest="S").encode("latin1")

        st.download_button(
            label="📥 PDF herunterladen",
            data=pdf_output,
            file_name=f"Protokoll_{wohnung.replace(' ', '_')}.pdf",
            mime="application/pdf",
        )

        for tf in temp_files:
            try:
                os.remove(tf)
            except Exception:
                pass
