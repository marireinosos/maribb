"""
🖤 Tablero de Mari — Tablero inteligente
Dibujas una figura o un número y la app adivina qué es.

· Figuras: usa visión por computador (OpenCV) para encontrar el contorno
  del dibujo, contar sus esquinas y medir qué tan redondo es.
· Números: usa un modelo de aprendizaje automático (scikit-learn) entrenado
  con 1.797 números escritos a mano.
· Constelaciones: compara tus estrellas con constelaciones reales, girándolas
  y escalándolas hasta encontrar la que mejor encaja.
"""

import inspect
import io
import random

import cv2
import numpy as np
import streamlit as st
from PIL import Image
from scipy.optimize import linear_sum_assignment
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
# DATOS
# ─────────────────────────────────────────────
FIGURAS = {
    "circulo":    ("⚪", "Círculo"),
    "ovalo":      ("🥚", "Óvalo"),
    "triangulo":  ("🔺", "Triángulo"),
    "cuadrado":   ("⬜", "Cuadrado"),
    "rectangulo": ("▭", "Rectángulo"),
    "pentagono":  ("⬟", "Pentágono"),
    "hexagono":   ("⬢", "Hexágono"),
    "estrella":   ("⭐", "Estrella"),
    "linea":      ("📏", "Línea"),
    "libre":      ("🌀", "Figura libre"),
    "pequeno":    ("🔍", "Muy pequeño"),
}

# Figuras que salen en el modo reto
RETOS_FIGURA = ["circulo", "triangulo", "cuadrado", "rectangulo", "estrella", "ovalo"]

# Constelaciones: coordenadas aproximadas de sus estrellas y las líneas que las unen
CONSTELACIONES = {
    "osa_mayor": dict(
        nombre="Osa Mayor", emoji="🐻",
        dato="Sus 7 estrellas forman un 'cucharón'. Dos de ellas señalan hacia la Estrella Polar.",
        puntos=[(0, 0), (0, 1), (1.3, 1.2), (1.4, 0.3), (2.3, 0.1), (3.1, -0.1), (4.2, 0.4)],
        lineas=[(0, 1), (1, 2), (2, 3), (3, 0), (3, 4), (4, 5), (5, 6)]),
    "casiopea": dict(
        nombre="Casiopea", emoji="👑",
        dato="Tiene forma de W (o de M). En la mitología griega era una reina muy vanidosa.",
        puntos=[(0, 0), (1, 1), (2, 0.35), (3, 1.1), (4, 0)],
        lineas=[(0, 1), (1, 2), (2, 3), (3, 4)]),
    "orion": dict(
        nombre="Orión", emoji="🏹",
        dato="El cazador. Las tres estrellas del centro son su cinturón: las 'Tres Marías'.",
        puntos=[(0, 0), (2.2, 0.3), (0.9, 2.2), (1.2, 2.0), (1.5, 1.8), (0.4, 4.0), (2.5, 3.8)],
        lineas=[(0, 1), (0, 2), (1, 4), (2, 3), (3, 4), (2, 5), (4, 6)]),
    "tres_marias": dict(
        nombre="Tres Marías", emoji="✨",
        dato="Tres estrellas en línea: el cinturón de Orión. Se ven muy bien desde Colombia.",
        puntos=[(0, 0), (1, -0.35), (2, -0.7)],
        lineas=[(0, 1), (1, 2)]),
    "cruz_del_sur": dict(
        nombre="Cruz del Sur", emoji="✝️",
        dato="La constelación más pequeña del cielo. Su brazo largo apunta hacia el polo sur.",
        puntos=[(0, 0), (0.1, 2.2), (-1.0, 0.9), (0.9, 1.1)],
        lineas=[(0, 1), (2, 3)]),
    "escorpio": dict(
        nombre="Escorpio", emoji="🦂",
        dato="Un escorpión con la cola curvada. Su estrella roja, Antares, es su corazón.",
        puntos=[(-0.5, 0.3), (0.4, -0.4), (0, 0), (0.2, 0.8), (0.6, 1.5), (0.9, 2.3),
                (1.0, 3.0), (1.4, 3.7), (2.1, 3.9), (2.7, 3.5), (2.6, 2.9)],
        lineas=[(0, 2), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10)]),
    "leo": dict(
        nombre="Leo", emoji="🦁",
        dato="El león. Su cabeza parece un signo de interrogación al revés.",
        puntos=[(0, 3), (0.2, 2.2), (0.5, 1.5), (0.4, 0.8), (-0.1, 0.4), (-0.6, 0.6),
                (2.6, 1.4), (3.8, 2.2), (2.7, 2.4)],
        lineas=[(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (2, 6), (6, 7), (7, 8), (8, 0)]),
    "lira": dict(
        nombre="Lira", emoji="🎵",
        dato="Un arpa pequeña. Su estrella Vega es una de las más brillantes del cielo.",
        puntos=[(0, 0), (0.3, 0.7), (0.9, 0.8), (0.6, 1.8), (0.0, 1.7)],
        lineas=[(0, 1), (1, 2), (2, 3), (3, 4), (4, 1)]),
}

COLORES_TRAZO = {
    "Blanco":   "#f5f5f7",
    "Violeta":  "#a78bfa",
    "Cian":     "#22d3ee",
    "Rosa":     "#f472b6",
    "Lima":     "#a3e635",
    "Amarillo": "#facc15",
}

