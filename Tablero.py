"""
🎨 Tablero de Mari — Tablero para dibujo
Dibuja libre, haz figuras, elige colores y descarga tu dibujo.
"""

import io
import random

import numpy as np
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas


# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Tablero de Mari",
    page_icon="🎨",
    layout="wide",
)


def html(codigo):
    """Muestra HTML/CSS. Usa st.html (Streamlit nuevo) y si no existe, st.markdown."""
    if hasattr(st, "html"):
        st.html(codigo)
    else:
        st.markdown(codigo, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# OPCIONES ✏️ (puedes agregar colores o ideas aquí)
# ─────────────────────────────────────────────
HERRAMIENTAS = {
    "✏️ Lápiz libre":       "freedraw",
    "📏 Línea":             "line",
    "⬜ Rectángulo":        "rect",
    "⚪ Círculo":           "circle",
    "🔺 Polígono":          "polygon",
    "🫧 Puntos":            "point",
    "✋ Mover y editar":    "transform",
}

AYUDAS = {
    "freedraw":  "Mantén presionado y dibuja como en papel.",
    "line":      "Haz clic, arrastra y suelta para trazar una línea recta.",
    "rect":      "Arrastra en diagonal para crear el rectángulo.",
    "circle":    "Arrastra desde el centro hacia afuera.",
    "polygon":   "Clic en cada esquina. Doble clic para cerrar la figura.",
    "point":     "Cada clic deja un puntito. ¡Ideal para estrellas o confeti!",
    "transform": "Haz clic sobre una figura para moverla, girarla o cambiarle el tamaño.",
}

COLORES_TRAZO = {
    "Café":       "#6f4e37",
    "Rosa":       "#d99aa0",
    "Fucsia":     "#e75480",
    "Durazno":    "#f4a582",
    "Lila":       "#b39ddb",
    "Salvia":     "#9cbf9b",
    "Cielo":      "#90caf9",
    "Negro":      "#2b2b2b",
}

FONDOS = {
    "Crema":        "#fffaf5",
    "Beige":        "#f4e9dd",
    "Rosa pálido":  "#fbe7e7",
    "Blanco":       "#ffffff",
    "Café oscuro":  "#3e2a1f",
}

IDEAS = [
    "una taza de café con corazones saliendo ☕",
    "un gatito durmiendo en una nube ☁️",
    "tu outfit favorito 👗",
    "un atardecer en Medellín 🌄",
    "una flor gigante con cara feliz 🌸",
    "un helado de tres sabores 🍦",
    "tu lugar favorito del mundo 🗺️",
    "un moño con brillitos 🎀",
    "una casa de muñecas 🏡",
    "tu animal favorito usando gafas 🕶️",
    "un pastel de cumpleaños 🎂",
    "una ventana con lluvia afuera 🌧️",
]


# ─────────────────────────────────────────────
# ESTILOS · beige, rosado y café 🤎🎀
# ─────────────────────────────────────────────
html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Great+Vibes&family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&family=Poppins:wght@300;400;500;600&display=swap');

    .stApp, .stApp p, .stApp label, .stApp input, .stApp button, .stApp li {
        font-family: 'Poppins', sans-serif;
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        font-family: 'Cormorant Garamond', serif !important;
        color: #6f4e37 !important;
        font-weight: 600 !important;
    }
    .stApp {
        background:
            radial-gradient(circle at 0% 0%, #f9e4e4 0%, transparent 35%),
            radial-gradient(circle at 100% 30%, #f3e2d2 0%, transparent 40%),
            #f8f0e7;
    }
    p, li, label { color: #7d5f4a; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #fffaf5 !important;
        border-right: 1px solid #ead8c4;
    }
    [data-testid="stSidebar"] h3 {
        font-family: 'Poppins', sans-serif !important;
        font-size: 0.72rem !important;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: #b8977c !important;
    }

    /* Cajas */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #ead8c4 !important;
        border-radius: 28px !important;
        background: #fffaf5;
        box-shadow: 0 10px 28px rgba(111,78,55,0.07);
    }

    /* Botones */
    .stButton > button, [data-testid="stDownloadButton"] button {
        background: linear-gradient(135deg, #e8b4b8, #d99aa0) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 999px !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover, [data-testid="stDownloadButton"] button:hover {
        background: linear-gradient(135deg, #b8977c, #6f4e37) !important;
        transform: translateY(-2px);
    }

    /* Métricas */
    [data-testid="stMetric"] {
        background: #fffaf5;
        border: 1px solid #ead8c4;
        border-radius: 22px;
        padding: 12px 16px;
        text-align: center;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Cormorant Garamond', serif;
        color: #d99aa0 !important;
    }

    /* Encabezado */
    .portada {
        background: linear-gradient(135deg, #fffaf5 0%, #f7e3dc 50%, #efd9c7 100%);
        border: 1px solid #ead8c4;
        border-radius: 36px;
        padding: 40px 36px 34px;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 16px 44px rgba(111,78,55,0.12);
        font-family: 'Poppins', sans-serif;
    }
    .portada .mini {
        font-size: 0.72rem;
        letter-spacing: 5px;
        text-transform: uppercase;
        color: #9c7a60;
    }
    .portada .firma {
        font-family: 'Great Vibes', cursive;
        font-size: 4.4rem;
        line-height: 1.05;
        color: #6f4e37;
        margin-top: 6px;
    }
    .portada .firma span { color: #d99aa0; }
    .portada p {
        color: #8a6a55;
        margin: 6px 0 0;
        font-size: 0.98rem;
    }
    .deco {
        position: absolute;
        font-size: 1.4rem;
        opacity: 0.75;
        animation: flotar 5s ease-in-out infinite;
    }
    @keyframes flotar {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50%      { transform: translateY(-10px) rotate(10deg); }
    }

    /* Idea del día */
    .idea {
        background: #fbe7e7;
        border: 1px dashed #d99aa0;
        border-radius: 22px;
        padding: 14px 20px;
        text-align: center;
        color: #6f4e37;
        font-family: 'Poppins', sans-serif;
        font-size: 0.95rem;
    }
    .idea b {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 1.3rem;
    }

    /* Ayuda de la herramienta */
    .ayuda {
        background: #f4e9dd;
        border-radius: 16px;
        padding: 10px 14px;
        font-size: 0.82rem;
        color: #6f4e37;
        font-family: 'Poppins', sans-serif;
    }

    /* Bolitas de color */
    .bolitas { display: flex; flex-wrap: wrap; gap: 8px; margin: 4px 0 2px; }
    .bolita {
        width: 26px; height: 26px; border-radius: 50%;
        border: 2px solid #fffaf5;
        box-shadow: 0 0 0 1px #ead8c4;
    }
    .bolita.activa { box-shadow: 0 0 0 2px #6f4e37; transform: scale(1.12); }

    /* Marco del tablero */
    .marco-titulo {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'Poppins', sans-serif;
        color: #9c7a60;
        font-size: 0.8rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    iframe[title="streamlit_drawable_canvas.st_canvas"] {
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(111,78,55,0.15);
    }

    .footer {
        text-align: center;
        margin-top: 30px;
        font-family: 'Poppins', sans-serif;
    }
    .footer .firma {
        font-family: 'Great Vibes', cursive;
        font-size: 2.2rem;
        color: #6f4e37;
    }
    .footer p {
        font-size: 0.75rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #b8977c;
        margin: 0;
    }
</style>
""")


# ─────────────────────────────────────────────
# PANEL LATERAL · propiedades del tablero
# ─────────────────────────────────────────────
with st.sidebar:
    html("""
    <div style="text-align:center; padding-top:6px;">
        <div style="font-family:'Great Vibes',cursive; font-size:2.3rem; color:#6f4e37;">Mi estuche</div>
        <div style="font-family:'Poppins',sans-serif; font-size:0.7rem; letter-spacing:3px;
                    text-transform:uppercase; color:#b8977c;">propiedades del tablero</div>
    </div>
    """)
    st.divider()

    # ── Herramienta ──
    st.markdown("### 🖌️ Herramienta")
    herramienta_sel = st.selectbox("Herramienta de dibujo", list(HERRAMIENTAS.keys()),
                                   label_visibility="collapsed")
    drawing_mode = HERRAMIENTAS[herramienta_sel]
    html(f'<div class="ayuda">💡 {AYUDAS[drawing_mode]}</div>')

    stroke_width = st.slider("Grosor de la línea", 1, 30, 6)
    if drawing_mode == "point":
        point_radius = st.slider("Tamaño de los puntos", 1, 25, 6)
    else:
        point_radius = 6

    st.divider()

    # ── Colores ──
    st.markdown("### 🎨 Color del trazo")
    color_nombre = st.radio("Color", list(COLORES_TRAZO.keys()) + ["🌈 Otro"],
                            horizontal=True, label_visibility="collapsed")
    if color_nombre == "🌈 Otro":
        stroke_color = st.color_picker("Elige tu color", "#e75480")
    else:
        stroke_color = COLORES_TRAZO[color_nombre]

    bolitas = "".join(
        f'<div class="bolita {"activa" if c == stroke_color else ""}" '
        f'style="background:{c};" title="{n}"></div>'
        for n, c in COLORES_TRAZO.items()
    )
    html(f'<div class="bolitas">{bolitas}</div>')

    rellenar = st.toggle("Rellenar figuras", value=False,
                         help="Para rectángulos, círculos y polígonos")
    opacidad = st.slider("Transparencia del relleno", 0.1, 1.0, 0.35, 0.05,
                         disabled=not rellenar)

    st.divider()

    # ── Fondo ──
    st.markdown("### 🧺 Fondo")
    fondo_nombre = st.selectbox("Color de fondo", list(FONDOS.keys()) + ["🌈 Otro"],
                                label_visibility="collapsed")
    if fondo_nombre == "🌈 Otro":
        bg_color = st.color_picker("Color del fondo", "#fffaf5")
    else:
        bg_color = FONDOS[fondo_nombre]

    st.divider()

    # ── Dimensiones ──
    st.markdown("### 📐 Dimensiones del tablero")
    canvas_width = st.slider("Ancho del tablero", 300, 900, 700, 50)
    canvas_height = st.slider("Alto del tablero", 200, 700, 450, 50)

    st.divider()
    tiempo_real = st.toggle("Actualizar mientras dibujo", value=True,
                            help="Si se pone lenta, apágalo y verás un botón para enviar el dibujo.")


def hex_a_rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


fill_color = hex_a_rgba(stroke_color, opacidad) if rellenar else "rgba(0, 0, 0, 0)"


# ─────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────
html("""
<div class="portada">
    <span class="deco" style="top:24px; left:36px;">🎨</span>
    <span class="deco" style="top:40px; right:52px; animation-delay:1.2s;">🖌️</span>
    <span class="deco" style="bottom:22px; left:18%; animation-delay:2s;">🎀</span>
    <span class="deco" style="bottom:26px; right:20%; animation-delay:1.6s;">✨</span>
    <div class="mini">Tablero para dibujo</div>
    <div class="firma">Tablero de <span>Mari</span></div>
    <p>Elige tus colores, tu herramienta favorita y deja volar la imaginación 🤎</p>
</div>
""")

st.write("")


# ─────────────────────────────────────────────
# IDEA PARA DIBUJAR
# ─────────────────────────────────────────────
if "idea" not in st.session_state:
    st.session_state.idea = random.choice(IDEAS)

col_idea, col_btn = st.columns([4, 1], vertical_alignment="center")
with col_idea:
    html(f'<div class="idea">¿No sabes qué dibujar? Intenta con… <b>{st.session_state.idea}</b></div>')
with col_btn:
    if st.button("🎲 Otra idea", use_container_width=True):
        opciones = [i for i in IDEAS if i != st.session_state.idea]
        st.session_state.idea = random.choice(opciones)
        st.rerun()

st.write("")


# ─────────────────────────────────────────────
# TABLERO
# ─────────────────────────────────────────────
col_tablero, col_info = st.columns([3, 1], gap="large")

with col_tablero:
    with st.container(border=True):
        html(f"""
        <div class="marco-titulo">
            <span>✏️ {herramienta_sel}</span>
            <span>{canvas_width} × {canvas_height} px</span>
        </div>
        """)
        canvas_result = st_canvas(
            fill_color=fill_color,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color=bg_color,
            height=canvas_height,
            width=canvas_width,
            drawing_mode=drawing_mode,
            point_display_radius=point_radius,
            update_streamlit=tiempo_real,
            display_toolbar=True,
            key=f"tablero_{canvas_width}_{canvas_height}",
        )
        st.caption("↩️ Deshacer · ↪️ Rehacer · 🗑️ Borrar todo: usa los íconos debajo del tablero.")


# ─────────────────────────────────────────────
# INFO DEL DIBUJO + DESCARGA
# ─────────────────────────────────────────────
NOMBRES_FIGURAS = {
    "path": "✏️ Trazos",
    "line": "📏 Líneas",
    "rect": "⬜ Rectángulos",
    "circle": "⚪ Círculos",
    "polygon": "🔺 Polígonos",
    "path_polygon": "🔺 Polígonos",
}

with col_info:
    with st.container(border=True):
        st.markdown("### Tu dibujo")

        objetos = []
        if canvas_result.json_data is not None:
            objetos = canvas_result.json_data.get("objects", [])

        st.metric("Elementos", len(objetos))

        if objetos:
            conteo = {}
            for o in objetos:
                nombre = NOMBRES_FIGURAS.get(o.get("type", ""), "🫧 Otros")
                conteo[nombre] = conteo.get(nombre, 0) + 1
            for nombre, n in sorted(conteo.items(), key=lambda x: -x[1]):
                st.write(f"{nombre}: **{n}**")

            colores_usados = {o.get("stroke") for o in objetos if o.get("stroke")}
            if colores_usados:
                st.caption("Colores que usaste")
                html('<div class="bolitas">' + "".join(
                    f'<div class="bolita" style="background:{c};"></div>' for c in colores_usados
                ) + "</div>")
        else:
            st.caption("Aún no has dibujado nada… ¡el tablero te espera! 🤎")

        st.write("")

        # Descargar como PNG (pegamos el dibujo sobre el color de fondo)
        if canvas_result.image_data is not None and objetos:
            dibujo = Image.fromarray(canvas_result.image_data.astype(np.uint8), "RGBA")
            fondo = Image.new("RGBA", dibujo.size, bg_color)
            final = Image.alpha_composite(fondo, dibujo).convert("RGB")

            buf = io.BytesIO()
            final.save(buf, format="PNG")
            st.download_button(
                "💾 Descargar dibujo",
                data=buf.getvalue(),
                file_name="dibujo_de_mari.png",
                mime="image/png",
                use_container_width=True,
            )


# ─────────────────────────────────────────────
# PIE
# ─────────────────────────────────────────────
html("""
<div class="footer">
    <div class="firma">con cariño, Mari</div>
    <p>hecho en clase con python y streamlit ☕</p>
</div>
""")
