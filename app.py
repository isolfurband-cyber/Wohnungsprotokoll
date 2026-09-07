import os
import io
from datetime import datetime
import streamlit as st
import pandas as pd
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from streamlit_drawable_canvas import st_canvas

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="KARE-Immobilien - Wohnungsabnahmeprotokoll",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING & DESIGN ---
st.markdown("""
    <style>
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 25px;
    }
    .section-title {
        font-size: 18px;
        font-weight: 600;
        color: #0F172A;
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 5px;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #3B82F6;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER & FIRMENDATEN ---
st.markdown('<div class="main-header">🏠 KARE-Immobilien – Wohnungsabnahmeprotokoll</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Talstr. 32, 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de</div>', unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/color/96/real-estate.png", width=70)
    st.markdown("### Navigation & Status")
    current_step = st.radio("Bereiche wählen:", [
        "1. Stammdaten",
        "2. Zählerstände",
        "3. Raum-Check & Mängel",
        "4. Schlüsselübergabe",
        "5. Unterschriften & PDF Export"
    ])
    st.markdown("---")
    st.info("💡 Tipp: Füllen Sie alle Felder sorgfältig aus, um das Übergabeprotokoll fehlerfrei als PDF zu generieren.")

# --- SESSION STATE INITIALISIERUNG ---
if "data" not in st.session_state:
    st.session_state.data = {
        "vermieter": "KARE-Immobilien",
        "ansprechpartner": "",
        "mieter": "",
        "objekt_adresse": "",
        "einzug_auszug": "Auszug",
        "datum": datetime.today().date(),
        "schluessel": {
            "Wohnungstür": 2,
            "Haustür": 2,
            "Keller": 1,
            "Briefkasten": 1,
            "Garage/Stellplatz": 0
        },
        "zaehler": {
            "kaltwasser": {"stand": "", "nr": ""},
            "warmwasser": {"stand": "", "nr": ""},
            "heizung": {
                "Wohnzimmer": {"stand": "", "nr": ""},
                "Kinderzimmer": {"stand": "", "nr": ""},
                "Flur": {"stand": "", "nr": ""},
                "Bad": {"stand": "", "nr": ""},
                "Küche": {"stand": "", "nr": ""}
            }
        },
        "raeume": [
            "Flur", "Wohnzimmer", "Schlafzimmer", "Kinderzimmer", 
            "Küche", "Badezimmer", "Keller", "Balkon / Terrasse"
        ],
        "maengel": {},
        "notizen": ""
    }

d = st.session_state.data

# ==========================================
# 1. STAMMDATEN
# ==========================================
if current_step == "1. Stammdaten":
    st.markdown('<div class="section-title">1. Allgemeine Stammdaten & Vertragsparteien</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        d["vermieter"] = st.text_input("Vermieter / Verwaltung", value=d["vermieter"])
        d["ansprechpartner"] = st.text_input("Name des Übergabe-Ansprechpartners", value=d["ansprechpartner"])
        d["objekt_adresse"] = st.text_area("Objektadresse (Straße, PLZ, Ort)", value=d["objekt_adresse"])
    
    with col2:
        d["mieter"] = st.text_input("Mieter (Neu / Alt)", value=d["mieter"])
        d["einzug_auszug"] = st.selectbox("Protokollart", ["Auszug (Übergabe an Vermieter)", "Einzug (Übergabe an Mieter)"], index=0 if "Auszug" in d["einzug_auszug"] else 1)
        d["datum"] = st.date_input("Datum der Übergabe", value=d["datum"])

# ==========================================
# 2. ZÄHLERSTÄNDE
# ==========================================
elif current_step == "2. Zählerstände":
    st.markdown('<div class="section-title">2. Zählerstände (Wasser & Heizung)</div>', unsafe_allow_html=True)
    
    st.subheader("💧 Wasserzähler")
    colw1, colw2 = st.columns(2)
    with colw1:
        st.markdown("**Kaltwasserzähler**")
        d["zaehler"]["kaltwasser"]["nr"] = st.text_input("Zählernummer (Kaltwasser)", value=d["zaehler"]["kaltwasser"]["nr"])
        d["zaehler"]["kaltwasser"]["stand"] = st.text_input("Zählerstand (m³) - Kaltwasser", value=d["zaehler"]["kaltwasser"]["stand"])
    with colw2:
        st.markdown("**Warmwasserzähler**")
        d["zaehler"]["warmwasser"]["nr"] = st.text_input("Zählernummer (Warmwasser)", value=d["zaehler"]["warmwasser"]["nr"])
        d["zaehler"]["warmwasser"]["stand"] = st.text_input("Zählerstand (m³) - Warmwasser", value=d["zaehler"]["warmwasser"]["stand"])

    st.markdown("---")
    st.subheader("🔥 Heizungszähler (Heizkostenverteiler / Wärmemengenzähler)")
    st.markdown("Erfassung für die 5 definierten Räume:")
    
    for raum in ["Wohnzimmer", "Kinderzimmer", "Flur", "Bad", "Küche"]:
        st.markdown(f"**Raum: {raum}**")
        colh1, colh2 = st.columns(2)
        with colh1:
            d["zaehler"]["heizung"][raum]["nr"] = st.text_input(f"Zählernummer ({raum})", value=d["zaehler"]["heizung"][raum]["nr"], key=f"h_nr_{raum}")
        with colh2:
            d["zaehler"]["heizung"][raum]["stand"] = st.text_input(f"Zählerstand ({raum})", value=d["zaehler"]["heizung"][raum]["stand"], key=f"h_std_{raum}")

# ==========================================
# 3. RAUM-CHECK & MÄNGEL
# ==========================================
elif current_step == "3. Raum-Check & Mängel":
    st.markdown('<div class="section-title">3. Raum-Check & Mängelerfassung</div>', unsafe_allow_html=True)
    st.write("Überprüfen Sie die Räume auf Zustand und eventuelle Mängel.")
    
    for raum in d["raeume"]:
        with st.expander(f"📍 Raum: {raum}", expanded=False):
            if raum not in d["maengel"]:
                d["maengel"][raum] = {"zustand": "Einwandfrei", "beschreibung": "", "sperrmuell": False}
            
            d["maengel"][raum]["zustand"] = st.selectbox(
                f"Zustand {raum}", 
                ["Einwandfrei", "Gebrauchsspuren", "Mängel vorhanden", "Renovierungsbedürftig"],
                index=["Einwandfrei", "Gebrauchsspuren", "Mängel vorhanden", "Renovierungsbedürftig"].index(d["maengel"][raum]["zustand"]) if d["maengel"][raum]["zustand"] in ["Einwandfrei", "Gebrauchsspuren", "Mängel vorhanden", "Renovierungsbedürftig"] else 0,
                key=f"zustand_{raum}"
            )
            d["maengel"][raum]["beschreibung"] = st.text_area(
                f"Beschreibung von Mängeln / Besonderheiten in {raum}",
                value=d["maengel"][raum]["beschreibung"],
                key=f"desc_{raum}"
            )

    st.markdown("---")
    d["notizen"] = st.text_area("Allgemeine Anmerkungen / Vereinbarungen", value=d["notizen"])

# ==========================================
# 4. SCHLÜSSELÜBERGABE
# ==========================================
elif current_step == "4. Schlüsselübergabe":
    st.markdown('<div class="section-title">4. Schlüsselübergabe</div>', unsafe_allow_html=True)
    st.write("Geben Sie die Anzahl der übergebenen Schlüssel je Schlossart an:")
    
    cols = st.columns(3)
    idx = 0
    for schluessel_typ, anzahl in d["schluessel"].items():
        with cols[idx % 3]:
            d["schluessel"][schluessel_typ] = st.number_input(f"{schluessel_typ}", min_value=0, max_value=20, value=anzahl, step=1)
        idx += 1

# ==========================================
# 5. UNTERSCHRIFTEN & PDF EXPORT
# ==========================================
elif current_step == "5. Unterschriften & PDF Export":
    st.markdown('<div class="section-title">5. Unterschriften & PDF-Generierung</div>', unsafe_allow_html=True)
    
    col_u1, col_u2 = st.columns(2)
    
    with col_u1:
        st.markdown("**Unterschrift Vermietung / Vertreter**")
        canvas_vermieter = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=150,
            width=350,
            drawing_mode="freedraw",
            key="canvas_v"
        )
        
    with col_u2:
        st.markdown("**Unterschrift Mieter**")
        canvas_mieter = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=150,
            width=350,
            drawing_mode="freedraw",
            key="canvas_m"
        )
        
    st.markdown("---")
    
    if st.button("📄 Wohnungsabnahmeprotokoll als PDF erstellen"):
        # Sichere Extraktion der Canvas-Daten mit Fehlerbehandlung
        vermieter_unterschrift_img = None
        try:
            if canvas_vermieter is not None and hasattr(canvas_vermieter, "image_data") and canvas_vermieter.image_data is not None:
                vermieter_unterschrift_img = canvas_vermieter.image_data
        except Exception:
            vermieter_unterschrift_img = None

        mieter_unterschrift_img = None
        try:
            if canvas_mieter is not None and hasattr(canvas_mieter, "image_data") and canvas_mieter.image_data is not None:
                mieter_unterschrift_img = canvas_mieter.image_data
        except Exception:
            mieter_unterschrift_img = None

        # PDF Generierung via ReportLab
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        story = []
        styles = getSampleStyleSheet()
        
        # Titel
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1E3A8A'), spaceAfter=4)
        subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#64748B'), spaceAfter=15)
        
        story.append(Paragraph("KARE-Immobilien – Wohnungsabnahmeprotokoll", title_style))
        story.append(Paragraph("Talstr. 32, 07545 Gera | Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de", subtitle_style))
        
        # Stammdaten Tabelle
        meta_data = [
            [Paragraph(f"<b>Objekt:</b> {d['objekt_adresse']}", styles['Normal']), Paragraph(f"<b>Datum:</b> {d['datum'].strftime('%d.%m.%Y')}", styles['Normal'])],
            [Paragraph(f"<b>Vermieter:</b> {d['vermieter']} (Ansprechpartner: {d['ansprechpartner']})", styles['Normal']), Paragraph(f"<b>Mieter:</b> {d['mieter']}", styles['Normal'])],
            [Paragraph(f"<b>Protokollart:</b> {d['einzug_auszug']}", styles['Normal']), Paragraph("", styles['Normal'])]
        ]
        t_meta = Table(meta_data, colWidths=[270, 270])
        t_meta.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_meta)
        story.append(Spacer(1, 15))
        
        # Zählerstände
        story.append(Paragraph("<b>Zählerstände</b>", styles['Heading2']))
        zaehler_rows = [
            ["Zählertyp", "Zählernummer", "Zählerstand"],
            ["Kaltwasser", d["zaehler"]["kaltwasser"]["nr"], d["zaehler"]["kaltwasser"]["stand"] + " m³"],
            ["Warmwasser", d["zaehler"]["warmwasser"]["nr"], d["zaehler"]["warmwasser"]["stand"] + " m³"]
        ]
        for r_name, r_vals in d["zaehler"]["heizung"].items():
            zaehler_rows.append([f"Heizung ({r_name})", r_vals["nr"], r_vals["stand"]])
            
        t_zaehler = Table(zaehler_rows, colWidths=[180, 180, 180])
        t_zaehler.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#FFFFFF')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_zaehler)
        story.append(Spacer(1, 15))
        
        # Raum-Check
        story.append(Paragraph("<b>Raum-Check & Mängel</b>", styles['Heading2']))
        raum_rows = [["Raum", "Zustand", "Mängel / Beschreibung"]]
        for raum, m in d["maengel"].items():
            raum_rows.append([raum, m["zustand"], m["beschreibung"] if m["beschreibung"] else "Keine Mängel"])
            
        t_raeume = Table(raum_rows, colWidths=[130, 120, 290])
        t_raeume.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_raeume)
        story.append(Spacer(1, 15))
        
        # Schlüssel
        story.append(Paragraph("<b>Schlüsselübergabe</b>", styles['Heading2']))
        schluessel_rows = [["Schlüsselart", "Anzahl"]]
        for art, anz in d["schluessel"].items():
            schluessel_rows.append([art, str(anz)])
        t_schl = Table(schluessel_rows, colWidths=[270, 270])
        t_schl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_schl)
        story.append(Spacer(1, 25))
        
        # Unterschriften
        story.append(Paragraph("<b>Unterschriften</b>", styles['Heading2']))
        story.append(Paragraph("Mit den Unterschriften wird die Richtigkeit der obigen Angaben sowie die ordnungsgemäße Übergabe bestätigt.", styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Convert canvas images if available
        sig_v_flowable = Paragraph("Unterschrift Vermietung<br/><br/><br/>___________________________", styles['Normal'])
        if vermieter_unterschrift_img is not None:
            try:
                img_v_pil = Image.fromarray(vermieter_unterschrift_img.astype('uint8'), mode='RGBA')
                img_v_io = io.BytesIO()
                img_v_pil.save(img_v_io, format='PNG')
                img_v_io.seek(0)
                from reportlab.platypus import Image as RLImage
                sig_v_flowable = RLImage(img_v_io, width=150, height=65)
            except Exception:
                pass

        sig_m_flowable = Paragraph("Unterschrift Mieter<br/><br/><br/>___________________________", styles['Normal'])
        if mieter_unterschrift_img is not None:
            try:
                img_m_pil = Image.fromarray(mieter_unterschrift_img.astype('uint8'), mode='RGBA')
                img_m_io = io.BytesIO()
                img_m_pil.save(img_m_io, format='PNG')
                img_m_io.seek(0)
                from reportlab.platypus import Image as RLImage
                sig_m_flowable = RLImage(img_m_io, width=150, height=65)
            except Exception:
                pass

        t_sig = Table([[sig_v_flowable, sig_m_flowable]], colWidths=[270, 270])
        t_sig.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        story.append(KeepTogether([t_sig]))

        doc.build(story)
        buffer.seek(0)
        
        st.success("PDF erfolgreich erstellt!")
        st.download_button(
            label="📥 Wohnungsabnahmeprotokoll Herunterladen",
            data=buffer,
            file_name=f"Wohnungsabnahmeprotokoll_{d['objekt_adresse'].replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
