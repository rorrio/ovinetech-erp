import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from datetime import date, datetime, timedelta

# Import models to ensure they are registered (optional if just reading tables via pandas)
# but good practice for ensuring environment consistency
# We need to add src to path if running from root
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from shared.database import sqlite_url, connect_args

# --- Configuration ---
st.set_page_config(page_title="OvineTech 4.0 - Centro de Mando", layout="wide")

# --- Database Connection ---
@st.cache_resource
def get_engine():
    return create_engine(sqlite_url, connect_args=connect_args)

@st.cache_data(ttl=60) # Refresh data every minute
def load_data():
    engine = get_engine()
    query = """
    SELECT 
        animal.id, 
        animal.rfid_tag, 
        animal.caravana_visual, 
        animal.raza, 
        animal.fecha_nacimiento, 
        animal.sexo, 
        animal.origen, 
        animal.estado_productivo, 
        animal.peso_actual, 
        animal.fecha_ultima_pesada
    FROM animal
    """
    try:
        df = pd.read_sql(query, engine)
        # Convert date columns
        df['fecha_nacimiento'] = pd.to_datetime(df['fecha_nacimiento']).dt.date
        df['fecha_ultima_pesada'] = pd.to_datetime(df['fecha_ultima_pesada'])
        
        # Calculate Age (Months) in pandas for display
        today = date.today()
        # Simplified age calc
        df['edad_meses'] = df['fecha_nacimiento'].apply(
            lambda d: round(((today.year - d.year) * 12 + (today.month - d.month)) + (today.day - d.day)/30.44, 1) if pd.notnull(d) else 0
        )
        return df
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return pd.DataFrame()

# --- Main App ---
def main():
    st.title("🐑 OvineTech 4.0 - Centro de Mando")
    st.markdown("---")

    df = load_data()

    if df.empty:
        st.warning("No hay datos en el rebaño. Por favor, cargue datos usando ingest_flock.py")
        return

    # --- Sidebar Filters ---
    st.sidebar.header("Filtros")
    
    # Raza Filter
    razas = df['raza'].unique().tolist()
    selected_razas = st.sidebar.multiselect("Raza", razas, default=razas)
    
    # Estado Filter
    estados = df['estado_productivo'].unique().tolist()
    selected_estados = st.sidebar.multiselect("Estado Productivo", estados, default=estados)

    # Filter Data
    df_filtered = df[
        (df['raza'].isin(selected_razas)) & 
        (df['estado_productivo'].isin(selected_estados))
    ]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Animales filtrados: {len(df_filtered)}")

    # --- KPIs ---
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total del Rebaño", len(df_filtered))

    with col2:
        milking_count = len(df_filtered[df_filtered['estado_productivo'].str.upper() == 'LACTANCIA'])
        st.metric("En Ordeñe 🥛", milking_count)

    with col3:
        # Próximos Partos (Gestación > 4 months approx, or just defined as specific query logic)
        # Requirement: "Gestación" with birth in next 30 days. 
        # But we only have 'fecha_nacimiento' (Animal Age), not 'expected_birth_date' for the animal itself giving birth.
        # The schema doesn't have 'pregnancy_start_date'. 
        # We will simulate this logic: 
        # Assumption: If 'Gestación', we assume they are pregnant. 
        # Without pregnancy date, we can't calculate due date exactly.
        # For DEMO purposes: We will count all 'Gestación' animals as "En Gestación"
        # OR if we want to simulate "Próximos partos", we might need to mock a due date or just show total Gestation.
        # Let's show "En Gestación" as the metric for now to be accurate to data, 
        # or mock a random selection if the user really wants the "30 days" KPI. 
        # Given strict requirement "Cantidad de animales en 'Gestación' con fecha de parto en los próximos 30 días",
        # I will note that we lack that field and just count all Gestation for now to avoid crashing, 
        # or maybe randomly assign due dates in a real app this would be a separate table 'Preñeces'.
        gestation_count = len(df_filtered[df_filtered['estado_productivo'] == 'Gestación'])
        st.metric("En Gestación 🤰", gestation_count, delta="Faltan datos de servicio")

    # --- Charts ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Distribución por Estado")
        if not df_filtered.empty:
            count_by_status = df_filtered['estado_productivo'].value_counts().reset_index()
            count_by_status.columns = ['Estado', 'Cantidad']
            fig_bar = px.bar(count_by_status, x='Estado', y='Cantidad', color='Estado', text_auto=True)
            st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("Composición Racial")
        if not df_filtered.empty:
            count_by_race = df_filtered['raza'].value_counts().reset_index()
            count_by_race.columns = ['Raza', 'Cantidad']
            fig_pie = px.pie(count_by_race, names='Raza', values='Cantidad', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

    # --- Simulación de Producción ---
    st.markdown("### 🥛 Proyección de Leche")
    with st.expander("Configurar Simulación", expanded=True):
        avg_yield = st.slider("Rendimiento Promedio por Oveja (L/día)", 0.5, 3.0, 1.2, 0.1)
        estimated_daily = milking_count * avg_yield
        st.success(f"Producción Diaria Estimada: **{estimated_daily:.1f} Litros**")

    # --- Atención Requerida ---
    st.markdown("### ⚠️ Atención Requerida")
    st.markdown("Animales que requieren revisión (Criterio: Peso < 30kg o Estado 'Gestación')")
    
    # Filter for attention
    # Criteria: Weight < 30 OR Gestation (as "close to birth" proxy for demo)
    attention_mask = (df_filtered['peso_actual'] < 30) | (df_filtered['estado_productivo'] == 'Gestación')
    df_attention = df_filtered[attention_mask].copy()

    if not df_attention.empty:
        # Format columns
        df_display = df_attention[['caravana_visual', 'raza', 'estado_productivo', 'peso_actual', 'edad_meses', 'rfid_tag']]
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No hay animales que requieran atención urgente según los filtros actuales.")

if __name__ == "__main__":
    main()
