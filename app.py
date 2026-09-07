import tempfile
from datetime import datetime
import numpy as np
from PIL import Image, ImageDraw
from fpdf import FPDF
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# Seitenkonfiguration
st.set_page_config(
    page_title="Wohnungsabnahmeprotokoll - KARE-Immobilien",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 Wohnungsabnahmeprotokoll")
st.markdown(
    "**KARE-Immobilien** | Talstr. 32, 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de"
)
st.markdown("---")

# --- SEITENLEISTE / EINGABEN ---
st.sidebar.header("📝 Stammdaten & Details")

# 1. Objektdaten
st.sidebar.subheader("1. Objektdaten")
strasse = st.sidebar.text_input("Straße & Hausnummer", "Talstr. 32")
plz_ort = st.sidebar.text_input("PLZ & Ort", "07545 Gera")
etage = st.sidebar.text_input("Etage / Lage", "2. Obergeschoss links")

# 2. Parteien
st.sidebar.subheader("2. Parteien")
vermieter = st.sidebar.text_input("Vermieter / Hausverwaltung", "KARE-Immobilien")
mieter = st.sidebar.text_input("Mieter", "adwad")
vertreter = st.sidebar.text_input(
    "Anwesender Vertreter (optional)", "Herr Mustermann"
)
uebergabe_art = st.sidebar.selectbox(
    "Art der Übergabe", ["Auszug (Rückgabe)", "Einzug (Übergabe)"]
)
datum = st.sidebar.date_input("Datum der Übergabe", datetime.today())

# 3. Zählerstände
st.sidebar.subheader("3. Zählerstände")
strom_nr = st.sidebar.text_input("Strom - Zähler-Nr.", "S-987654")
strom_stand = st.sidebar.text_input("Strom - Stand (kWh)", "45210")

gas_nr = st.sidebar.text_input("Gas - Zähler-Nr.", "G-123456")
gas_stand = st.sidebar.text_input("Gas - Stand (m³)", "1280")

wasser_kalt_nr = st.sidebar.text_input("Kaltwasser - Zähler-Nr.", "KW-5544")
wasser_kalt_stand = st.sidebar.text_input("Kaltwasser - Stand (m³)", "145.2")

wasser_warm_nr = st.sidebar.text_input("Warmwasser - Zähler-Nr.", "WW-3322")
wasser_warm_stand = st.sidebar.text_input("Warmwasser - Stand (m³)", "68.5")

# 5 Heizungszähler
st.sidebar.markdown("**Heizungszähler (Heizkostenverteiler)**")
heizung_raeume = ["Wohnzimmer", "Kinderzimmer", "Flur", "Bad", "Küche"]
heizung_daten = {}
for raum in heizung_raeume:
    h_nr = st.sidebar.text_input(f"Nr. {raum}", f"HZ-{raum[:3].upper()}-01")
    h_std = st.sidebar.text_input(f"Stand {raum}", "1234")
    heizung_daten[raum] = {"nr": h_nr, "stand": h_std}

# --- HAUPTBEREICH: ZUSTAND DER RÄUME ---
st.subheader("🛠️ 4. Zustand der Räume & Mängel")
st.write(
    "Bitte bewerten Sie den Zustand der einzelnen Bereiche und erfassen Sie ggf. Mängel."
)

raeume_liste = [
    "Flur / Diele",
    "Wohnzimmer",
    "Schlafzimmer",
    "Kinderzimmer",
    "Küche",
    "Badezimmer",
    "Keller / Abstellraum",
    "Balkon / Terrasse",
]
raum_zustaende = {}

for raum in raeume_liste:
    with st.expander(f"📍 {raum}"):
        col_z1, col_z2 = st.columns([1, 2])
        with col_z1:
            zustand = st.selectbox(
                f"Zustand",
                ["Einwandfrei", "Gebrauchsspuren", "Mängel vorhanden"],
                key=f"zustand_{raum}",
            )
        with col_z2:
            maengel = st.text_area(
                f"Beschreibung von Mängeln / Details",
                placeholder="z.B. Bohrlocher in Wand, Türstock verkratzt...",
                key=f"maengel_{raum}",
            )
        raum_zustaende[raum] = {"zustand": zustand, "maengel": maengel}

# --- SCHLÜSSELÜBERGABE ---
st.subheader("🔑 5. Schlüsselübergabe")
col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    schl_haus = st.number_input(
        "Hauseingangstür", min_value=0, max_value=10, value=2
    )
with col_s2:
    schl_wohnung = st.number_input(
        "Wohnungstür", min_value=0, max_value=10, value=2
    )
with col_s3:
    schl_keller = st.number_input("Keller / Sonstige", min_value=0, max_value=10, value=1)

sonstige_schluessel = st.text_input(
    "Weitere Schlüssel / Besonderheiten", "Briefkastenschlüssel (2 Stk.)"
)

# --- ABSCHNITT 6: UNTERSCHRIFTEN ---
st.markdown("---")
st.subheader("✍️ 6. Unterschriften")
st.write("Bitte unterschreiben Sie mit dem Finger oder einem Stift direkt im Feld.")

col_sig1, col_sig2 = st.columns(2)

with col_sig1:
    st.write("**Vermieter (KARE-Immobilien)**")
    canvas_vermieter_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=150,
        width=280,
        drawing_mode="freedraw",
        realtime_update=True,
        key="canvas_vermieter",
    )

