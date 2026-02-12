import streamlit as st
import pandas as pd
import requests
import time

# CONFIGURACIÓN
API_URL = "http://127.0.0.1:8000"  # Donde vive tu FastAPI
st.set_page_config(page_title="OvineTech 4.0", page_icon="🐑", layout="wide")

# TÍTULO Y ESTADO
st.title("🐑 OvineTech 4.0 - Centro de Control")
st.markdown("---")

# SIDEBAR (Menú Lateral)
st.sidebar.header("📡 Estado del Sistema")
status_col = st.sidebar.columns(2)
status_col[0].metric("API Backend", "Online 🟢")
status_col[1].metric("IoT Gateway", "Activo 🔵")

opcion = st.sidebar.radio("Navegación", ["🏭 Fábrica de Quesos", "🚨 Alertas IoT", "🌱 Invernadero FVH"])

# --- VISTA 1: FÁBRICA DE QUESOS ---
if opcion == "🏭 Fábrica de Quesos":
    st.header("🧀 Gestión de Producción Láctea")
    
    # 1. Formulario para Nuevo Lote (¡Adiós Swagger!)
    with st.expander("➕ Registrar Nuevo Lote", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo de Queso", ["Ricotta", "Pecorino", "Manchego", "Feta"])
            litros = st.number_input("Litros de Leche", min_value=1.0, value=10.0)
        with col2:
            peso = st.number_input("Peso Final (kg)", min_value=0.1, value=1.5)
            notas = st.text_area("Notas del Maestro Quesero")
        
        if st.button("Guardar Lote"):
            # Aquí llamamos a TU API real
            payload = {
                "fecha_elaboracion": pd.Timestamp.now().isoformat(),
                "tipo_queso": tipo,
                "litros_leche_usados": litros,
                "peso_salida_prensa_kg": peso,
                # Datos dummy para completar el modelo estricto
                "ph_inicial": 6.6, "ph_corte": 4.6, 
                "temp_coagulacion": 32, "tiempo_floculacion_min": 40,
                "peso_cuajada_fresca_kg": peso 
            }
            try:
                res = requests.post(f"{API_URL}/cheese-batches/", json=payload)
                if res.status_code == 200:
                    st.success(f"✅ Lote de {tipo} registrado con éxito!")
                    time.sleep(1)
                    st.rerun() # Recargar página
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"No se pudo conectar con el ERP: {e}")

    # 2. Tabla de Lotes Existentes
    st.subheader("Historial de Lotes")
    try:
        # Petición GET a tu API
        response = requests.get(f"{API_URL}/cheese-batches/")
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                
                # Limpieza de datos para mostrar
                df['fecha'] = pd.to_datetime(df['fecha_elaboracion']).dt.strftime('%d/%m/%Y %H:%M')
                
                # Calcular Rendimiento en tiempo real
                df['Rendimiento (%)'] = (df['peso_salida_prensa_kg'] / df['litros_leche_usados']) * 100
                
                # Mostrar tabla tuneada
                st.dataframe(
                    df[['id', 'fecha', 'tipo_queso', 'litros_leche_usados', 'peso_salida_prensa_kg', 'Rendimiento (%)']],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Métricas rápidas
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Producción", f"{df['peso_salida_prensa_kg'].sum():.1f} kg")
                col2.metric("Rendimiento Promedio", f"{df['Rendimiento (%)'].mean():.1f}%")
                col3.metric("Lotes Totales", len(df))
            else:
                st.info("No hay lotes registrados aún.")
    except Exception as e:
        st.warning(f"⚠️ El Backend parece estar apagado. Inicia 'uvicorn main:app' primero.")

# --- VISTA 2: ALERTAS (Placeholder) ---
elif opcion == "🚨 Alertas IoT":
    st.header("🔥 Centro de Alertas")
    st.info("Aquí conectaremos los logs de temperatura crítica.")
    # Simulación visual
    st.error("🚨 12/02/2026 17:45 - TEMPERATURA CRÍTICA: 15.2°C (Cámara 1)")

elif opcion == "🌱 Invernadero FVH":
    st.header("🌱 Control de Forraje Verde")
    st.success("Módulo listo para implementación.")