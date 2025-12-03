import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.title("Visor de Coordenadas")
st.write("Sube tu archivo Excel o CSV para visualizar las ubicaciones en el mapa")

# INSTRUCCIONES PARA EL USUARIO
with st.expander("📋 Instrucciones - Formato del archivo", expanded=False):
    st.markdown("""
    ### 📝 Tu archivo debe tener exactamente estas 3 columnas:
    
    | descripcion | latitud | longitud |
    |-------------|---------|----------|
    | MI CASA     | -6.62   | -79.41   |
    | INSTITUTO   | -6.78   | -79.85   |
    | DET         | -6.619  | -79.4    |
    
    #### ✅ Requisitos importantes:
    - **Columnas obligatorias:** `descripcion`, `latitud`, `longitud` (en minúsculas)
    - **Formato de coordenadas:** Números decimales (ejemplo: -6.62, -79.41)
    - **Descripción:** Texto que identifica cada ubicación
    - **Formato de archivo:** Excel (.xlsx) o CSV (.csv)
    
    #### 💡 Ejemplo de coordenadas:
    - Latitud: valores entre -90 y 90 (negativo para Sur, positivo para Norte)
    - Longitud: valores entre -180 y 180 (negativo para Oeste, positivo para Este)
    """)

# SUBIR ARCHIVO
archivo = st.file_uploader("Selecciona un archivo", type=["xlsx", "csv"])