FONDOS = {
    "Negro":      "#0a0a0d",
    "Carbón":     "#18181d",
    "Azul noche": "#0f172a",
}


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
        --ok:      #a3e635;
        --mal:     #f43f5e;
    }

    .stApp, .stApp p, .stApp label, .stApp input, .stApp button, .stApp li {
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
    [data-testid="stCaptionContainer"] { color: var(--suave) !important; }
    [data-testid="stHeader"] { background: transparent; }

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

    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--borde) !important;
        border-radius: 20px !important;
        background: var(--panel);
    }

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
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7c3aed, #0891b2) !important;
        border: none !important;
    }

    /* Selector de modo */
    [data-testid="stRadio"] [role="radiogroup"] { gap: 10px; flex-wrap: wrap; }
    [data-testid="stRadio"] [role="radiogroup"] label {
        background: var(--panel);
        border: 1px solid var(--borde);
        border-radius: 12px;
        padding: 8px 16px;
    }

    /* Encabezado */
    .portada {
        position: relative;
        overflow: hidden;
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
    }
    .portada h1 {
        position: relative;
        font-size: 3.3rem;
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
    .portada p { position: relative; color: var(--suave); margin: 0; font-size: 1rem; }
    .cursor {
        display: inline-block; width: 3px; height: 2.5rem; margin-left: 6px;
        vertical-align: -6px; background: var(--acento2);
        animation: parpadeo 1s steps(1) infinite;
    }
    @keyframes parpadeo { 50% { opacity: 0; } }

    /* Reto */
    .reto {
        display: flex; align-items: center; justify-content: space-between; gap: 14px;
        background: var(--panel);
        border: 1px dashed #3a3a46;
        border-radius: 16px;
        padding: 14px 20px;
        font-family: 'Space Grotesk', sans-serif;
        color: var(--suave);
    }
    .reto b { color: #ffffff; font-size: 1.25rem; }
    .reto .score {
        font-family: 'JetBrains Mono', monospace;
        color: var(--ok);
        font-size: 1rem;
        white-space: nowrap;
    }

    /* Barra del tablero */
    .barra {
        display: flex; justify-content: space-between; align-items: center;
        font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
        color: var(--suave); margin-bottom: 6px;
    }
    .barra .puntos span {
        display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px;
    }
    iframe[title="streamlit_drawable_canvas.st_canvas"] {
        border-radius: 14px;
        box-shadow: 0 0 0 1px var(--borde), 0 20px 50px rgba(0,0,0,0.6);
    }

    /* Resultado */
    .resultado {
        text-align: center;
        padding: 18px 10px 10px;
        font-family: 'Space Grotesk', sans-serif;
        animation: aparecer 0.4s ease;
    }
    .resultado .mini {
        font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
        color: var(--suave); letter-spacing: 1px;
    }
    .resultado .emoji { font-size: 3.6rem; line-height: 1.2; margin-top: 6px; }
    .resultado .nombre {
        font-size: 2.2rem; font-weight: 700; color: #ffffff; letter-spacing: -0.5px;
    }
    .resultado .conf {
        font-family: 'JetBrains Mono', monospace; color: var(--acento2); font-size: 0.85rem;
    }
    .resultado.vacio .nombre { color: #4a4a55; font-size: 1.4rem; }
    @keyframes aparecer {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .veredicto {
        border-radius: 14px; padding: 12px; text-align: center;
        font-family: 'Space Grotesk', sans-serif; font-weight: 600;
    }
    .veredicto.ok  { background: rgba(163,230,53,0.12); color: var(--ok);  border: 1px solid rgba(163,230,53,0.4); }
    .veredicto.mal { background: rgba(244,63,94,0.10); color: var(--mal); border: 1px solid rgba(244,63,94,0.4); }

    /* Barras de probabilidad */
    .prob { margin: 8px 0; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }
    .prob .top { display: flex; justify-content: space-between; color: var(--texto); margin-bottom: 4px; }
    .prob .fondo { background: var(--panel2); border-radius: 999px; height: 8px; overflow: hidden; }
    .prob .lleno { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #7c3aed, #22d3ee); }

    /* Datos técnicos */
    .datos { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: var(--suave); }
    .datos div { display: flex; justify-content: space-between; padding: 4px 0;
                 border-bottom: 1px solid var(--borde); }
    .datos b { color: var(--texto); font-weight: 600; }

    .footer {
        text-align: center; margin-top: 34px;
        font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
        color: #55555f; letter-spacing: 1px;
    }
    .footer b { color: var(--acento); font-weight: 600; }
</style>
""")


# ─────────────────────────────────────────────
# RECONOCIMIENTO 🧠
# ─────────────────────────────────────────────
def mascara_de(image_data, bg_hex):
    """Devuelve True donde hay dibujo y False donde está el fondo."""
    img = image_data.astype(np.int16)
    alpha = img[:, :, 3]
    if alpha.min() < 255:
        return alpha > 50
    h = bg_hex.lstrip("#")
    bg = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)])
    return np.abs(img[:, :, :3] - bg).sum(axis=2) > 60


def clasificar_figura(mask):
    """Encuentra el contorno más grande y decide qué figura es."""
    m = mask.astype(np.uint8) * 255
    # cierra pequeños huecos del trazo a mano
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8), iterations=2)
    contornos, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos:
        return None

    c = max(contornos, key=cv2.contourArea)
    area = cv2.contourArea(c)
    perimetro = cv2.arcLength(c, True)
    x, y, w, h = cv2.boundingRect(c)

    if w * h < 900:
        return dict(clave="pequeno", contorno=c, vertices=0, circ=0.0, solidez=0.0, conf=0.0)

    relleno = area / (w * h)
    solidez = area / max(cv2.contourArea(cv2.convexHull(c)), 1)
    circ = 4 * np.pi * area / (perimetro ** 2) if perimetro else 0.0
    aprox = cv2.approxPolyDP(c, 0.03 * perimetro, True)
    v = len(aprox)
    proporcion = w / h
    limpio = float(np.clip(1 - abs(area - cv2.contourArea(aprox)) / max(area, 1) * 3, 0.4, 0.99))

    if relleno < 0.12:
        clave, conf = "linea", 0.80
    elif solidez < 0.75 and v >= 8:
        clave, conf = "estrella", float(np.clip(1.4 - solidez, 0.5, 0.97))
    elif circ > 0.80 and v > 6:
        clave, conf = "circulo", float(np.clip(circ, 0, 0.99))
    elif v == 3:
        clave, conf = "triangulo", limpio
    elif v == 4:
        clave = "cuadrado" if 0.82 <= proporcion <= 1.18 else "rectangulo"
        conf = limpio
    elif v == 5:
        clave, conf = "pentagono", limpio * 0.9
    elif v == 6:
        clave, conf = "hexagono", limpio * 0.85
    elif circ > 0.70:
        clave, conf = "ovalo", float(np.clip(circ, 0, 0.95))
    else:
        clave, conf = "libre", 0.5

    return dict(clave=clave, contorno=aprox, vertices=v, circ=circ, solidez=solidez, conf=conf)


@st.cache_resource
def modelo_numeros():
    """Entrena (una sola vez) un modelo con 1.797 números escritos a mano."""
    from sklearn.datasets import load_digits
    from sklearn.svm import SVC
    datos = load_digits()
    modelo = SVC(gamma=0.001, C=10, probability=True)
    modelo.fit(datos.data, datos.target)
    return modelo


def preparar_numero(mask):
    """Recorta el número, lo centra y lo reduce a 8x8 como en el entrenamiento."""
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    recorte = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8) * 255
    h, w = recorte.shape
    if max(h, w) < 25:
        return None
    grosor = max(1, max(h, w) // 14)
    recorte = cv2.dilate(recorte, np.ones((grosor, grosor), np.uint8))
    lado = int(max(h, w) * 1.25) + 2
    lienzo = np.zeros((lado, lado), np.uint8)
    oy, ox = (lado - h) // 2, (lado - w) // 2
    lienzo[oy:oy + h, ox:ox + w] = recorte
    pequeno = cv2.resize(lienzo, (8, 8), interpolation=cv2.INTER_AREA).astype(np.float32)
    if pequeno.max() > 0:
        pequeno = pequeno / pequeno.max() * 16
    return pequeno


def encontrar_estrellas(mask):
    """Cada manchita separada del dibujo es una estrella: devuelve sus centros."""
    n, _, stats, centros = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    return np.array([centros[i] for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= 4])


def normalizar(puntos):
    p = np.asarray(puntos, float)
    centro = p.mean(axis=0)
    q = p - centro
    escala = np.sqrt((q ** 2).sum(axis=1).mean()) or 1.0
    return q / escala, centro, escala


def ajustar(origen, destino):
    """Mejor giro + escala + movimiento (sin espejo) para llevar origen sobre destino."""
    mo, md = origen.mean(axis=0), destino.mean(axis=0)
    a, b = origen - mo, destino - md
    U, S, Vt = np.linalg.svd(b.T @ a)
    D = np.diag([1, np.sign(np.linalg.det(U @ Vt))])
    R = U @ D @ Vt
    s = (S * np.diag(D)).sum() / ((a ** 2).sum() or 1.0)
    return s, R, md - s * R @ mo


def comparar_constelacion(estrellas, plantilla):
    """Qué tan parecidas son tus estrellas a una constelación (0 = idénticas)."""
    u, centro, escala = normalizar(estrellas)
    p, _, _ = normalizar(plantilla)
    mejor_costo, mejor_pt = np.inf, None
    for ang in np.radians(np.arange(0, 360, 30)):          # el cielo puede estar girado
        R0 = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
        pt = p @ R0.T
        for _ in range(4):
            dist = np.linalg.norm(pt[:, None] - u[None], axis=2)
            fi, co = linear_sum_assignment(dist)            # empareja estrella con estrella
            if len(fi) >= 3:
                s, R, t = ajustar(p[fi], u[co])
                pt = (s * (R @ p.T)).T + t
        dist = np.linalg.norm(pt[:, None] - u[None], axis=2)
        fi, co = linear_sum_assignment(dist)
        costo = dist[fi, co].mean() + 0.25 * abs(len(u) - len(p))
        if costo < mejor_costo:
            mejor_costo, mejor_pt = costo, pt
    return mejor_costo, mejor_pt * escala + centro           # de vuelta a píxeles


def reconocer_constelacion(estrellas):
    resultados = []
    for clave, c in CONSTELACIONES.items():
        costo, pt = comparar_constelacion(estrellas, c["puntos"])
        conf = float(np.clip(1 - costo / 0.45, 0.02, 0.99))
        resultados.append(dict(clave=clave, costo=costo, conf=conf, puntos=pt))
    return sorted(resultados, key=lambda r: r["costo"])


def dibujar_cielo(ancho, alto, estrellas=None, plantilla=None, lineas=()):
    """Imagen de cielo nocturno con tus estrellas y la constelación encima."""
    cielo = np.zeros((alto, ancho, 3), np.uint8)
    for y in range(alto):                                    # degradado azul noche
        f = y / alto
        cielo[y] = (int(42 - 20 * f), int(23 - 10 * f), int(15 - 5 * f))
    rng = np.random.default_rng(7)
    for x, y in zip(rng.integers(0, ancho, 140), rng.integers(0, alto, 140)):
        cv2.circle(cielo, (int(x), int(y)), 1, (90, 90, 110), -1)
    if plantilla is not None:
        for a, b in lineas:
            pa = tuple(int(v) for v in plantilla[a])
            pb = tuple(int(v) for v in plantilla[b])
            cv2.line(cielo, pa, pb, (238, 211, 34), 2, cv2.LINE_AA)
        for p in plantilla:
            cv2.circle(cielo, tuple(int(v) for v in p), 9, (250, 139, 167), 2, cv2.LINE_AA)
    if estrellas is not None:
        for p in estrellas:
            c = tuple(int(v) for v in p)
            cv2.circle(cielo, c, 9, (120, 110, 90), -1, cv2.LINE_AA)
            cv2.circle(cielo, c, 5, (255, 255, 255), -1, cv2.LINE_AA)
    return cv2.cvtColor(cielo, cv2.COLOR_BGR2RGB)


def plantilla_en_lienzo(clave, ancho, alto):
    """Ubica una constelación centrada en el lienzo (para la pista del reto)."""
    p, _, _ = normalizar(CONSTELACIONES[clave]["puntos"])
    escala = min(ancho, alto) * 0.28
    return p * escala + np.array([ancho / 2, alto / 2])


def barras(probabilidades):
    filas = ""
    for etiqueta, p in probabilidades:
        filas += f"""
        <div class="prob">
            <div class="top"><span>{etiqueta}</span><span>{p * 100:.0f}%</span></div>
            <div class="fondo"><div class="lleno" style="width:{max(p * 100, 2):.0f}%"></div></div>
        </div>"""
    return filas


# ─────────────────────────────────────────────
# ESTADO (reto, puntaje y limpiar)
# ─────────────────────────────────────────────
estado = st.session_state
estado.setdefault("lienzo_id", 0)
estado.setdefault("puntos", 0)
estado.setdefault("intentos", 0)
estado.setdefault("reto_figura", random.choice(RETOS_FIGURA))
estado.setdefault("reto_numero", random.randint(0, 9))
estado.setdefault("reto_conste", random.choice(list(CONSTELACIONES.keys())))
estado.setdefault("veredicto", None)


def limpiar():
    estado.lienzo_id += 1
    estado.veredicto = None


def nuevo_reto(modo):
    if modo == "figuras":
        estado.reto_figura = random.choice([f for f in RETOS_FIGURA if f != estado.reto_figura])
    elif modo == "numeros":
        estado.reto_numero = random.choice([n for n in range(10) if n != estado.reto_numero])
    else:
        estado.reto_conste = random.choice([c for c in CONSTELACIONES if c != estado.reto_conste])
    limpiar()


# ─────────────────────────────────────────────
# PANEL LATERAL
# ─────────────────────────────────────────────
with st.sidebar:
    html("""
    <div style="font-family:'Space Grotesk',sans-serif; padding-top:4px;">
        <div style="font-size:1.6rem; font-weight:700; color:#ffffff;">Propiedades</div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#8b8b99;">
            // del tablero
        </div>
    </div>
    """)
    st.divider()

    st.markdown("### Modo reto")
    modo_reto = st.toggle("Jugar contra la IA 🎯", value=False,
                          help="La app te pide algo para dibujar y revisa si lo adivina.")

    st.divider()
    st.markdown("### Trazo")
    stroke_width = st.slider("Grosor de la línea / tamaño de estrellas", 4, 30, 14,
                             help="Para números funciona mejor un trazo grueso.")
    color_nombre = st.selectbox("Color", list(COLORES_TRAZO.keys()), index=1)
    stroke_color = COLORES_TRAZO[color_nombre]

    st.markdown("### Fondo")
    fondo_nombre = st.selectbox("Color de fondo", list(FONDOS.keys()))
    bg_color = FONDOS[fondo_nombre]

    st.markdown("### Dimensiones")
    canvas_width = st.slider("Ancho del tablero", 300, 800, 600, 50)
    canvas_height = st.slider("Alto del tablero", 250, 600, 400, 50)

    st.divider()
    st.markdown("### ¿Cómo funciona?")
    st.caption(
        "**Figuras:** la app busca el contorno de tu dibujo con OpenCV, cuenta sus "
        "esquinas y mide qué tan redondo es.\n\n"
        "**Números:** un modelo de aprendizaje automático (SVM) entrenado con 1.797 "
        "números escritos a mano compara tu trazo y calcula la probabilidad de cada número.\n\n"
        "**Constelaciones:** cada clic es una estrella. La app gira, escala y mueve 8 "
        "constelaciones reales sobre tus estrellas y mide cuál encaja mejor."
    )


# ─────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────
html("""
<div class="portada">
    <div class="grid"></div>
    <span class="tag">● tablero_inteligente.py</span>
    <h1>Tablero de <span>Mari</span><span class="cursor"></span></h1>
    <p>Dibuja una figura o un número y la inteligencia artificial adivina qué es.</p>
</div>
""")
st.write("")

modo_txt = st.radio(
    "¿Qué quieres que adivine?",
    ["🔷 Figuras", "🔢 Números", "✨ Constelaciones"],
    horizontal=True,
    on_change=limpiar,
)
modo = {"🔷 Figuras": "figuras", "🔢 Números": "numeros"}.get(modo_txt, "constelaciones")


# ── Barra del reto ──
if modo_reto:
    if modo == "figuras":
        emoji, nombre = FIGURAS[estado.reto_figura]
        objetivo = f"{emoji} {nombre}"
    elif modo == "numeros":
        objetivo = f"el número {estado.reto_numero}"
    else:
        c = CONSTELACIONES[estado.reto_conste]
        objetivo = f"{c['emoji']} {c['nombre']}"
    html(f"""
    <div class="reto">
        <span>🎯 Tu reto: dibuja <b>{objetivo}</b></span>
        <span class="score">✔ {estado.puntos} / {estado.intentos}</span>
    </div>
    """)
    if modo == "constelaciones":
        with st.expander("👀 Pista: ¿cómo es esta constelación?"):
            c = CONSTELACIONES[estado.reto_conste]
            st.image(dibujar_cielo(500, 300, plantilla=plantilla_en_lienzo(estado.reto_conste, 500, 300),
                                   lineas=c["lineas"]), use_container_width=True)
            st.caption(c["dato"])
    st.write("")


# ─────────────────────────────────────────────
# TABLERO + RESULTADO
# ─────────────────────────────────────────────
col_tablero, col_info = st.columns([3, 2], gap="large")

with col_tablero:
    with st.container(border=True):
        pista = {
            "figuras": "Dibuja UNA figura cerrada (que el final toque el inicio).",
            "numeros": "Dibuja UN número del 0 al 9, grande y centrado.",
            "constelaciones": "Haz clic para poner cada estrella ✦",
        }[modo]
        html(f"""
        <div class="barra">
            <span class="puntos"><span style="background:#f43f5e"></span><span style="background:#facc15"></span><span style="background:#a3e635"></span></span>
            <span>{pista}</span>
            <span>{canvas_width}×{canvas_height}</span>
        </div>
        """)

        opciones = dict(
            fill_color="rgba(0, 0, 0, 0)",
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color=bg_color,
            height=canvas_height,
            width=canvas_width,
            drawing_mode="point" if modo == "constelaciones" else "freedraw",
            point_display_radius=max(4, stroke_width // 2),
            update_streamlit=True,
            display_toolbar=False,
            key=f"tablero_{modo}_{canvas_width}_{canvas_height}_{estado.lienzo_id}",
        )
        aceptadas = inspect.signature(st_canvas).parameters
        opciones = {k: v for k, v in opciones.items() if k in aceptadas}

        try:
            canvas_result = st_canvas(**opciones)
        except Exception as e:
            st.error("El tablero no pudo cargar 😢 Revisa las versiones en requirements.txt.")
            st.code(f"{type(e).__name__}: {e}")
            st.stop()

        b1, b2 = st.columns(2)
        with b1:
            st.button("🧽 Limpiar tablero", on_click=limpiar, use_container_width=True)
        with b2:
            if modo_reto:
                st.button("⏭ Saltar reto", on_click=nuevo_reto, args=(modo,),
                          use_container_width=True)


# ── Analizar el dibujo ──
hay_dibujo = False
resultado = None
if canvas_result is not None and canvas_result.image_data is not None:
    mask = mascara_de(canvas_result.image_data, bg_color)
    hay_dibujo = mask.sum() > 80
    if hay_dibujo:
        if modo == "figuras":
            resultado = clasificar_figura(mask)
        elif modo == "constelaciones":
            estrellas = encontrar_estrellas(mask)
            if len(estrellas) >= 3:
                resultado = dict(estrellas=estrellas, top=reconocer_constelacion(estrellas))
            else:
                resultado = dict(estrellas=estrellas, top=None)
        else:
            x = preparar_numero(mask)
            if x is not None:
                probs = modelo_numeros().predict_proba([x.ravel()])[0]
                resultado = dict(numero=int(np.argmax(probs)), probs=probs, imagen=x)


with col_info:
    with st.container(border=True):
        # ── Sin dibujo ──
        if resultado is None:
            html("""
            <div class="resultado vacio">
                <div class="mini">// esperando dibujo</div>
                <div class="emoji">✍️</div>
                <div class="nombre">Dibuja algo en el tablero</div>
            </div>
            """)

        # ── Figuras ──
        elif modo == "figuras":
            emoji, nombre = FIGURAS[resultado["clave"]]
            html(f"""
            <div class="resultado">
                <div class="mini">// la IA cree que es</div>
                <div class="emoji">{emoji}</div>
                <div class="nombre">{nombre}</div>
                <div class="conf">{resultado['conf'] * 100:.0f}% de seguridad</div>
            </div>
            """)

            if resultado["clave"] == "linea":
                st.caption("💡 Parece una figura abierta. Cierra el contorno para que la reconozca.")

            # Lo que ve la IA: el contorno detectado
            vista = np.zeros((canvas_height, canvas_width, 3), np.uint8)
            vista[mask] = (70, 70, 85)
            cv2.drawContours(vista, [resultado["contorno"]], -1, (250, 139, 167), 3)
            for p in resultado["contorno"].reshape(-1, 2):
                cv2.circle(vista, tuple(int(c) for c in p), 7, (238, 211, 34), -1)

            with st.expander("👁 Lo que ve la IA", expanded=True):
                st.image(cv2.cvtColor(vista, cv2.COLOR_BGR2RGB), use_container_width=True)
                html(f"""
                <div class="datos">
                    <div><span>esquinas detectadas</span><b>{resultado['vertices']}</b></div>
                    <div><span>redondez (1 = círculo)</span><b>{resultado['circ']:.2f}</b></div>
                    <div><span>solidez (1 = sin picos)</span><b>{resultado['solidez']:.2f}</b></div>
                </div>
                """)

            acierto = resultado["clave"] == estado.reto_figura

        # ── Constelaciones ──
        elif modo == "constelaciones":
            estrellas = resultado["estrellas"]
            acierto = False
            if resultado["top"] is None:
                html(f"""
                <div class="resultado vacio">
                    <div class="mini">// {len(estrellas)} estrella(s)</div>
                    <div class="emoji">✦</div>
                    <div class="nombre">Pon al menos 3 estrellas</div>
                </div>
                """)
            else:
                mejor = resultado["top"][0]
                c = CONSTELACIONES[mejor["clave"]]
                parecida = mejor["costo"] < 0.32
                titulo = "// la IA cree que es" if parecida else "// no se parece mucho… lo más cercano es"
                html(f"""
                <div class="resultado">
                    <div class="mini">{titulo}</div>
                    <div class="emoji">{c['emoji']}</div>
                    <div class="nombre">{c['nombre']}</div>
                    <div class="conf">{mejor['conf'] * 100:.0f}% de parecido · {len(estrellas)} estrellas</div>
                </div>
                """)
                st.caption(f"💫 {c['dato']}")
                html(barras([(CONSTELACIONES[r["clave"]]["nombre"], r["conf"])
                             for r in resultado["top"][:3]]))

                with st.expander("👁 Lo que ve la IA", expanded=True):
                    st.image(dibujar_cielo(canvas_width, canvas_height, estrellas,
                                           mejor["puntos"], c["lineas"]),
                             use_container_width=True)
                    st.caption("⚪ tus estrellas · ◯ violeta: estrellas de la constelación real · "
                               "líneas cian: cómo se une la constelación")
                acierto = parecida and mejor["clave"] == estado.reto_conste

        # ── Números ──
        else:
            n = resultado["numero"]
            probs = resultado["probs"]
            html(f"""
            <div class="resultado">
                <div class="mini">// la IA cree que es</div>
                <div class="emoji" style="font-family:'JetBrains Mono',monospace; font-weight:600; font-size:4.4rem; color:#ffffff;">{n}</div>
                <div class="conf">{probs[n] * 100:.0f}% de seguridad</div>
            </div>
            """)

            top3 = np.argsort(probs)[::-1][:3]
            html(barras([(f"número {i}", float(probs[i])) for i in top3]))

            with st.expander("👁 Lo que ve la IA (8×8 píxeles)"):
                vista = cv2.resize((resultado["imagen"] / 16 * 255).astype(np.uint8),
                                   (200, 200), interpolation=cv2.INTER_NEAREST)
                st.image(vista, width=200)
                st.caption("La app reduce tu dibujo a 64 cuadritos, igual que los "
                           "números con los que se entrenó el modelo.")

            acierto = n == estado.reto_numero

        # ── Revisar reto ──
        if modo_reto and resultado is not None:
            st.write("")
            if st.button("✅ Comprobar reto", type="primary", use_container_width=True):
                estado.intentos += 1
                if acierto:
                    estado.puntos += 1
                    estado.veredicto = "ok"
                    nuevo_reto(modo)
                    estado.veredicto = "ok"
                    st.balloons()
                else:
                    estado.veredicto = "mal"
                st.rerun()

        if modo_reto and estado.veredicto == "ok":
            html('<div class="veredicto ok">¡Lo adivinó! +1 punto · nuevo reto arriba ✨</div>')
        elif modo_reto and estado.veredicto == "mal":
            html('<div class="veredicto mal">La IA no lo reconoció. Intenta otra vez 💪</div>')

        # ── Descargar dibujo ──
        if hay_dibujo:
            dibujo = Image.fromarray(canvas_result.image_data.astype(np.uint8), "RGBA")
            fondo = Image.new("RGBA", dibujo.size, bg_color)
            final = Image.alpha_composite(fondo, dibujo).convert("RGB")
            buf = io.BytesIO()
            final.save(buf, format="PNG")
            st.download_button("⬇ Descargar dibujo", data=buf.getvalue(),
                               file_name="dibujo_de_mari.png", mime="image/png",
                               use_container_width=True)


# ─────────────────────────────────────────────
# PIE
# ─────────────────────────────────────────────
html('<div class="footer">hecho en clase por <b>Mari</b> · python + streamlit + opencv + scikit-learn</div>')    "Lima":     "#a3e635",
    "Amarillo": "#facc15",
}

FONDOS = {
    "Negro":      "#0a0a0d",
    "Carbón":     "#18181d",
    "Azul noche": "#0f172a",
}


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
        --ok:      #a3e635;
        --mal:     #f43f5e;
    }

    .stApp, .stApp p, .stApp label, .stApp input, .stApp button, .stApp li {
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
    [data-testid="stCaptionContainer"] { color: var(--suave) !important; }
    [data-testid="stHeader"] { background: transparent; }

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

    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--borde) !important;
        border-radius: 20px !important;
        background: var(--panel);
    }

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
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7c3aed, #0891b2) !important;
        border: none !important;
    }

    /* Selector de modo */
    [data-testid="stRadio"] [role="radiogroup"] { gap: 10px; flex-wrap: wrap; }
    [data-testid="stRadio"] [role="radiogroup"] label {
        background: var(--panel);
        border: 1px solid var(--borde);
        border-radius: 12px;
        padding: 8px 16px;
    }

    /* Encabezado */
    .portada {
        position: relative;
        overflow: hidden;
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
    }
    .portada h1 {
        position: relative;
        font-size: 3.3rem;
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
    .portada p { position: relative; color: var(--suave); margin: 0; font-size: 1rem; }
    .cursor {
        display: inline-block; width: 3px; height: 2.5rem; margin-left: 6px;
        vertical-align: -6px; background: var(--acento2);
        animation: parpadeo 1s steps(1) infinite;
    }
    @keyframes parpadeo { 50% { opacity: 0; } }

    /* Reto */
    .reto {
        display: flex; align-items: center; justify-content: space-between; gap: 14px;
        background: var(--panel);
        border: 1px dashed #3a3a46;
        border-radius: 16px;
        padding: 14px 20px;
        font-family: 'Space Grotesk', sans-serif;
        color: var(--suave);
    }
    .reto b { color: #ffffff; font-size: 1.25rem; }
    .reto .score {
        font-family: 'JetBrains Mono', monospace;
        color: var(--ok);
        font-size: 1rem;
        white-space: nowrap;
    }

    /* Barra del tablero */
    .barra {
        display: flex; justify-content: space-between; align-items: center;
        font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
        color: var(--suave); margin-bottom: 6px;
    }
    .barra .puntos span {
        display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px;
    }
    iframe[title="streamlit_drawable_canvas.st_canvas"] {
        border-radius: 14px;
        box-shadow: 0 0 0 1px var(--borde), 0 20px 50px rgba(0,0,0,0.6);
    }

    /* Resultado */
    .resultado {
        text-align: center;
        padding: 18px 10px 10px;
        font-family: 'Space Grotesk', sans-serif;
        animation: aparecer 0.4s ease;
    }
    .resultado .mini {
        font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
        color: var(--suave); letter-spacing: 1px;
    }
    .resultado .emoji { font-size: 3.6rem; line-height: 1.2; margin-top: 6px; }
    .resultado .nombre {
        font-size: 2.2rem; font-weight: 700; color: #ffffff; letter-spacing: -0.5px;
    }
    .resultado .conf {
        font-family: 'JetBrains Mono', monospace; color: var(--acento2); font-size: 0.85rem;
    }
    .resultado.vacio .nombre { color: #4a4a55; font-size: 1.4rem; }
    @keyframes aparecer {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .veredicto {
        border-radius: 14px; padding: 12px; text-align: center;
        font-family: 'Space Grotesk', sans-serif; font-weight: 600;
    }
    .veredicto.ok  { background: rgba(163,230,53,0.12); color: var(--ok);  border: 1px solid rgba(163,230,53,0.4); }
    .veredicto.mal { background: rgba(244,63,94,0.10); color: var(--mal); border: 1px solid rgba(244,63,94,0.4); }

    /* Barras de probabilidad */
    .prob { margin: 8px 0; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }
    .prob .top { display: flex; justify-content: space-between; color: var(--texto); margin-bottom: 4px; }
    .prob .fondo { background: var(--panel2); border-radius: 999px; height: 8px; overflow: hidden; }
    .prob .lleno { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #7c3aed, #22d3ee); }

    /* Datos técnicos */
    .datos { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: var(--suave); }
    .datos div { display: flex; justify-content: space-between; padding: 4px 0;
                 border-bottom: 1px solid var(--borde); }
    .datos b { color: var(--texto); font-weight: 600; }

    .footer {
        text-align: center; margin-top: 34px;
        font-family: 'JetBrains Mono', monospace; font-size: 0.75rem;
        color: #55555f; letter-spacing: 1px;
    }
    .footer b { color: var(--acento); font-weight: 600; }
</style>
""")


# ─────────────────────────────────────────────
# RECONOCIMIENTO 🧠
# ─────────────────────────────────────────────
def mascara_de(image_data, bg_hex):
    """Devuelve True donde hay dibujo y False donde está el fondo."""
    img = image_data.astype(np.int16)
    alpha = img[:, :, 3]
    if alpha.min() < 255:
        return alpha > 50
    h = bg_hex.lstrip("#")
    bg = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)])
    return np.abs(img[:, :, :3] - bg).sum(axis=2) > 60


def clasificar_figura(mask):
    """Encuentra el contorno más grande y decide qué figura es."""
    m = mask.astype(np.uint8) * 255
    # cierra pequeños huecos del trazo a mano
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8), iterations=2)
    contornos, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos:
        return None

    c = max(contornos, key=cv2.contourArea)
    area = cv2.contourArea(c)
    perimetro = cv2.arcLength(c, True)
    x, y, w, h = cv2.boundingRect(c)

    if w * h < 900:
        return dict(clave="pequeno", contorno=c, vertices=0, circ=0.0, solidez=0.0, conf=0.0)

    relleno = area / (w * h)
    solidez = area / max(cv2.contourArea(cv2.convexHull(c)), 1)
    circ = 4 * np.pi * area / (perimetro ** 2) if perimetro else 0.0
    aprox = cv2.approxPolyDP(c, 0.03 * perimetro, True)
    v = len(aprox)
    proporcion = w / h
    limpio = float(np.clip(1 - abs(area - cv2.contourArea(aprox)) / max(area, 1) * 3, 0.4, 0.99))

    if relleno < 0.12:
        clave, conf = "linea", 0.80
    elif solidez < 0.75 and v >= 8:
        clave, conf = "estrella", float(np.clip(1.4 - solidez, 0.5, 0.97))
    elif circ > 0.80 and v > 6:
        clave, conf = "circulo", float(np.clip(circ, 0, 0.99))
    elif v == 3:
        clave, conf = "triangulo", limpio
    elif v == 4:
        clave = "cuadrado" if 0.82 <= proporcion <= 1.18 else "rectangulo"
        conf = limpio
    elif v == 5:
        clave, conf = "pentagono", limpio * 0.9
    elif v == 6:
        clave, conf = "hexagono", limpio * 0.85
    elif circ > 0.70:
        clave, conf = "ovalo", float(np.clip(circ, 0, 0.95))
    else:
        clave, conf = "libre", 0.5

    return dict(clave=clave, contorno=aprox, vertices=v, circ=circ, solidez=solidez, conf=conf)