with col_sig2:
    st.write(f"**Mieter ({mieter})**")
    canvas_mieter_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=150,
        width=280,
        drawing_mode="freedraw",
        realtime_update=True,
        key="canvas_mieter",
    )


# --- PDF KLASSE ---
class PDF(FPDF):

    def header(self):
        self.set_font("helvetica", "B", 14)
        self.cell(
            0,
            8,
            "Wohnungsabnahmeprotokoll".encode("latin-1", "replace").decode(
                "latin-1"
            ),
            0,
            1,
            "L",
        )
        self.set_font("helvetica", "", 8)
        self.setTextColor(100, 100, 100)
        self.cell(
            0,
            4,
            "KARE-Immobilien | Talstr. 32, 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de".encode(
                "latin-1", "replace"
            ).decode("latin-1"),
            0,
            1,
            "L",
        )
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(6)
        self.setTextColor(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(
            0,
            10,
            f"Seite {self.page_no()}/{{nb}}",
            0,
            0,
            "C",
        )

    def chapter_title(self, title):
        self.set_font("helvetica", "B", 11)
        self.set_fill_color(240, 240, 240)
        self.cell(
            0,
            6,
            f" {title}".encode("latin-1", "replace").decode("latin-1"),
            0,
            1,
            "L",
            1,
        )
        self.ln(2)


# --- PDF GENERIEREN BUTTON ---
st.markdown("---")
if st.button("📄 PDF-Protokoll generieren", type="primary"):
    temp_files = []
    try:
        pdf = PDF(orientation="P", unit="mm", format="A4")
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("helvetica", "", 10)

        # 1. Objektdaten & Parteien
        pdf.chapter_title("1. Objektdaten & Parteien")
        data_block1 = [
            ("Objektanschrift:", f"{strasse}, {plz_ort} ({etage})"),
            ("Art der Übergabe:", str(uebergabe_art)),
            ("Datum:", datum.strftime("%d.%m.%Y")),
            ("Vermieter:", str(vermieter)),
            ("Mieter:", str(mieter)),
            (
                "Anwesender Vertreter:",
                str(vertreter) if vertreter else "Keiner",
            ),
        ]
        pdf.set_font("helvetica", "", 9)
        for k, v in data_block1:
            pdf.cell(50, 5, k.encode("latin-1", "replace").decode("latin-1"), 0, 0)
            pdf.cell(
                140, 5, v.encode("latin-1", "replace").decode("latin-1"), 0, 1
            )
        pdf.ln(4)

        # 2. Zählerstände
        pdf.chapter_title("2. Zählerstände")
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(45, 6, "Zählertyp", 1, 0, "C", True)
        pdf.cell(65, 6, "Zählernummer", 1, 0, "C", True)
        pdf.cell(80, 6, "Zählerstand", 1, 1, "C", True)

        pdf.set_font("helvetica", "", 9)
        zaehler_list = [
            ("Strom", strom_nr, f"{strom_stand} kWh"),
            ("Gas", gas_nr, f"{gas_stand} m³"),
            ("Kaltwasser", wasser_kalt_nr, f"{wasser_kalt_stand} m³"),
            ("Warmwasser", wasser_warm_nr, f"{wasser_warm_stand} m³"),
        ]
        for zt, zn, zs in zaehler_list:
            pdf.cell(45, 6, zt, 1, 0)
            pdf.cell(65, 6, zn.encode("latin-1", "replace").decode("latin-1"), 1, 0)
            pdf.cell(80, 6, zs.encode("latin-1", "replace").decode("latin-1"), 1, 1)

        # Heizungszähler
        for raum, h_data in heizung_daten.items():
            pdf.cell(45, 6, f"Heizung ({raum})", 1, 0)
            pdf.cell(
                65,
                6,
                h_data["nr"].encode("latin-1", "replace").decode("latin-1"),
                1,
                0,
            )
            pdf.cell(
                80,
                6,
                h_data["stand"].encode("latin-1", "replace").decode("latin-1"),
                1,
                1,
            )
        pdf.ln(4)

        # 3. Zustand der Räume
        pdf.chapter_title("3. Zustand der Räume & Mängel")
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(45, 6, "Raum", 1, 0, "C", True)
        pdf.cell(45, 6, "Zustand", 1, 0, "C", True)
        pdf.cell(100, 6, "Mängel / Beschreibung", 1, 1, "C", True)

        pdf.set_font("helvetica", "", 9)
        for raum, vals in raum_zustaende.items():
            pdf.cell(45, 6, raum, 1, 0)
            pdf.cell(
                45,
                6,
                vals["zustand"].encode("latin-1", "replace").decode("latin-1"),
                1,
                0,
            )
            pdf.cell(
                100,
                6,
                vals["maengel"].encode("latin-1", "replace").decode("latin-1")
                or "-",
                1,
                1,
            )
        pdf.ln(4)

        # 4. Schlüsselübergabe
        pdf.chapter_title("4. Schlüsselübergabe")
        pdf.set_font("helvetica", "", 9)
        pdf.cell(
            60,
            5,
            f"Hauseingangstür: {schl_haus} Stück".encode(
                "latin-1", "replace"
            ).decode("latin-1"),
            0,
            0,
        )
        pdf.cell(
            60,
            5,
            f"Wohnungstür: {schl_wohnung} Stück".encode(
                "latin-1", "replace"
            ).decode("latin-1"),
            0,
            0,
        )
        pdf.cell(
            70,
            5,
            f"Keller/Sonstige: {schl_keller} Stück".encode(
                "latin-1", "replace"
            ).decode("latin-1"),
            0,
            1,
        )
        pdf.cell(
            0,
            5,
            f"Weitere Schlüssel: {sonstige_schluessel}".encode(
                "latin-1", "replace"
            ).decode("latin-1"),
            0,
            1,
        )
        pdf.ln(6)

        # 5. Unterschriften
        if pdf.get_y() > 210:
            pdf.add_page()

        pdf.chapter_title("5. Unterschriften")
        pdf.ln(5)

        sig_y = pdf.get_y()


        def canvas_to_image(canvas_result):
            try:
                if (
                    canvas_result is not None
                    and "json_data" in canvas_result
                    and canvas_result["json_data"] is not None
                ):
                    objects = canvas_result["json_data"].get("objects", [])
                    if len(objects) > 0:
                        sig_img = Image.new("RGB", (280, 150), (255, 255, 255))
                        draw = ImageDraw.Draw(sig_img)

                        for obj in objects:
                            if obj.get("type") == "path":
                                path = obj.get("path", [])
                                points = []
                                for cmd in path:
                                    if (
                                        len(cmd) >= 3
                                        and cmd[0] in ["M", "L", "Q", "C"]
                                    ):
                                        points.append((cmd[-2], cmd[-1]))

                                if len(points) > 1:
                                    left = obj.get("left", 0)
                                    top = obj.get("top", 0)
                                    scale_x = obj.get("scaleX", 1)
                                    scale_y = obj.get("scaleY", 1)

                                    adjusted_points = [
                                        (
                                            (p[0] * scale_x) + left,
                                            (p[1] * scale_y) + top,
                                        )
                                        for p in points
                                    ]
                                    for i in range(len(adjusted_points) - 1):
                                        draw.line(
                                            [
                                                adjusted_points[i],
                                                adjusted_points[i + 1],
                                            ],
                                            fill="black",
                                            width=3,
                                        )
                        return sig_img

                if (
                    canvas_result is not None
                    and hasattr(canvas_result, "image_data")
                    and canvas_result.image_data is not None
                ):
                    img_data = canvas_result.image_data
                    if img_data.shape[0] > 0 and img_data.shape[1] > 0:
                        img = Image.fromarray(
                            img_data.astype("uint8"), mode="RGBA"
                        )
                        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
                        return Image.alpha_composite(bg, img).convert("RGB")
            except Exception as ex:
                print(f"Canvas Verarbeitungsfehler: {ex}")
            return None


        # Vermieter Unterschrift einfügen
        img_v = canvas_to_image(canvas_vermieter_result)
        if img_v:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".png"
            ) as tmp_sig_v:
                img_v.save(tmp_sig_v.name)
                temp_files.append(tmp_sig_v.name)
                pdf.image(tmp_sig_v.name, x=15, y=sig_y, w=80)

        # Mieter Unterschrift einfügen
        img_m = canvas_to_image(canvas_mieter_result)
        if img_m:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".png"
            ) as tmp_sig_m:
                img_m.save(tmp_sig_m.name)
                temp_files.append(tmp_sig_m.name)
                pdf.image(tmp_sig_m.name, x=115, y=sig_y, w=80)

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

        # PDF Bytes ausgeben
        pdf_bytes = pdf.output(dest="S").encode("latin1")

        st.success("✅ Das Wohnungsabnahmeprotokoll wurde erfolgreich erstellt!")
        st.download_button(
            label="📥 PDF herunterladen",
            data=pdf_bytes,
            file_name=f"Wohnungsabnahmeprotokoll_{datum.strftime('%Y-%m-%d')}.pdf",
            mime="application/pdf",
        )

    finally:
        for tf in temp_files:
            try:
                import os

                os.remove(tf)
            except:
                pass
