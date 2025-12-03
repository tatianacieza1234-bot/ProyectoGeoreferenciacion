# Visor de Coordenadas con Streamlit

Aplicación para visualizar coordenadas (latitud y longitud) desde un archivo Excel o CSV.

## 🚀 Cómo usar
1. Sube un archivo `.xlsx` o `.csv` con columnas:
   - `descripcion`
   - `latitud`
   - `longitud`

2. La app mostrará:
   - Tabla con los datos
   - Un mapa para cada punto (con Google Maps, Satélite y ESRI)

## ▶ Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
