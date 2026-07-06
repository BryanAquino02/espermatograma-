# espermia — Demo de conteo espermático

Interfaz web para probar el modelo YOLOv8 de detección/conteo de
espermatozoides, clusters y pinheads.

## Estructura del repo

```
acrosom-ai-demo/
├── app.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
└── model/
    └── best.pt
```

## Cómo desplegar en Streamlit Community Cloud

1. Crea un repo nuevo en GitHub (puede ser privado o público).
2. Sube estos 4 elementos exactamente con esta estructura de carpetas:
   - `app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `model/best.pt`  (copia tu archivo `best.pt` entrenado aquí, dentro de una carpeta llamada `model`)
3. Ve a https://share.streamlit.io
4. Inicia sesión con tu cuenta de GitHub.
5. Clic en "New app" → selecciona el repo → selecciona la rama (main) →
   archivo principal: `app.py`.
6. Clic en "Deploy". Toma 2-5 minutos la primera vez (instala las
   dependencias de requirements.txt).
7. Te da una URL pública tipo: `https://tu-usuario-acrosom-ai-demo.streamlit.app`

## Notas

- El modelo `best.pt` pesa ~6.2MB, así que no hay problema subiéndolo
  directo a GitHub (el límite normal de GitHub es 100MB por archivo).
- Si la app "duerme" por inactividad (plan gratuito de Streamlit Cloud),
  la primera visita del día tarda unos segundos extra en despertar —
  es normal, no es un error.
- Cualquier cambio que subas al repo (push a main) redepliega la app
  automáticamente.
