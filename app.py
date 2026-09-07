from datetime import datetime
import streamlit as st
from streamlit_drawable_canvas import st_canvas

st.set_page_config(
    page_title="Wohnungsabnahmeprotokoll - KARE-Immobilien", layout="wide"
)

st.title("🏠 Wohnungsabnahmeprotokoll")
st.markdown(
    "**KARE-Immobilien** | Talstr. 32, 07545 Gera | Tel.: 0365 / 800 49 37 |"
    " E-Mail: Info@KARE-Immobilien.de"
)
st.markdown("---")

# --- 1. STAMMDATEN ---
with st.container(border=True):
  st.subheader("1. Stammdaten & Objekt")
  col1, col2 = st.columns(2)
  with col1:
    vermieter = st.text_input(
        "Vermieter / Vertreter", value="KARE-Immobilien"
    )
    strasse = st.text_input(
        "Objektadresse (Straße, Hausnr.)", value="Beispielstraße 1"
    )
    plz_ort = st.text_input("PLZ, Ort", value="07545 Gera")
  with col2:
    mieter = st.text_input("Mieter (Name)")
    abnahme_datum = st.date_input("Datum der Abnahme", value=datetime.today())

# --- 2. ZÄHLERSTÄNDE ---
with st.container(border=True):
  st.subheader("2. Zählerstände")

  col_w1, col_w2 = st.columns(2)
  with col_w1:
    z_kalt = st.text_input(
        "Kaltwasserzähler", placeholder="Zähler-Nr. & Stand in m³"
    )
  with col_w2:
    z_warm = st.text_input(
        "Warmwasserzähler", placeholder="Zähler-Nr. & Stand in m³"
    )

  st.markdown("**Heizungszähler (Heizkostenverteiler)**")
  heiz_raeume = ["Wohnzimmer", "Kinderzimmer", "Flur", "Bad", "Küche"]
  heiz_staende = {}
  cols = st.columns(len(heiz_raeume))
  for i, raum in enumerate(heiz_raeume):
    with cols[i]:
      heiz_staende[raum] = st.text_input(
          raum, placeholder="Stand", key=f"heiz_{raum}"
      )

# --- 3. MÄNGEL & ZUSTAND ---
with st.container(border=True):
  st.subheader("3. Zustand und Mängel")
  maengel = st.text_area(
      "Festgestellte Mängel / Sondervereinbarungen",
      placeholder=(
          "z.B. Bohrlöcher im Flur verschließen, Wandfarbe im Wohnzimmer..."
      ),
  )

# --- 4. SCHLÜSSELÜBERGABE ---
with st.container(border=True):
  st.subheader("4. Schlüsselübergabe")
  c1, c2, c3 = st.columns(3)
  with c1:
    schluessel_haus = st.number_input(
        "Haus-/Hauseingangstür", min_value=0, value=2
    )
  with c2:
    schluessel_wohnung = st.number_input("Wohnungstür", min_value=0, value=2)
  with c3:
    schluessel_keller = st.number_input("Keller / Sonstige", min_value=0, value=1)

# --- 5. UNTERSCHRIFTEN ---
with st.container(border=True):
  st.subheader("✍️ 5. Unterschriften")
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
        update_streamlit=True,
        realtime_update=True,
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
        update_streamlit=True,
        realtime_update=True,
        key="canvas_mieter",
    )

st.markdown("---")
if st.button("Protokoll generieren", type="primary"):
  if not mieter:
    st.warning("Bitte geben Sie den Namen des Mieters ein.")
  else:
    st.success("Protokoll erfolgreich erstellt und Unterschriften geladen!")
    # Hier kann die PDF-Generierung per ReportLab oder FPDF anknüpfen
