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

opcion = st.sidebar.radio("Navegación", ["🏭 Fábrica de Quesos", "🚨 Alertas IoT", "🌱 Invernadero FVH", "🛡️ Calidad y SSOP", "💰 Finanzas"])

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
            # Costos
            costo_leche = st.number_input("Costo Leche ($)", min_value=0.0, value=0.0, step=10.0)
            costo_operativo = st.number_input("Costos Operativos ($)", min_value=0.0, value=0.0, step=10.0)
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
                "peso_cuajada_fresca_kg": peso,
                # Financials
                "costo_leche_total": costo_leche,
                "costo_operativo": costo_operativo 
            }
            try:
                res = requests.post(f"{API_URL}/cheese-factory/batches/", json=payload)
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
        response = requests.get(f"{API_URL}/cheese-factory/batches/")
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                
                # Limpieza de datos para mostrar
                df['fecha'] = pd.to_datetime(df['fecha_elaboracion']).dt.strftime('%d/%m/%Y %H:%M')
                
                # Calcular Rendimiento en tiempo real
                df['Rendimiento (%)'] = (df['peso_salida_prensa_kg'] / df['litros_leche_usados']) * 100
                
                # Calcular Costo por Kg (Necesitamos lógica segura por si faltan columnas en historial viejo, aunque borraremos DB)
                if 'costo_leche_total' not in df.columns: df['costo_leche_total'] = 0.0
                if 'costo_operativo' not in df.columns: df['costo_operativo'] = 0.0
                
                df['Costo Total'] = df['costo_leche_total'] + df['costo_operativo']
                df['Costo/Kg'] = df.apply(lambda x: x['Costo Total'] / x['peso_salida_prensa_kg'] if x['peso_salida_prensa_kg'] > 0 else 0, axis=1)
                
                # Mostrar tabla tuneada
                st.dataframe(
                    df[['id', 'fecha', 'tipo_queso', 'litros_leche_usados', 'peso_salida_prensa_kg', 'Rendimiento (%)', 'Costo/Kg']],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Métricas rápidas
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Producción", f"{df['peso_salida_prensa_kg'].sum():.1f} kg")
                col2.metric("Rendimiento Promedio", f"{df['Rendimiento (%)'].mean():.1f}%")
                col3.metric("Costo Promedio/Kg", f"${df['Costo/Kg'].mean():.2f}")
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

# --- VISTA 3: INVERNADERO FVH ---
elif opcion == "🌱 Invernadero FVH":
    st.header("🌱 Gestión de Forraje Verde Hidropónico")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Nueva Siembra")
        with st.form("form_fvh"):
            tipo_semilla = st.selectbox("Semilla", ["Cebada", "Avena", "Maíz"])
            kilos_semilla = st.number_input("Kilos de Semilla", min_value=0.1)
            if st.form_submit_button("Iniciar Ciclo"):
                # Llamada al endpoint de GreenHouse que ya definimos en el Backend
                st.success(f"Ciclo de {tipo_semilla} iniciado.")
                
    with col2:
        st.subheader("Estado Ambiental")
        # Aquí conectarás los datos de telemetría de InfluxDB
        st.metric("Humedad Relativa", "85%", "+2%")
        st.metric("Temperatura Invernadero", "22°C", "-1°C")

# --- VISTA 4: CALIDAD Y SSOP (Nueva pestaña) ---
elif opcion == "🛡️ Calidad y SSOP":
    st.header("🛡️ Control de Calidad y Bioseguridad")
    
    tabs = st.tabs(["Limpieza y Desinfección", "Control de Agua"])
    
    with tabs[0]:
        st.subheader("Registro de Limpieza y Desinfección")
        with st.form("form_ssop"):
            area = st.text_input("Área o Equipo", placeholder="Ej: Tina Quesera, Prensa")
            tipo_acc = st.selectbox("Acción", ["Limpieza", "Desinfección", "Pre-Enjuague", "Enjuague Final"])
            quimico = st.text_input("Agente Químico (Ej: Ácido Peracético)")
            concentracion = st.text_input("Concentración (Ej: 200ppm)")
            operario = st.text_input("Responsable")
            
            if st.form_submit_button("Guardar Registro SSOP"):
                payload = {
                    "area_equipo": area, "tipo": tipo_acc,
                    "agente_quimico": quimico, "concentracion": concentracion,
                    "responsable": operario
                }
                res = requests.post(f"{API_URL}/quality/saneamiento/", json=payload)
                if res.status_code == 200:
                    st.success("Registro guardado exitosamente.")
    
    with tabs[1]:
        st.subheader("Control de Cloro y pH")
        # El MGAP exige análisis fisicoquímicos y microbiológicos periódicos
        cloro = st.number_input("Cloro Residual (ppm)", min_value=0.0, max_value=5.0, step=0.1)
        ph_agua = st.number_input("pH del Agua", min_value=0.0, max_value=14.0, value=7.0)
        
        if cloro < 0.3 or cloro > 1.5:
            st.warning("⚠️ El nivel de cloro está fuera del rango recomendado (0.3 - 1.5 ppm).")

# --- VISTA 5: FINANZAS ---
elif opcion == "💰 Finanzas":
    st.header("💰 Gestión Financiera")
    
    # 1. Obtener Resumen
    summary = {}
    try:
        res = requests.get(f"{API_URL}/finance/summary/")
        if res.status_code == 200:
            summary = res.json()
    except:
        st.warning("No se pudo conectar con el servicio financiero.")

    # 2. Mostrar KPIs
    if summary:
        col1, col2, col3 = st.columns(3)
        col1.metric("Ahorro Total", f"${summary.get('balance_total', 0):,.2f}")
        col2.metric("Ingresos", f"${summary.get('total_ingresos', 0):,.2f}", delta_color="normal")
        col3.metric("Gastos", f"${summary.get('total_gastos', 0):,.2f}", delta_color="inverse")
        
        st.divider()

        # 3. Meta de Ahorro (Gráfico)
        meta = summary.get("meta_activa")
        if meta:
            st.subheader(f"🎯 Meta: {meta['nombre']}")
            
            progreso = meta['progreso_pct']
            target = meta['objetivo']
            
            # Barra de progreso
            st.progress(min(progreso / 100, 1.0))
            st.caption(f"Has ahorrado un {progreso}% de la meta de ${target:,.2f}")
            
            # Gráfico de Torta Simple (Ahorrado vs Falta)
            ahorrado = summary.get('balance_total', 0)
            falta = max(target - ahorrado, 0)
            
            chart_data = pd.DataFrame({
                "Estado": ["Ahorrado", "Faltante"],
                "Monto": [ahorrado, falta]
            })
            
            st.bar_chart(chart_data, x="Estado", y="Monto")
            
        else:
            st.info("No hay metas financieras activas. Crea una desde la API.")
    
    # 4. Formulario Rápido de Transacción
    with st.expander("💸 Registrar Movimiento Rápido"):
        with st.form("quick_finance"):
            f_tipo = st.selectbox("Tipo", ["GASTO", "INGRESO"]) # Enum strings
            f_cat = st.text_input("Categoría", "General")
            f_monto = st.number_input("Monto", min_value=0.01)
            f_desc = st.text_input("Descripción")
            
            if st.form_submit_button("Registrar"):
                payload = {
                    "tipo": f_tipo,
                    "categoria": f_cat,
                    "monto": f_monto,
                    "descripcion": f_desc
                }
                res = requests.post(f"{API_URL}/finance/transactions/", json=payload)
                if res.status_code == 200:
                    st.success("Movimiento registrado!")
                    time.sleep(1)
                    st.rerun()