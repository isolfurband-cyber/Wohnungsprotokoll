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
        background_color="#f0f2f6",  # <--- Hier von "#000000" auf "#f0f2f6" geändert
        height=150,
        width=280,
        drawing_mode="freedraw",
        key="canvas_mieter",
    )
