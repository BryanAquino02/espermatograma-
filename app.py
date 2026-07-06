"""
Acrosom.ai — Interfaz de análisis de conteo espermático.

Sube una imagen de microscopio, el modelo YOLOv8 detecta y cuenta
espermatozoides, clusters y pinheads, y muestra el resultado con un
diseño minimal consistente con los reportes de Concebir.

Uso:
    streamlit run app.py
"""

import os
import io
from datetime import datetime

import streamlit as st
from PIL import Image
from ultralytics import YOLO

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

MODEL_PATH = os.path.join("model", "best.pt")
CONF_THRESHOLD = 0.25

CLASS_LABELS = {
    "sperm": "Espermatozoides",
    "cluster": "Clusters",
    "pinhead": "Pinheads",
}

st.set_page_config(
    page_title="Acrosom.ai — Análisis de conteo",
    page_icon="🔬",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Estilo minimal — paleta neutra, tipografía limpia, sin ruido visual
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, sans-serif;
        }

        .main {
            background-color: #fafaf8;
        }

        .block-container {
            padding-top: 3rem;
            max-width: 780px;
        }

        h1 {
            font-weight: 500;
            font-size: 1.9rem;
            letter-spacing: -0.02em;
            color: #1a1a1a;
            margin-bottom: 0.1rem;
        }

        .subtitle {
            color: #8a8a85;
            font-size: 0.95rem;
            font-weight: 400;
            margin-bottom: 2.2rem;
            letter-spacing: 0.01em;
        }

        .divider {
            border: none;
            border-top: 1px solid #e4e2dc;
            margin: 1.8rem 0;
        }

        [data-testid="stFileUploader"] {
            border: 1px solid #e4e2dc;
            border-radius: 4px;
            padding: 0.5rem;
            background-color: #ffffff;
        }

        .result-card {
            background-color: #ffffff;
            border: 1px solid #e4e2dc;
            border-radius: 6px;
            padding: 1.6rem 1.8rem;
            margin-top: 1.5rem;
        }

        .result-title {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #a19d94;
            font-weight: 500;
            margin-bottom: 1rem;
        }

        .count-row {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            padding: 0.55rem 0;
            border-bottom: 1px solid #f1efe9;
        }

        .count-row:last-child {
            border-bottom: none;
        }

        .count-label {
            font-size: 0.92rem;
            color: #4a4a45;
            font-weight: 400;
        }

        .count-value {
            font-size: 1.15rem;
            color: #1a1a1a;
            font-weight: 600;
            font-variant-numeric: tabular-nums;
        }

        .total-row {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            padding-top: 1rem;
            margin-top: 0.4rem;
            border-top: 1px solid #e4e2dc;
        }

        .total-label {
            font-size: 0.85rem;
            color: #1a1a1a;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .total-value {
            font-size: 1.4rem;
            color: #1a1a1a;
            font-weight: 600;
            font-variant-numeric: tabular-nums;
        }

        .meta-text {
            font-size: 0.78rem;
            color: #a19d94;
            margin-top: 0.8rem;
        }

        .stButton>button {
            background-color: #1a1a1a;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1.4rem;
            font-weight: 500;
            font-size: 0.88rem;
            letter-spacing: 0.02em;
        }

        .stButton>button:hover {
            background-color: #3a3a35;
            color: #ffffff;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Carga del modelo (cacheado, se carga una sola vez)
# ---------------------------------------------------------------------------

@st.cache_resource
def load_model(path):
    return YOLO(path)


# ---------------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------------

st.markdown("<h1>Acrosom.ai</h1>", unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Análisis automatizado de conteo espermático — Concebir</div>',
    unsafe_allow_html=True,
)

if not os.path.exists(MODEL_PATH):
    st.error(f"No se encontró el modelo en: {MODEL_PATH}")
    st.stop()

model = load_model(MODEL_PATH)

uploaded_file = st.file_uploader(
    "Sube una imagen de microscopio",
    type=["jpg", "jpeg", "png", "bmp"],
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    with st.spinner("Analizando muestra..."):
        results = model.predict(source=image, conf=CONF_THRESHOLD, verbose=False)
        result = results[0]

    annotated_array = result.plot(labels=False, conf=False, line_width=1)  # solo recuadros, sin texto
    annotated_image = Image.fromarray(annotated_array[:, :, ::-1])  # BGR -> RGB

    st.image(annotated_image, use_container_width=True)

    # Conteo por clase
    counts = {name: 0 for name in CLASS_LABELS}
    if result.boxes is not None and len(result.boxes) > 0:
        for cls_id in result.boxes.cls.tolist():
            class_name = model.names[int(cls_id)]
            if class_name in counts:
                counts[class_name] += 1

    total = sum(counts.values())

    rows_html = "".join(
        f"""
        <div class="count-row">
            <span class="count-label">{label}</span>
            <span class="count-value">{counts[key]:,}</span>
        </div>
        """
        for key, label in CLASS_LABELS.items()
    )

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-title">Resultado del análisis</div>
            {rows_html}
            <div class="total-row">
                <span class="total-label">Total detectado</span>
                <span class="total-value">{total:,}</span>
            </div>
        </div>
        <div class="meta-text">
            Analizado el {datetime.now().strftime("%d/%m/%Y a las %H:%M")}
            &nbsp;·&nbsp; Umbral de confianza: {CONF_THRESHOLD}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Descarga de la imagen anotada
    buf = io.BytesIO()
    annotated_image.save(buf, format="PNG")
    st.download_button(
        label="Descargar imagen analizada",
        data=buf.getvalue(),
        file_name=f"acrosom_analisis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
        mime="image/png",
    )
else:
    st.markdown(
        '<div class="meta-text">Formatos soportados: JPG, PNG, BMP</div>',
        unsafe_allow_html=True,
    )
