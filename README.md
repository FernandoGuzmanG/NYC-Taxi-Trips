# NYC Taxi Trips (2018) - Pipeline de Datos

## Etapa 1: Ingesta de Datos Automatizada
- **Fuente de Origen:** `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2018`
- **Script Executable:** `1_ingesta_y_eda.py`
- **Descripción:** Extracción automatizada de una muestra de 100,000 registros del mes de enero de 2018. Aplica selección de características en origen (Feature Selection) extrayendo únicamente 10 columnas fundamentales para mitigar latencia de red y optimizar el uso de memoria en memoria local.
- **Análisis Exploratorio (EDA):** Bloque integrado que evalúa tipos de datos, recuento de valores nulos y estadísticas descriptivas para la identificación temprana de anomalías operacionales.
- **Entorno Técnico:** Infraestructura portable basada en contenedores Docker (Python 3.11-slim) con volumen enlazado.
- **Persistencia Inicial:** Datos en crudo almacenados en formato columnar optimizado `/data/raw/nyc_taxi_2018_raw.parquet`.

## Etapa 2: Limpieza y Transformación del Dataset
- **Script Executable:** `2_limpieza.py`
- **Descripción:** Procesamiento automatizado de la capa de datos en crudo para asegurar consistencia e integridad.
- **Criterios Técnicos de Limpieza:**
  - Eliminación sistemática de registros con valores nulos (`dropna`) y filas duplicadas (`drop_duplicates`).
  - Filtrado por lógica de negocio: distancias de viaje mayores a 0 millas, cantidad de pasajeros válida (entre 1 y 6) y montos financieros de tarifas no negativos.
  - Estandarización de tipos de datos convirtiendo las marcas de tiempo a formato `datetime64`.
- **Creación de Columnas Derivadas:** Construcción de la métrica de negocio `trip_duration_minutes` calculada programáticamente mediante la diferencia temporal entre el término (`dropoff_datetime`) y el inicio (`pickup_datetime`) del viaje en taxi.
- **Persistencia Procesada:** Dataset limpio y estructurado almacenado en `/data/processed/nyc_taxi_2018_clean.parquet`.