if archivo is not None:

    nombre = archivo.name.lower()

    # LEER ARCHIVO
    try:
        if nombre.endswith(".csv"):
            df = pd.read_csv(archivo, encoding="utf-8", dtype=str)
        else:
            df = pd.read_excel(archivo, dtype=str)

        # LIMPIAR COLUMNAS
        df.columns = (
            df.columns
            .str.replace('\ufeff', '')
            .str.replace('\xa0', ' ')
            .str.strip()
            .str.lower()
        )

        # VERIFICAR QUE EXISTAN LAS COLUMNAS REQUERIDAS
        columnas_requeridas = ['descripcion', 'latitud', 'longitud']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        
        if columnas_faltantes:
            st.error(f"❌ Error: Faltan las siguientes columnas en tu archivo: {', '.join(columnas_faltantes)}")
            st.info("📋 Revisa las instrucciones arriba para ver el formato correcto del archivo.")
        else:
            # CONVERTIR NUMÉRICOS
            df["latitud"] = pd.to_numeric(df.get("latitud"), errors="coerce")
            df["longitud"] = pd.to_numeric(df.get("longitud"), errors="coerce")
            
            # FILTRAR SOLO REGISTROS CON COORDENADAS VÁLIDAS
            df_valido = df.dropna(subset=['latitud', 'longitud'])
            
            # VERIFICAR SI HAY COORDENADAS VÁLIDAS
            if len(df_valido) == 0:
                st.error("❌ Error: No se encontraron coordenadas válidas. Asegúrate de usar números decimales.")
            else:
                st.success(f"✅ Archivo cargado correctamente: {len(df_valido)} ubicaciones encontradas")
                
                st.subheader("Datos cargados:")
                st.dataframe(df)

                # ========================================
                # MAPA GENERAL CON TODAS LAS UBICACIONES
                # ========================================
                st.subheader("🗺️ Mapa General - Todas las ubicaciones")
                
                # SELECTOR DE TIPO DE MAPA PARA EL MAPA GENERAL
                tipo_mapa_general = st.selectbox(
                    "Selecciona el tipo de mapa:",
                    ["🗺️ Google Híbrido", "🛰️ Google Satélite", "🚗 Google Calles", "📍 CartoDB Positron"],
                    key="tipo_mapa_general"
                )
                
                # CALCULAR CENTRO Y ZOOM PARA ABARCAR TODAS LAS UBICACIONES
                lat_centro = df_valido['latitud'].mean()
                lon_centro = df_valido['longitud'].mean()
                
                # CREAR MAPA GENERAL
                mapa_general = folium.Map(
                    location=[lat_centro, lon_centro],
                    zoom_start=12,
                    max_zoom=22,
                    min_zoom=1,
                    control_scale=True,
                    tiles=None,
                    zoom_control=True,
                    scrollWheelZoom=True
                )

                # AGREGAR LA CAPA SELECCIONADA
                if tipo_mapa_general == "🗺️ Google Híbrido":
                    folium.TileLayer(
                        tiles="https://{s}.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                        attr="Google Hybrid",
                        name="Google Híbrido",
                        subdomains=['mt0', 'mt1', 'mt2', 'mt3'],
                        max_zoom=22
                    ).add_to(mapa_general)
                
                elif tipo_mapa_general == "🛰️ Google Satélite":
                    folium.TileLayer(
                        tiles="https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
                        attr="Google Satellite",
                        name="Google Satélite",
                        subdomains=['mt0', 'mt1', 'mt2', 'mt3'],
                        max_zoom=22
                    ).add_to(mapa_general)
                
                elif tipo_mapa_general == "🚗 Google Calles":
                    folium.TileLayer(
                        tiles="https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
                        attr="Google Streets",
                        name="Google Calles",
                        subdomains=['mt0', 'mt1', 'mt2', 'mt3'],
                        max_zoom=22
                    ).add_to(mapa_general)
                
                else:  # CartoDB Positron
                    folium.TileLayer(
                        tiles="CartoDB Positron",
                        name="CartoDB Positron"
                    ).add_to(mapa_general)

                # AGREGAR TODOS LOS MARCADORES AL MAPA GENERAL
                colores = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
                
                for idx, row in df_valido.iterrows():
                    color_marcador = colores[idx % len(colores)]  # Rotar colores
                    
                    folium.Marker(
                        location=[float(row["latitud"]), float(row["longitud"])],
                        popup=f"<b>{row['descripcion']}</b><br>Lat: {row['latitud']}<br>Lon: {row['longitud']}",
                        tooltip=row["descripcion"],
                        icon=folium.Icon(color=color_marcador, icon='info-sign')
                    ).add_to(mapa_general)
                
                # AJUSTAR EL ZOOM PARA QUE SE VEAN TODOS LOS MARCADORES
                if len(df_valido) > 1:
                    coordenadas = [[float(row['latitud']), float(row['longitud'])] for _, row in df_valido.iterrows()]
                    mapa_general.fit_bounds(coordenadas, padding=[50, 50])
                
                # MOSTRAR MAPA GENERAL
                st_folium(
                    mapa_general, 
                    width=700, 
                    height=500,
                    returned_objects=[],
                    key=f"mapa_general_{tipo_mapa_general}"
                )

                # ========================================
                # MAPAS INDIVIDUALES POR UBICACIÓN
                # ========================================
                st.subheader("📍 Mapas Individuales")

                # MOSTRAR CADA REGISTRO
                for i, row in df_valido.iterrows():
                    with st.expander(f"📍 {row['descripcion']}"):
                        
                        # SELECTOR DE TIPO DE MAPA
                        tipo_mapa = st.selectbox(
                            "Selecciona el tipo de mapa:",
                            ["🗺️ Google Híbrido", "🛰️ Google Satélite", "🚗 Google Calles", "📍 CartoDB Positron"],
                            key=f"tipo_mapa_{i}"
                        )
                        
                        col1, col2 = st.columns([1, 2])

                        with col1:
                            st.write(f"**Latitud:** {row['latitud']}")
                            st.write(f"**Longitud:** {row['longitud']}")

                        with col2:
                            lat = float(row["latitud"])
                            lon = float(row["longitud"])
                            
                            # CREAR MAPA SEGÚN LA SELECCIÓN
                            mapa = folium.Map(
                                location=[lat, lon],
                                zoom_start=18,
                                max_zoom=22,
                                min_zoom=1,
                                control_scale=True,
                                tiles=None,
                                zoom_control=True,
                                scrollWheelZoom=True
                            )

                            # AGREGAR LA CAPA SELECCIONADA
                            if tipo_mapa == "🗺️ Google Híbrido":
                                folium.TileLayer(
                                    tiles="https://{s}.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                                    attr="Google Hybrid",
                                    name="Google Híbrido",
                                    subdomains=['mt0', 'mt1', 'mt2', 'mt3'],
                                    max_zoom=22
                                ).add_to(mapa)
                            
                            elif tipo_mapa == "🛰️ Google Satélite":
                                folium.TileLayer(
                                    tiles="https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
                                    attr="Google Satellite",
                                    name="Google Satélite",
                                    subdomains=['mt0', 'mt1', 'mt2', 'mt3'],
                                    max_zoom=22
                                ).add_to(mapa)
                            
                            elif tipo_mapa == "🚗 Google Calles":
                                folium.TileLayer(
                                    tiles="https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
                                    attr="Google Streets",
                                    name="Google Calles",
                                    subdomains=['mt0', 'mt1', 'mt2', 'mt3'],
                                    max_zoom=22
                                ).add_to(mapa)
                            
                            else:  # CartoDB Positron
                                folium.TileLayer(
                                    tiles="CartoDB Positron",
                                    name="CartoDB Positron"
                                ).add_to(mapa)

                            # MARCADOR
                            folium.Marker(
                                location=[lat, lon],
                                popup=row["descripcion"],
                                tooltip="Ver ubicación",
                                icon=folium.Icon(color='red', icon='info-sign')
                            ).add_to(mapa)

                            # MOSTRAR MAPA
                            st_folium(
                                mapa, 
                                width=420, 
                                height=420,
                                returned_objects=[],
                                key=f"mapa_display_{i}_{tipo_mapa}"
                            )
    
    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {str(e)}")
        st.info("📋 Verifica que el archivo tenga el formato correcto según las instrucciones.")

else:
    st.info("⬆️ Sube un archivo para comenzar")