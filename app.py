import io
import os
from datetime import datetime
import numpy as np
import streamlit as st
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from streamlit_drawable_canvas import st_canvas

# Seitenkonfiguration
st.set_page_config(
    page_title="Wohnungsabnahmeprotokoll - KARE-Immobilien",
    page_icon="🏠",
    layout="wide"
)

def create_pdf(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Eigene Styles definieren
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1a365d'),
        alignment=1, # Zentriert
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4a5568'),
        alignment=1,
        spaceAfter=25
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2b6cb0'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    normal_style = ParagraphStyle(
        'Standard',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#2d3748')
    )
    
    bold_style = ParagraphStyle(
        'BoldStandard',
        parent=normal_style,
        fontName='Helvetica-Bold'
    )

    story = []

    # Briefkopf / Titel
    story.append(Paragraph("WOHNUNGSABNAHMEPROTOKOLL", title_style))
    story.append(Paragraph(
        "<b>KARE-Immobilien</b> | Talstr. 32 | 07545 Gera<br/>"
        "Tel.: 0365 / 800 49 37 | E-Mail: Info@KARE-Immobilien.de",
        subtitle_style
    ))
    
    # Allgemeine Daten
    story.append(Paragraph("1. Allgemeine Objektdaten", heading_style))
    general_data = [
        [Paragraph("<b>Objektadresse:</b>", normal_style), Paragraph(data.get('objekt_adresse', ''), normal_style)],
        [Paragraph("<b>Wohnungsnummer / Lage:</b>", normal_style), Paragraph(data.get('wohnung_lage', ''), normal_style)],
        [Paragraph("<b>Datum der Übergabe:</b>", normal_style), Paragraph(data.get('uebergabe_datum', ''), normal_style)],
        [Paragraph("<b>Vermieter / Vertreter:</b>", normal_style), Paragraph(data.get('vermieter_name', 'KARE-Immobilien'), normal_style)],
        [Paragraph("<b>Anwesender Mieter:</b>", normal_style), Paragraph(data.get('mieter_name', ''), normal_style)],
        [Paragraph("<b>Art der Übergabe:</b>", normal_style), Paragraph(data.get('uebergabe_art', 'Einzug / Auszug'), normal_style)]
    ]
    t_gen = Table(general_data, colWidths=[150, 385])
    t_gen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f7fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0'))
    ]))
    story.append(t_gen)
    story.append(Spacer(1, 10))

    # Zählerstände
    story.append(Paragraph("2. Zählerstände", heading_style))
    zaehler_data = [
        [Paragraph("<b>Zählerart / Bezeichnung</b>", bold_style), Paragraph("<b>Zählernummer</b>", bold_style), Paragraph("<b>Stand</b>", bold_style), Paragraph("<b>Einheit</b>", bold_style)]
    ]
    
    # Wasserzähler
    zaehler_data.append([Paragraph("Kaltwasserzähler", normal_style), Paragraph(data.get('kw_nr', ''), normal_style), Paragraph(data.get('kw_stand', ''), normal_style), Paragraph("m³", normal_style)])
    zaehler_data.append([Paragraph("Warmwasserzähler", normal_style), Paragraph(data.get('ww_nr', ''), normal_style), Paragraph(data.get('ww_stand', ''), normal_style), Paragraph("m³", normal_style)])
    
    # Heizungszähler (5 Stück)
    heiz_raeume = ["Wohnzimmer", "Kinderzimmer", "Flur", "Bad", "Küche"]
    for raum in heiz_raeume:
        nr = data.get(f'heiz_{raum}_nr', '')
        stand = data.get(f'heiz_{raum}_stand', '')
        zaehler_data.append([Paragraph(f"Heizungszähler ({raum})", normal_style), Paragraph(nr, normal_style), Paragraph(stand, normal_style), Paragraph("Einheiten", normal_style)])

    t_zaehler = Table(zaehler_data, colWidths=[180, 140, 115, 100])
    t_zaehler.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#edf2f7')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0'))
    ]))
    story.append(t_zaehler)
    story.append(Spacer(1, 10))

    # Schlüsselübergabe
    story.append(Paragraph("3. Schlüsselübergabe", heading_style))
    schluessel_data = [
        [Paragraph("<b>Schlüsselart</b>", bold_style), Paragraph("<b>Anzahl übergeben</b>", bold_style)]
    ]
    for s_art in ["Haustürschlüssel", "Wohnungstürschlüssel", "Briefkastenschlüssel", "Keller-/Kastenschlüssel", "Garagenschlüssel"]:
        anz = data.get(f'schl_{s_art}', '0')
        schluessel_data.append([Paragraph(s_art, normal_style), Paragraph(str(anz), normal_style)])
        
    t_schl = Table(schluessel_data, colWidths=[335, 200])
    t_schl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#edf2f7')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0'))
    ]))
    story.append(t_schl)
    story.append(Spacer(1, 10))

    # Mängel / Zustand der Räume
    story.append(Paragraph("4. Mängel und Bemerkungen", heading_style))
    maengel_text = data.get('maengel_text', 'Keine besonderen Mängel festgestellt.')
    t_maengel = Table([[Paragraph(maengel_text.replace('\n', '<br/>'), normal_style)]], colWidths=[535])
    t_maengel.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fffdfd')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 8)
    ]))
    story.append(t_maengel)
    story.append(Spacer(1, 20))

    # Unterschriften
    sig_elements = []
    sig_elements.append(Paragraph("5. Unterschriften", heading_style))
    sig_elements.append(Paragraph("Mit den Unterschriften wird die Richtigkeit der obigen Angaben sowie der Zustand der Wohnung bestätigt.", normal_style))
    sig_elements.append(Spacer(1, 15))
    
    img_v_path = data.get('sig_vermieter_path')
    img_m_path = data.get('sig_mieter_path')
    
    v_img_flow = Paragraph("<i>Keine Unterschrift erfasst</i>", normal_style)
    m_img_flow = Paragraph("<i>Keine Unterschrift erfasst</i>", normal_style)
    
    if img_v_path and os.path.exists(img_v_path):
        from reportlab.platypus import Image as RLImage
        v_img_flow = RLImage(img_v_path, width=180, height=70)
        
    if img_m_path and os.path.exists(img_m_path):
        from reportlab.platypus import Image as RLImage
        m_img_flow = RLImage(img_m_path, width=180, height=70)

    sig_table_data = [
        [v_img_flow, m_img_flow],
        [Paragraph("__________________________________________<br/>Unterschrift Vermieter (KARE-Immobilien)", normal_style),
         Paragraph("__________________________________________<br/>Unterschrift Mieter", normal_style)]
    ]
    
    t_sig = Table(sig_table_data, colWidths=[267, 268])
    t_sig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 4)
    ]))
    sig_elements.append(t_sig)
    
    story.append(KeepTogether(sig_elements))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def process_signature(canvas_result, pdf_prefix, index, y_pos):
    if canvas_result is not None and hasattr(canvas_result, "image_data"):
        img_data = canvas_result.image_data
        if img_data is not None:
            # Überprüfen ob etwas gezeichnet wurde (nicht nur transparent/schwarz)
            if np.any(img_data[:, :, 3] > 0):
                # Alpha-Kanal verarbeiten und auf weißem Hintergrund speichern
                rgba = Image.fromarray(img_data.astype('uint8'), mode="RGBA")
                background = Image.new("RGB", rgba.size, (255, 255, 255))
                background.paste(rgba, mask=rgba.split()[3])
                
                path = f"temp_sig_{pdf_prefix}_{index}.png"
                background.save(path)
                return path
    return None


