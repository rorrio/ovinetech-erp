# Estructura del Proyecto OvineTech ERP

Este documento detalla la estructura actual del proyecto y la funcionalidad de cada archivo implementado.

## Raíz del Proyecto (`c:\Ovine Tech ERP`)

-   **`dashboard.py`**: Aplicación Streamlit principal "Centro de Control".
    -   Panel de estado del sistema (API, IoT).
    -   Gestión de la Fábrica de Quesos (Registro y visualización de lotes).
    -   Invernadero FVH (Inicio de ciclos y visualización de sensores simulados).
    -   Calidad y SSOP (Formularios para registros de limpieza y control de agua).
    -   Finanzas (Visualización de metas y registro rápido de transacciones).
-   **`flock_dashboard.py`**: Tablero de control específico para la gestión del rebaño (Streamlit).
    -   Visualización de KPIs del rebaño (Total animales, lactancia, etc.).
    -   Gráficos de distribución por raza y estado productivo.
    -   Tabla filtrable de animales.
    -   Calculadora de proyección de leche.
-   **`main.py`**: Punto de entrada de la aplicación FastAPI (`uvicorn main:app`).
    -   Configura la base de datos y las tablas al inicio.
    -   Inicia el planificador (scheduler) de mantenimiento.
    -   Incluye los routers de los distintos módulos (incluyendo Finanzas).
    -   Define un endpoint básico para recibir alertas IoT.
-   **`ovinetech.db`**: Base de datos SQLite del sistema.
-   **`requirements.txt`**: Lista de dependencias del proyecto.
-   **`seed_ricotta.py`**: Script de inicialización de datos (crea un lote de queso de prueba).
-   **`test_telegram_alert.py`**: Script simple para probar el envío de notificaciones a Telegram.

## Directorio Fuente (`src/`)

### 1. `src/shared/` - Utilidades Compartidas
-   **`database.py`**:
    -   Configuración del motor de base de datos (SQLAlchemy/SQLModel).
    -   Función `get_session` para inyección de dependencias en FastAPI.
    -   Función `create_db_and_tables` para inicialización.

### 2. `src/core/` - Núcleo del Sistema
-   **`notifications.py`**:
    -   Función `send_telegram_alert`: Envía mensajes al bot de Telegram configurado.

### 3. `src/cheese_factory/` - Módulo de Quesería
-   **`models.py`**:
    -   `LoteQueso`: Modelo de base de datos para lotes de producción (tipo, litros, parámetros fisicoquímicos).
    -   `MaduracionLog`: Registro de seguimiento de maduración (peso, humedad).
-   **`router.py`**:
    -   Endpoints API para crear y listar lotes de queso (`/cheese-factory/batches/`).

### 4. `src/greenhouse/` - Módulo de Invernadero (FVH)
-   **`models.py`**:
    -   `FVHCiclo`: Ciclo de producción de Forraje Verde Hidropónico (siembra, semilla).
    -   `FVHCosecha`: Registro del resultado final de la cosecha (peso, ratio de conversión).
-   **`router.py`**:
    -   Endpoints API para gestionar ciclos (`/greenhouse/cycles/`) y registrar cosechas (`/greenhouse/harvests/`).

### 5. `src/ovine_manager/` - Gestión del Rebaño
-   **`models.py`**:
    -   `Animal`: Modelo principal de la oveja (RFC, raza, edad, relaciones de genealogía). Combina SQLModel con estilo imperativo de SQLAlchemy 2.0.
    -   `LoteOvejas`: Agrupación de animales.
    -   `EventoAlimentacion`: Registro de alimentación (conexión con FVH).
    -   `OrdenieDiario`: Registro de producción de leche.
-   **`schemas.py`**:
    -   Schemas Pydantic (`AnimalCreate`, `AnimalRead`) para validación y serialización de datos de la API.
-   **`router.py`**:
    -   Endpoints API para gestión de lotes de ovejas y eventos de alimentación (`/ovine-manager/...`).
-   **`ingest_flock.py`**:
    -   Script independiente para la importación masiva de animales desde un archivo CSV (`initial_flock.csv`). Maneja validación, normalización e idempotencia.

### 6. `src/quality_control/` - Calidad y SSOP
-   **`models.py`**:
    -   `RegistroSaneamiento`: Log de procedimientos de limpieza y desinfección (SSOP).
    -   `ControlAgua`: Registro de parámetros del agua (cloro, pH).
    -   `ControlPlagas`: Registro de inspección de trampas.
-   **`router.py`**:
    -   Endpoints API para registrar saneamientos y controles de agua (`/quality/...`).

### 7. `src/maintenance/` - Mantenimiento Predictivo y Agentes
-   **`agents.py`**:
    -   `MaintenanceAgent`: Lógica de negocio ("Agente") que valida si un equipo está apto para uso basándose en registros previos y reglas de tiempo (ventana de esterilidad).
-   **`api.py`**:
    -   Endpoint para recibir logs de limpieza (pensado para integración con IoT/Raspberry Pi).
-   **`scheduler.py`**:
    -   Configuración de `APScheduler` para ejecutar tareas de fondo.
    -   `run_sanitization_check`: Tarea periódica que verifica la caducidad de la limpieza en equipos críticos y envía alertas por Telegram.

### 8. `src/finance/` - Módulo Financiero
-   **`models.py`**:
    -   `Transaccion`: Registro de ingresos y gastos (fecha, tipo, monto, categoría).
    -   `MetaCapital`: Definición de objetivos de ahorro (monto objetivo, fecha límite).
-   **`router.py`**:
    -   Endpoints API para registrar transacciones y obtener resumen financiero (`/finance/...`).
