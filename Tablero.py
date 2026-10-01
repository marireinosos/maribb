"""
🖤 Tablero de Mari — Tablero para dibujo (modo dark)
Dibuja libre, haz figuras, elige colores neón y descarga tu dibujo.
"""

import inspect
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
    page_icon="🖤",
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
    "✏️ Lápiz libre":    "freedraw",
    "📏 Línea":          "line",
    "⬜ Rectángulo":     "rect",
    "⚪ Círculo":        "circle",
    "🔺 Polígono":       "polygon",
    "✦ Puntos":          "point",
    "✋ Mover y editar": "transform",
}

AYUDAS = {
    "freedraw":  "Mantén presionado y dibuja libre.",
    "line":      "Clic, arrastra y suelta para una línea recta.",
    "rect":      "Arrastra en diagonal para crear el rectángulo.",
    "circle":    "Arrastra desde el centro hacia afuera.",
    "polygon":   "Clic en cada esquina. Doble clic para cerrar.",
    "point":     "Cada clic deja un punto. Perfecto para estrellas.",
    "transform": "Clic en una figura para moverla, girarla o escalarla.",
}

COLORES_TRAZO = {
    "Blanco":  "#f5f5f7",
    "Violeta": "#a78bfa",
    "Cian":    "#22d3ee",
    "Rosa":    "#f472b6",
    "Lima":    "#a3e635",
    "Naranja": "#fb923c",
    "Amarillo":"#facc15",
    "Rojo":    "#f43f5e",
}

FONDOS = {
    "Negro":       "#0a0a0d",
    "Carbón":      "#18181d",
    "Grafito":     "#2a2a32",
    "Azul noche":  "#0f172a",
    "Blanco":      "#ffffff",
}

IDEAS = [
    "una ciudad de noche con luces neón",
    "una galaxia con planetas raros",
    "un gato negro bajo la luna",
    "un rayo partiendo una nube",
    "tu inicial en letra gótica",
    "un ojo que todo lo ve",
    "una calavera con flores",
    "una constelación inventada",
    "un portal a otra dimensión",
    "una tormenta en el mar",
    "un fantasma tímido",
    "unas gafas de sol reflejando un atardecer",
]


