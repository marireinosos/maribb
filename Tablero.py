import streamlit as st
from streamlit_drawable_canvas import st_canvas

st.title("Tablero para dibujo")

with st.sidebar:
    st.subheader("Propiedades del Tablero")

    # Dimensiones del canvas
    st.subheader("Dimensiones del Tablero")

    canvas_width = st.slider(
        "Ancho del tablero",
        min_value=300,
        max_value=700,
        value=500,
        step=50
    )

    canvas_height = st.slider(
        "Alto del tablero",
        min_value=200,
        max_value=600,
        value=300,
        step=50
    )

    # Herramientas de dibujo
    drawing_mode = st.selectbox(
        "Herramienta de Dibujo:",
        (
            "freedraw",
            "line",
            "rect",
            "circle",
            "transform",
            "polygon",
            "point"
        )
    )

    # Grosor de línea
    stroke_width = st.slider(
        "Selecciona el ancho de línea",
        min_value=1,
        max_value=30,
        value=15
    )

    # Color de línea
    stroke_color = st.color_picker(
        "Color de línea",
        "#000000"
    )

    # Color de fondo
    bg_color = st.color_picker(
        "Color de fondo",
        "#FFFFFF"
    )

# Canvas
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    width=canvas_width,
    height=canvas_height,
    drawing_mode=drawing_mode,
    key="canvas",
)

# Mostrar datos del dibujo
if canvas_result.json_data is not None:
    st.subheader("Datos del dibujo")
    st.json(canvas_result.json_data)