def main():
    st.title("🏠 KARE-Immobilien - Wohnungsabnahmeprotokoll")
    st.markdown("Erfassung von Zählerständen, Schlüsseln und digitalen Unterschriften für Wohnungsübergaben in Gera.")

    with st.form("protokoll_form"):
        st.subheader("1. Objektdaten")
        col1, col2 = st.columns(2)
        with col1:
            objekt_adresse = st.text_input("Objektadresse (Strasse, Hausnummer, PLZ, Ort)", value="Talstr. 32, 07545 Gera")
            wohnung_lage = st.text_input("Wohnungsnummer / Lage im Gebäude", value="1. Obergeschoss links")
            vermieter_name = st.text_input("Vermieter / Vertreter", value="KARE-Immobilien")
        with col2:
            uebergabe_datum = st.text_date_input = st.text_input("Datum der Übergabe", value=datetime.now().strftime("%d.%m.%Y"))
            mieter_name = st.text_input("Name des Mieters", value="")
            uebergabe_art = st.selectbox("Art der Übergabe", ["Einzug (Übergabe)", "Auszug (Rückgabe)"])

        st.divider()
        st.subheader("2. Zählerstände")
        
        st.markdown("**Wasserzähler**")
        w_col1, w_col2, w_col3 = st.columns(3)
        with w_col1:
            kw_nr = st.text_input("Zählernummer Kaltwasser", value="")
        with w_col2:
            kw_stand = st.text_input("Zählerstand Kaltwasser", value="")
        with w_col3:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("Einheit: m³")

        w2_col1, w2_col2, w2_col3 = st.columns(3)
        with w2_col1:
            ww_nr = st.text_input("Zählernummer Warmwasser", value="")
        with w2_col2:
            ww_stand = st.text_input("Zählerstand Warmwasser", value="")
        with w2_col3:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("Einheit: m³")

        st.markdown("**Heizungszähler (5 Stück)**")
        heiz_raeume = ["Wohnzimmer", "Kinderzimmer", "Flur", "Bad", "Küche"]
        heiz_data = {}
        for raum in heiz_raeume:
            h_col1, h_col2 = st.columns(2)
            with h_col1:
                heiz_data[f'heiz_{raum}_nr'] = st.text_input(f"Zählernummer Heizung ({raum})", value="", key=f"nr_{raum}")
            with h_col2:
                heiz_data[f'heiz_{raum}_stand'] = st.text_input(f"Zählerstand Heizung ({raum})", value="", key=f"stand_{raum}")

        st.divider()
        st.subheader("3. Schlüsselübergabe")
        s_col1, s_col2, s_col3, s_col4, s_col5 = st.columns(5)
        schluessel_arten = ["Haustürschlüssel", "Wohnungstürschlüssel", "Briefkastenschlüssel", "Keller-/Kastenschlüssel", "Garagenschlüssel"]
        schluessel_Mengen = {}
        
        cols = [s_col1, s_col2, s_col3, s_col4, s_col5]
        for i, s_art in enumerate(schluessel_arten):
            with cols[i]:
                schluessel_Mengen[f'schl_{s_art}'] = st.number_input(s_art, min_value=0, max_value=20, value=2 if i<2 else 1)

        st.divider()
        st.subheader("4. Mängel, Schäden und Bemerkungen")
        maengel_text = st.text_area("Beschreibung des Zustands / festgestellte Mängel", value="Die Wohnung befindet sich in einem sauberen und ordnungsgemäßen Zustand. Keine Mängel erkennbar.")

        submitted_data = st.form_submit_button("Formulardaten speichern / aktualisieren")

    st.divider()
    st.subheader("5. Digitale Unterschriften")
    st.markdown("Bitte unterschreiben Sie direkt im jeweiligen Feld:")

    uc1, uc2 = st.columns(2)
    with uc1:
        st.markdown("**Unterschrift Vermieter (KARE-Immobilien)**")
        canvas_vermieter = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=150,
            width=350,
            drawing_mode="freedraw",
            key="canvas_v",
            return_image_data=True  # Wichtig, um den RuntimeError zu verhindern
        )

    with uc2:
        st.markdown("**Unterschrift Mieter**")
        canvas_mieter = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=150,
            width=350,
            drawing_mode="freedraw",
            key="canvas_m",
            return_image_data=True  # Wichtig, um den RuntimeError zu verhindern
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("PDF-Protokoll generieren und herunterladen", type="primary", use_container_width=True):
        # Unterschriften als Bild sichern
        sig_v_path = process_signature(canvas_vermieter, "vermieter", 1, 75)
        sig_m_path = process_signature(canvas_mieter, "mieter", 2, 75)
        
        # Daten-Dictionary zusammenbauen
        form_data = {
            'objekt_adresse': objekt_adresse,
            'wohnung_lage': wohnung_lage,
            'uebergabe_datum': uebergabe_datum,
            'vermieter_name': vermieter_name,
            'mieter_name': mieter_name if mieter_name else "Nicht angegeben",
            'uebergabe_art': uebergabe_art,
            'kw_nr': kw_nr,
            'kw_stand': kw_stand,
            'ww_nr': ww_nr,
            'ww_stand': ww_stand,
            'maengel_text': maengel_text,
            'sig_vermieter_path': sig_v_path,
            'sig_mieter_path': sig_m_path
        }
        
        # Heizungszähler hinzufügen
        for k, v in heiz_data.items():
            form_data[k] = v
            
        # Schlüssel hinzufügen
        for k, v in schluessel_Mengen.items():
            form_data[k] = str(v)

        # PDF erzeugen
        pdf_bytes = create_pdf(form_data)
        
        st.success("Wohnungsabnahmeprotokoll wurde erfolgreich erstellt!")
        st.download_button(
            label="PDF herunterladen",
            data=pdf_bytes,
            file_name=f"Wohnungsabnahmeprotokoll_{objekt_adresse.split(',')[0].strip()}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


if __name__ == "__main__":
    main()