# ─────────────────────────────────────────────
# ESTILOS · super dark 🖤
# ─────────────────────────────────────────────
html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    :root {
        --bg:      #0a0a0d;
        --panel:   #121217;
        --panel2:  #18181f;
        --borde:   #26262f;
        --texto:   #ececf1;
        --suave:   #8b8b99;
        --acento:  #a78bfa;
        --acento2: #22d3ee;
    }

    .stApp, .stApp p, .stApp label, .stApp input, .stApp button, .stApp li, .stApp span {
        font-family: 'Space Grotesk', sans-serif;
    }
    .stApp {
        background:
            radial-gradient(circle at 15% -10%, rgba(167,139,250,0.14) 0%, transparent 40%),
            radial-gradient(circle at 100% 40%, rgba(34,211,238,0.08) 0%, transparent 40%),
            var(--bg);
        color: var(--texto);
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 { color: var(--texto) !important; }
    p, li, label, .stMarkdown { color: var(--texto); }
    [data-testid="stCaptionContainer"], .stCaption { color: var(--suave) !important; }
    [data-testid="stHeader"] { background: transparent; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--panel) !important;
        border-right: 1px solid var(--borde);
    }
    [data-testid="stSidebar"] h3 {
        font-size: 0.7rem !important;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--suave) !important;
        font-weight: 600 !important;
    }

    /* Cajas */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--borde) !important;
        border-radius: 20px !important;
        background: var(--panel);
    }

    /* Botones */
    .stButton > button, [data-testid="stDownloadButton"] button {
        background: var(--panel2) !important;
        color: var(--texto) !important;
        border: 1px solid var(--borde) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover, [data-testid="stDownloadButton"] button:hover {
        border-color: var(--acento) !important;
        box-shadow: 0 0 18px rgba(167,139,250,0.35);
        transform: translateY(-1px);
    }
    [data-testid="stDownloadButton"] button {
        background: linear-gradient(135deg, #7c3aed, #0891b2) !important;
        border: none !important;
    }

    /* Métricas */
    [data-testid="stMetric"] {
        background: var(--panel2);
        border: 1px solid var(--borde);
        border-radius: 16px;
        padding: 12px 16px;
    }
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        color: var(--acento) !important;
    }

    /* Encabezado */
    .portada {
        position: relative;
        overflow: hidden;
        border: 1px solid var(--borde);
        border-radius: 26px;
        padding: 38px 36px;
        background:
            linear-gradient(var(--panel), var(--panel)) padding-box,
            linear-gradient(135deg, rgba(167,139,250,0.6), rgba(34,211,238,0.4), transparent 60%) border-box;
        border: 1px solid transparent;
        font-family: 'Space Grotesk', sans-serif;
    }
    .portada .grid {
        position: absolute; inset: 0;
        background-image:
            linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px);
        background-size: 28px 28px;
        mask-image: linear-gradient(90deg, transparent, black 40%, black 70%, transparent);
    }
    .portada .tag {
        position: relative;
        display: inline-block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: var(--acento2);
        border: 1px solid rgba(34,211,238,0.35);
        border-radius: 999px;
        padding: 4px 12px;
        letter-spacing: 1px;
    }
    .portada h1 {
        position: relative;
        font-size: 3.4rem;
        font-weight: 700;
        line-height: 1;
        margin: 14px 0 8px;
        color: #ffffff;
        letter-spacing: -1.5px;
    }
    .portada h1 span {
        background: linear-gradient(90deg, #a78bfa, #22d3ee);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    .portada p {
        position: relative;
        color: var(--suave);
        margin: 0;
        font-size: 1rem;
    }
    .cursor {
        display: inline-block;
        width: 3px;
        height: 2.6rem;
        margin-left: 6px;
        vertical-align: -6px;
        background: var(--acento2);
        animation: parpadeo 1s steps(1) infinite;
    }
    @keyframes parpadeo { 50% { opacity: 0; } }

    /* Idea */
    .idea {
        background: var(--panel);
        border: 1px dashed #3a3a46;
        border-radius: 16px;
        padding: 14px 18px;
        color: var(--suave);
        font-size: 0.95rem;
        font-family: 'Space Grotesk', sans-serif;
    }
    .idea b { color: var(--texto); }
    .idea code {
        font-family: 'JetBrains Mono', monospace;
        color: var(--acento);
        background: transparent;
        margin-right: 6px;
    }

    /* Ayuda */
    .ayuda {
        background: var(--panel2);
        border-left: 3px solid var(--acento);
        border-radius: 10px;
        padding: 9px 12px;
        font-size: 0.8rem;
        color: var(--suave);
        font-family: 'Space Grotesk', sans-serif;
    }

    /* Bolitas */
    .bolitas { display: flex; flex-wrap: wrap; gap: 8px; margin: 6px 0 2px; }
    .bolita {
        width: 22px; height: 22px; border-radius: 50%;
        border: 2px solid var(--panel);
        box-shadow: 0 0 0 1px var(--borde);
    }
    .bolita.activa {
        box-shadow: 0 0 0 2px #ffffff, 0 0 14px currentColor;
        transform: scale(1.15);
    }

    /* Barra del tablero */
    .barra {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: var(--suave);
        margin-bottom: 6px;
    }
    .barra .puntos span {
        display: inline-block; width: 10px; height: 10px; border-radius: 50%;
        margin-right: 5px;
    }
    iframe[title="streamlit_drawable_canvas.st_canvas"] {
        border-radius: 14px;
        box-shadow: 0 0 0 1px var(--borde), 0 20px 50px rgba(0,0,0,0.6);
    }

    .footer {
        text-align: center;
        margin-top: 34px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #55555f;
        letter-spacing: 1px;
    }
    .footer b { color: var(--acento); font-weight: 600; }
</style>
""")


# ─────────────────────────────────────────────
# PANEL LATERAL · propiedades del tablero
# ─────────────────────────────────────────────
with st.sidebar:
    html("""
    <div style="font-family:'Space Grotesk',sans-serif; padding-top:4px;">
        <div style="font-size:1.6rem; font-weight:700; color:#ffffff; letter-spacing:-0.5px;">
            Propiedades
        </div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#8b8b99;">
            // del tablero
        </div>
    </div>
    """)
    st.divider()

    # ── Herramienta ──
    st.markdown("### Herramienta")
    herramienta_sel = st.selectbox("Herramienta de dibujo", list(HERRAMIENTAS.keys()),
                                   label_visibility="collapsed")
    drawing_mode = HERRAMIENTAS[herramienta_sel]
    html(f'<div class="ayuda">{AYUDAS[drawing_mode]}</div>')

    stroke_width = st.slider("Grosor de la línea", 1, 30, 5)
    point_radius = st.slider("Tamaño de los puntos", 1, 25, 5) if drawing_mode == "point" else 5

    st.divider()

    # ── Color ──
    st.markdown("### Color del trazo")
    color_nombre = st.selectbox("Color", list(COLORES_TRAZO.keys()) + ["Otro…"],
                                index=1, label_visibility="collapsed")
    if color_nombre == "Otro…":
        stroke_color = st.color_picker("Elige tu color", "#a78bfa")
    else:
        stroke_color = COLORES_TRAZO[color_nombre]

    html('<div class="bolitas">' + "".join(
        f'<div class="bolita {"activa" if c == stroke_color else ""}" '
        f'style="background:{c}; color:{c};" title="{n}"></div>'
        for n, c in COLORES_TRAZO.items()
    ) + "</div>")

    rellenar = st.toggle("Rellenar figuras", value=False)
    opacidad = st.slider("Opacidad del relleno", 0.1, 1.0, 0.3, 0.05, disabled=not rellenar)

    st.divider()

    # ── Fondo ──
    st.markdown("### Fondo")
    fondo_nombre = st.selectbox("Color de fondo", list(FONDOS.keys()) + ["Otro…"],
                                label_visibility="collapsed")
    bg_color = st.color_picker("Color del fondo", "#0a0a0d") if fondo_nombre == "Otro…" \
        else FONDOS[fondo_nombre]

    st.divider()

    # ── Dimensiones ──
    st.markdown("### Dimensiones")
    canvas_width = st.slider("Ancho del tablero", 300, 900, 700, 50)
    canvas_height = st.slider("Alto del tablero", 200, 700, 450, 50)

    st.divider()
    tiempo_real = st.toggle("Actualizar en tiempo real", value=True)


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
    <div class="grid"></div>
    <span class="tag">● tablero_para_dibujo.py</span>
    <h1>Tablero de <span>Mari</span><span class="cursor"></span></h1>
    <p>Un lienzo oscuro, colores que brillan y cero reglas.</p>
</div>
""")