@st.cache_resource
def modelo_numeros():
    """Entrena (una sola vez) un modelo con 1.797 números escritos a mano."""
    from sklearn.datasets import load_digits
    from sklearn.svm import SVC
    datos = load_digits()
    modelo = SVC(gamma=0.001, C=10, probability=True)
    modelo.fit(datos.data, datos.target)
    return modelo


def preparar_numero(mask):
    """Recorta el número, lo centra y lo reduce a 8x8 como en el entrenamiento."""
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    recorte = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8) * 255
    h, w = recorte.shape
    if max(h, w) < 25:
        return None
    grosor = max(1, max(h, w) // 14)
    recorte = cv2.dilate(recorte, np.ones((grosor, grosor), np.uint8))
    lado = int(max(h, w) * 1.25) + 2
    lienzo = np.zeros((lado, lado), np.uint8)
    oy, ox = (lado - h) // 2, (lado - w) // 2
    lienzo[oy:oy + h, ox:ox + w] = recorte
    pequeno = cv2.resize(lienzo, (8, 8), interpolation=cv2.INTER_AREA).astype(np.float32)
    if pequeno.max() > 0:
        pequeno = pequeno / pequeno.max() * 16
    return pequeno


def barras(probabilidades):
    filas = ""
    for etiqueta, p in probabilidades:
        filas += f"""
        <div class="prob">
            <div class="top"><span>{etiqueta}</span><span>{p * 100:.0f}%</span></div>
            <div class="fondo"><div class="lleno" style="width:{max(p * 100, 2):.0f}%"></div></div>
        </div>"""
    return filas


# ─────────────────────────────────────────────
# ESTADO (reto, puntaje y limpiar)
# ─────────────────────────────────────────────
estado = st.session_state
estado.setdefault("lienzo_id", 0)
estado.setdefault("puntos", 0)
estado.setdefault("intentos", 0)
estado.setdefault("reto_figura", random.choice(RETOS_FIGURA))
estado.setdefault("reto_numero", random.randint(0, 9))
estado.setdefault("veredicto", None)


def limpiar():
    estado.lienzo_id += 1
    estado.veredicto = None


def nuevo_reto(modo):
    if modo == "figuras":
        estado.reto_figura = random.choice([f for f in RETOS_FIGURA if f != estado.reto_figura])
    else:
        estado.reto_numero = random.choice([n for n in range(10) if n != estado.reto_numero])
    limpiar()


# ─────────────────────────────────────────────
# PANEL LATERAL
# ─────────────────────────────────────────────
with st.sidebar:
    html("""
    <div style="font-family:'Space Grotesk',sans-serif; padding-top:4px;">
        <div style="font-size:1.6rem; font-weight:700; color:#ffffff;">Propiedades</div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#8b8b99;">
            // del tablero
        </div>
    </div>
    """)
    st.divider()

    st.markdown("### Modo reto")
    modo_reto = st.toggle("Jugar contra la IA 🎯", value=False,
                          help="La app te pide algo para dibujar y revisa si lo adivina.")

    st.divider()
    st.markdown("### Trazo")
    stroke_width = st.slider("Grosor de la línea", 4, 30, 14,
                             help="Para números funciona mejor un trazo grueso.")
    color_nombre = st.selectbox("Color", list(COLORES_TRAZO.keys()), index=1)
    stroke_color = COLORES_TRAZO[color_nombre]

    st.markdown("### Fondo")
    fondo_nombre = st.selectbox("Color de fondo", list(FONDOS.keys()))
    bg_color = FONDOS[fondo_nombre]

    st.markdown("### Dimensiones")
    canvas_width = st.slider("Ancho del tablero", 300, 800, 600, 50)
    canvas_height = st.slider("Alto del tablero", 250, 600, 400, 50)

    st.divider()
    st.markdown("### ¿Cómo funciona?")
    st.caption(
        "**Figuras:** la app busca el contorno de tu dibujo con OpenCV, cuenta sus "
        "esquinas y mide qué tan redondo es.\n\n"
        "**Números:** un modelo de aprendizaje automático (SVM) entrenado con 1.797 "
        "números escritos a mano compara tu trazo y calcula la probabilidad de cada número."
    )


# ─────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────
html("""
<div class="portada">
    <div class="grid"></div>
    <span class="tag">● tablero_inteligente.py</span>
    <h1>Tablero de <span>Mari</span><span class="cursor"></span></h1>
    <p>Dibuja una figura o un número y la inteligencia artificial adivina qué es.</p>
</div>
""")
st.write("")

modo_txt = st.radio(
    "¿Qué quieres que adivine?",
    ["🔷 Figuras", "🔢 Números"],
    horizontal=True,
    on_change=limpiar,
)
modo = "figuras" if "Figuras" in modo_txt else "numeros"


# ── Barra del reto ──
if modo_reto:
    if modo == "figuras":
        emoji, nombre = FIGURAS[estado.reto_figura]
        objetivo = f"{emoji} {nombre}"
    else:
        objetivo = f"el número {estado.reto_numero}"
    html(f"""
    <div class="reto">
        <span>🎯 Tu reto: dibuja <b>{objetivo}</b></span>
        <span class="score">✔ {estado.puntos} / {estado.intentos}</span>
    </div>
    """)
    st.write("")


# ─────────────────────────────────────────────
# TABLERO + RESULTADO
# ─────────────────────────────────────────────
col_tablero, col_info = st.columns([3, 2], gap="large")

with col_tablero:
    with st.container(border=True):
        pista = ("Dibuja UNA figura cerrada (que el final toque el inicio)."
                 if modo == "figuras" else "Dibuja UN número del 0 al 9, grande y centrado.")
        html(f"""
        <div class="barra">
            <span class="puntos"><span style="background:#f43f5e"></span><span style="background:#facc15"></span><span style="background:#a3e635"></span></span>
            <span>{pista}</span>
            <span>{canvas_width}×{canvas_height}</span>
        </div>
        """)

        opciones = dict(
            fill_color="rgba(0, 0, 0, 0)",
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color=bg_color,
            height=canvas_height,
            width=canvas_width,
            drawing_mode="freedraw",
            update_streamlit=True,
            display_toolbar=False,
            key=f"tablero_{modo}_{canvas_width}_{canvas_height}_{estado.lienzo_id}",
        )
        aceptadas = inspect.signature(st_canvas).parameters
        opciones = {k: v for k, v in opciones.items() if k in aceptadas}

        try:
            canvas_result = st_canvas(**opciones)
        except Exception as e:
            st.error("El tablero no pudo cargar 😢 Revisa las versiones en requirements.txt.")
            st.code(f"{type(e).__name__}: {e}")
            st.stop()

        b1, b2 = st.columns(2)
        with b1:
            st.button("🧽 Limpiar tablero", on_click=limpiar, use_container_width=True)
        with b2:
            if modo_reto:
                st.button("⏭ Saltar reto", on_click=nuevo_reto, args=(modo,),
                          use_container_width=True)


# ── Analizar el dibujo ──
hay_dibujo = False
resultado = None
if canvas_result is not None and canvas_result.image_data is not None:
    mask = mascara_de(canvas_result.image_data, bg_color)
    hay_dibujo = mask.sum() > 80
    if hay_dibujo:
        if modo == "figuras":
            resultado = clasificar_figura(mask)
        else:
            x = preparar_numero(mask)
            if x is not None:
                probs = modelo_numeros().predict_proba([x.ravel()])[0]
                resultado = dict(numero=int(np.argmax(probs)), probs=probs, imagen=x)


with col_info:
    with st.container(border=True):
        # ── Sin dibujo ──
        if resultado is None:
            html("""
            <div class="resultado vacio">
                <div class="mini">// esperando dibujo</div>
                <div class="emoji">✍️</div>
                <div class="nombre">Dibuja algo en el tablero</div>
            </div>
            """)

        # ── Figuras ──
        elif modo == "figuras":
            emoji, nombre = FIGURAS[resultado["clave"]]
            html(f"""
            <div class="resultado">
                <div class="mini">// la IA cree que es</div>
                <div class="emoji">{emoji}</div>
                <div class="nombre">{nombre}</div>
                <div class="conf">{resultado['conf'] * 100:.0f}% de seguridad</div>
            </div>
            """)

            if resultado["clave"] == "linea":
                st.caption("💡 Parece una figura abierta. Cierra el contorno para que la reconozca.")

            # Lo que ve la IA: el contorno detectado
            vista = np.zeros((canvas_height, canvas_width, 3), np.uint8)
            vista[mask] = (70, 70, 85)
            cv2.drawContours(vista, [resultado["contorno"]], -1, (250, 139, 167), 3)
            for p in resultado["contorno"].reshape(-1, 2):
                cv2.circle(vista, tuple(int(c) for c in p), 7, (238, 211, 34), -1)

            with st.expander("👁 Lo que ve la IA", expanded=True):
                st.image(cv2.cvtColor(vista, cv2.COLOR_BGR2RGB), use_container_width=True)
                html(f"""
                <div class="datos">
                    <div><span>esquinas detectadas</span><b>{resultado['vertices']}</b></div>
                    <div><span>redondez (1 = círculo)</span><b>{resultado['circ']:.2f}</b></div>
                    <div><span>solidez (1 = sin picos)</span><b>{resultado['solidez']:.2f}</b></div>
                </div>
                """)

            acierto = resultado["clave"] == estado.reto_figura

        # ── Números ──
        else:
            n = resultado["numero"]
            probs = resultado["probs"]
            html(f"""
            <div class="resultado">
                <div class="mini">// la IA cree que es</div>
                <div class="emoji" style="font-family:'JetBrains Mono',monospace; font-weight:600; font-size:4.4rem; color:#ffffff;">{n}</div>
                <div class="conf">{probs[n] * 100:.0f}% de seguridad</div>
            </div>
            """)

            top3 = np.argsort(probs)[::-1][:3]
            html(barras([(f"número {i}", float(probs[i])) for i in top3]))

            with st.expander("👁 Lo que ve la IA (8×8 píxeles)"):
                vista = cv2.resize((resultado["imagen"] / 16 * 255).astype(np.uint8),
                                   (200, 200), interpolation=cv2.INTER_NEAREST)
                st.image(vista, width=200)
                st.caption("La app reduce tu dibujo a 64 cuadritos, igual que los "
                           "números con los que se entrenó el modelo.")

            acierto = n == estado.reto_numero

        # ── Revisar reto ──
        if modo_reto and resultado is not None:
            st.write("")
            if st.button("✅ Comprobar reto", type="primary", use_container_width=True):
                estado.intentos += 1
                if acierto:
                    estado.puntos += 1
                    estado.veredicto = "ok"
                    nuevo_reto(modo)
                    estado.veredicto = "ok"
                    st.balloons()
                else:
                    estado.veredicto = "mal"
                st.rerun()

        if modo_reto and estado.veredicto == "ok":
            html('<div class="veredicto ok">¡Lo adivinó! +1 punto · nuevo reto arriba ✨</div>')
        elif modo_reto and estado.veredicto == "mal":
            html('<div class="veredicto mal">La IA no lo reconoció. Intenta otra vez 💪</div>')

        # ── Descargar dibujo ──
        if hay_dibujo:
            dibujo = Image.fromarray(canvas_result.image_data.astype(np.uint8), "RGBA")
            fondo = Image.new("RGBA", dibujo.size, bg_color)
            final = Image.alpha_composite(fondo, dibujo).convert("RGB")
            buf = io.BytesIO()
            final.save(buf, format="PNG")
            st.download_button("⬇ Descargar dibujo", data=buf.getvalue(),
                               file_name="dibujo_de_mari.png", mime="image/png",
                               use_container_width=True)


# ─────────────────────────────────────────────
# PIE
# ─────────────────────────────────────────────
html('<div class="footer">hecho en clase por <b>Mari</b> · python + streamlit + opencv + scikit-learn</div>')
