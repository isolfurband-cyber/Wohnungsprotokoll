import streamlit as st
from streamlit_drawable_canvas import st_canvas
from fpdf import FPDF
import tempfile
import os
from PIL import Image

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="KARE-Immobilien | Protokoll-Generator",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FÜR MODERNES DESIGN ---
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .stButton>button {
        background-color: #0f172a;
        color: white;
        border-radius: 6px;
        font-weight: 600;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1e293b;
        color: white;
    }
    h1, h2, h3 {
        color: #0f172a;
    }
    </style>
""", unsafe_allow_html=True)

# --- FPDF KLASSE DEFINITION ---
class ModernPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(15, 23, 42)
        self.cell(0, 6, 'KARE-Immobilien', 0, 1, 'L')
        self.set_font('helvetica', '', 9)
        self.set_text_color(100, 116, 139)
        self.cell(0, 5, 'Talstr. 32 | 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de', 0, 1, 'L')
        self.ln(2)
        self.set_draw_color(203, 213, 225)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', '', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f'Seite {self.page_no()}/{{nb}} - KARE-Immobilien', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('helvetica', 'B', 11)
        self.set_fill_color(241, 245, 249)
        self.set_text_color(15, 23, 42)
        self.cell(0, 7, f"  {title}", 0, 1, 'L', fill=True)
        self.ln(3)

# --- HAUPTAPP ---
st.title("🏠 KARE-Immobilien Protokoll-Generator")
st.write("Erstelle rechtssichere Wohnungsabnahme- und Übergabeprotokolle mit digitaler Unterschrift.")

# Protokoll-Art Auswahl wiederhergestellt
protokoll_typ = st.selectbox(
    "Protokoll-Art wählen",
    ["Wohnungsübergabeprotokoll (Einzug)", "Wohnungsabnahmeprotokoll (Auszug)", "Zwischenprotokoll"]
)

st.divider()

# --- 1. STAMMDATEN ---
with st.container(border=True):
    st.subheader("📋 1. Stammdaten & Objekt")
    col1, col2 = st.columns(2)
    with col1:
        wohnung = st.text_input("Objektanschrift / Wohnung", placeholder="z.B. Musterstraße 12, 07545 Gera")
        vermieter = st.text_input("Vermieter / Vertreter", value="KARE-Immobilien")
    with col2:
        mieter = st.text_input("Name des Mieters", placeholder="Max Mustermann")
        datum = st.date_input("Datum des Protokolls")

st.write("")

# --- 2. ZÄHLERSTÄNDE ---
with st.container(border=True):
    st.subheader("⚡ 2. Zählerstände")
    st.write("Bitte erfasse hier die aktuellen Zählerstände und Zählernummern.")

    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.markdown("**💧 Kaltwasserzähler**")
        kw_nr = st.text_input("Zählernummer Kaltwasser", placeholder="Nummer eingeben")
        kw_stand = st.text_input("Stand Kaltwasser (m³)", placeholder="z.B. 124.5")
    with col_w2:
        st.markdown("**🔥 Warmwasserzähler**")
        ww_nr = st.text_input("Zählernummer Warmwasser", placeholder="Nummer eingeben")
        ww_stand = st.text_input("Stand Warmwasser (m³)", placeholder="z.B. 45.2")

    st.divider()
    st.markdown("**🔥 Heizungszähler (Heizkostenverteiler)**")
    
    haeuser_raeume = ["Wohnzimmer", "Kinderzimmer", "Flur", "Bad", "Küche"]
    heizungs_daten = {}

    col_h1, col_h2 = st.columns(2)
    for i, raum in enumerate(haeuser_raeume):
        with (col_h1 if i % 2 == 0 else col_h2):
            st.markdown(f"*{raum}*")
            h_nr = st.text_input(f"Zählernummer {raum}", key=f"hnr_{raum}", placeholder="Gerätenummer")
            h_std = st.text_input(f"Ablesewert {raum}", key=f"hstd_{raum}", placeholder="Wert")
            heizungs_daten[raum] = {"nummer": h_nr, "stand": h_std}

st.write("")

# --- 3. KAUTION & FINANZIELLES ---
with st.container(border=True):
    st.subheader("💶 3. Kaution & Zahlungen")
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        kaution_soll = st.text_input("Kautionshöhe gesamt (€)", placeholder="z.B. 1200.00")
    with col_k2:
        kaution_status = st.selectbox("Status Kaution", ["Gezahlt", "Teilweise gezahlt", "Ausstehend", "Wird bar übergeben"])

st.write("")

# --- 4. SCHLÜSSELISTE ---
with st.container(border=True):
    st.subheader("🔑 4. Schlüsselübergabe")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        schl_wohnung = st.number_input("Wohnungsschlüssel", min_value=0, value=3, step=1)
    with col_s2:
        schl_haus = st.number_input("Hauseingang / Haustür", min_value=0, value=2, step=1)
    with col_s3:
        schl_keller = st.number_input("Keller / Sonstige", min_value=0, value=1, step=1)

st.write("")

# --- 5. RÄUME & MÄNGEL ---
with st.container(border=True):
    st.subheader("🛠️ 5. Raumzustand & Mängel")
    maengel_text = st.text_area("Festgestellte Mängel, Schäden oder notwendige Schönheitsreparaturen", placeholder="z.B. Leichte Kratzer im Laminat im Wohnzimmer...")

st.write("")

# --- 6. UNTERSCHRIFTEN ---
with st.container(border=True):
    st.subheader("✍️ 6. Unterschriften & Bestätigung")
    st.write("Bitte hier direkt mit der Maus oder dem Finger (Tablet/iPad) unterschreiben:")

    col_sig1, col_sig2 = st.columns(2)

    with col_sig1:
        st.write("**Vermieter (KARE-Immobilien)**")
        canvas_vermieter = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=130,
            width=300,
            drawing_mode="freedraw",
            update_streamlit=True,
            key="canvas_vermieter",
        )

    with col_sig2:
        st.write("**Mieter**")
        canvas_mieter = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=130,
            width=300,
            drawing_mode="freedraw",
            update_streamlit=True,
            key="canvas_mieter",
        )

st.write("")

# --- PDF GENERIERUNG LOGIK ---
if not wohnung or not mieter:
    st.warning("⚠️ Bitte fülle mindestens die Objektanschrift und den Namen des Mieters aus.")
else:
    pdf = ModernPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("helvetica", size=10)

    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, protokoll_typ.upper(), 0, 1, "C")
    pdf.ln(4)

    pdf.chapter_title("1. Stammdaten & Objekt")
    pdf.set_font("helvetica", "", 10)
    pdf.cell(50, 6, "Objekt / Anschrift:", 0, 0)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 6, wohnung, 0, 1)
    
    pdf.set_font("helvetica", "", 10)
    pdf.cell(50, 6, "Mieter:", 0, 0)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 6, mieter, 0, 1)

    pdf.set_font("helvetica", "", 10)
    pdf.cell(50, 6, "Vermieter:", 0, 0)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 6, vermieter, 0, 1)

    pdf.set_font("helvetica", "", 10)
    pdf.cell(50, 6, "Datum:", 0, 0)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 6, str(datum), 0, 1)
    pdf.ln(5)

    pdf.chapter_title("2. Zählerstände")
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(95, 6, "Wasserzähler", 0, 0)
    pdf.cell(95, 6, "Zählernummer / Wert", 0, 1)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(95, 6, f"Kaltwasser: {kw_stand or '-'} m³", 0, 0)
    pdf.cell(95, 6, f"Nr: {kw_nr or '-'}", 0, 1)
    pdf.cell(95, 6, f"Warmwasser: {ww_stand or '-'} m³", 0, 0)
    pdf.cell(95, 6, f"Nr: {ww_nr or '-'}", 0, 1)
    pdf.ln(3)

    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 6, "Heizungszähler (Heizkostenverteiler)", 0, 1)
    pdf.set_font("helvetica", "", 10)
    for raum, daten in heizungs_daten.items():
        pdf.cell(50, 5, f"- {raum}:", 0, 0)
        pdf.cell(70, 5, f"Stand: {daten['stand'] or '-'}", 0, 0)
        pdf.cell(70, 5, f"Nr: {daten['nummer'] or '-'}", 0, 1)
    pdf.ln(5)

    pdf.chapter_title("3. Kaution & Zahlungen")
    pdf.cell(50, 6, "Kautionssumme:", 0, 0)
    pdf.cell(0, 6, f"{kaution_soll} €" if kaution_soll else "-", 0, 1)
    pdf.cell(50, 6, "Status:", 0, 0)
    pdf.cell(0, 6, kaution_status, 0, 1)
    pdf.ln(5)

    pdf.chapter_title("4. Schlüsselübergabe")
    pdf.cell(60, 6, f"Wohnungsschlüssel: {schl_wohnung}", 0, 0)
    pdf.cell(60, 6, f"Haustür: {schl_haus}", 0, 0)
    pdf.cell(60, 6, f"Keller/Sonstige: {schl_keller}", 0, 1)
    pdf.ln(5)

    pdf.chapter_title("5. Raumzustand & Festgestellte Mängel")
    pdf.multi_cell(0, 6, maengel_text if maengel_text else "Keine besonderen Mängel vermerkt.")
    pdf.ln(8)

    pdf.chapter_title("6. Unterschriften & Bestätigung")
    pdf.ln(2)

    sig_y = pdf.get_y()
    if sig_y > 200:
        pdf.add_page()
        sig_y = pdf.get_y()

    temp_files = []

    sig_v_path = None
    if isinstance(canvas_vermieter, dict) and canvas_vermieter.get("data") is not None:
        try:
            arr_v = canvas_vermieter["data"]
            img_v = Image.fromarray(arr_v.astype("uint8"), mode="RGBA")
            background = Image.new("RGBA", img_v.size, (255, 255, 255, 255))
            alpha_composite = Image.alpha_composite(background, img_v)
            rgb_img = alpha_composite.convert("RGB")
            
            extrema = rgb_img.getextrema()
            if extrema[0][0] < 250 or extrema[1][0] < 250 or extrema[2][0] < 250:
                sig_v_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
                rgb_img.save(sig_v_path, "PNG")
                temp_files.append(sig_v_path)
        except Exception as e:
            print("Vermieter Unterschrift Fehler:", e)

    sig_m_path = None
    if isinstance(canvas_mieter, dict) and canvas_mieter.get("data") is not None:
        try:
            arr_m = canvas_mieter["data"]
            img_m = Image.fromarray(arr_m.astype("uint8"), mode="RGBA")
            background = Image.new("RGBA", img_m.size, (255, 255, 255, 255))
            alpha_composite = Image.alpha_composite(background, img_m)
            rgb_img_m = alpha_composite.convert("RGB")
            
            extrema = rgb_img_m.getextrema()
            if extrema[0][0] < 250 or extrema[1][0] < 250 or extrema[2][0] < 250:
                sig_m_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
                rgb_img_m.save(sig_m_path, "PNG")
                temp_files.append(sig_m_path)
        except Exception as e:
            print("Mieter Unterschrift Fehler:", e)

    current_y_sig = pdf.get_y()

    if sig_v_path:
        try:
            pdf.image(sig_v_path, x=15, y=current_y_sig - 10, w=80)
        except Exception:
            pass

    if sig_m_path:
        try:
            pdf.image(sig_m_path, x=110, y=current_y_sig - 10, w=80)
        except Exception:
            pass

    pdf.ln(25)
    pdf.set_font("helvetica", "", 9)
    pdf.cell(90, 5, "________________________________________", 0, 0, "L")
    pdf.cell(10, 5, "", 0, 0)
    pdf.cell(90, 5, "________________________________________", 0, 1, "L")

    pdf.cell(90, 5, "Vermieter (KARE-Immobilien)", 0, 0, "L")
    pdf.cell(10, 5, "", 0, 0)
    pdf.cell(90, 5, f"Mieter ({mieter})", 0, 1, "L")

    pdf_output = bytes(pdf.output())

    for tf in temp_files:
        try:
            os.unlink(tf)
        except Exception:
            pass

    st.success("Protokoll erfolgreich erstellt und unterschrieben!")
    st.download_button(
        label="PDF-Protokoll herunterladen",
        data=pdf_output,
        file_name=f"Protokoll_{mieter.replace(' ', '_')}.pdf",
        mime="application/octet-stream",
        use_container_width=True,
    )