st.write("")


# ─────────────────────────────────────────────
# IDEA PARA DIBUJAR
# ─────────────────────────────────────────────
if "idea" not in st.session_state:
    st.session_state.idea = random.choice(IDEAS)

col_idea, col_btn = st.columns([5, 1])
with col_idea:
    html(f'<div class="idea"><code>&gt; idea:</code><b>{st.session_state.idea}</b></div>')
with col_btn:
    if st.button("🎲 Otra", use_container_width=True):
        st.session_state.idea = random.choice([i for i in IDEAS if i != st.session_state.idea])
        st.rerun()

st.write("")


# ─────────────────────────────────────────────
# TABLERO
# ─────────────────────────────────────────────
col_tablero, col_info = st.columns([3, 1], gap="large")

with col_tablero:
    with st.container(border=True):
        html(f"""
        <div class="barra">
            <span class="puntos"><span style="background:#f43f5e"></span><span style="background:#facc15"></span><span style="background:#a3e635"></span></span>
            <span>{herramienta_sel} · {stroke_width}px</span>
            <span>{canvas_width}×{canvas_height}</span>
        </div>
        """)
        opciones = dict(
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
        # Usamos solo las opciones que acepta la versión instalada de la librería
        aceptadas = inspect.signature(st_canvas).parameters
        opciones = {k: v for k, v in opciones.items() if k in aceptadas}

        try:
            canvas_result = st_canvas(**opciones)
        except Exception as e:
            st.error("El tablero no pudo cargar 😢 Revisa las versiones en requirements.txt.")
            st.code(f"{type(e).__name__}: {e}")
            st.stop()

        if "display_toolbar" in aceptadas:
            st.caption("↩ deshacer · ↪ rehacer · 🗑 borrar todo → íconos debajo del tablero")


# ─────────────────────────────────────────────
# INFO DEL DIBUJO + DESCARGA
# ─────────────────────────────────────────────
NOMBRES_FIGURAS = {
    "path": "Trazos",
    "line": "Líneas",
    "rect": "Rectángulos",
    "circle": "Círculos",
    "polygon": "Polígonos",
    "path_polygon": "Polígonos",
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
                nombre = NOMBRES_FIGURAS.get(o.get("type", ""), "Otros")
                conteo[nombre] = conteo.get(nombre, 0) + 1
            for nombre, n in sorted(conteo.items(), key=lambda x: -x[1]):
                st.write(f"`{n:02d}` {nombre}")

            colores_usados = {o.get("stroke") for o in objetos if o.get("stroke")}
            if colores_usados:
                st.caption("Paleta usada")
                html('<div class="bolitas">' + "".join(
                    f'<div class="bolita" style="background:{c};"></div>' for c in colores_usados
                ) + "</div>")

            st.write("")
            if canvas_result.image_data is not None:
                dibujo = Image.fromarray(canvas_result.image_data.astype(np.uint8), "RGBA")
                fondo = Image.new("RGBA", dibujo.size, bg_color)
                final = Image.alpha_composite(fondo, dibujo).convert("RGB")
                buf = io.BytesIO()
                final.save(buf, format="PNG")
                st.download_button(
                    "⬇ Descargar PNG",
                    data=buf.getvalue(),
                    file_name="dibujo_de_mari.png",
                    mime="image/png",
                    use_container_width=True,
                )
        else:
            st.caption("El lienzo está vacío. Empieza a dibujar →")


# ─────────────────────────────────────────────
# PIE
# ─────────────────────────────────────────────
html('<div class="footer">hecho en clase por <b>Mari</b> · python + streamlit</div>')
