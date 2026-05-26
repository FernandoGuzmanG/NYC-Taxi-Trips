# NYC Taxi Trips (2018) - Pipeline de Datos

## Etapa 1: Ingesta de Datos
- **Fuente:** `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2018`
- **Script:** `1_ingesta_y_eda.py`
- **Descripción:** Extracción automatizada de 100,000 registros del mes de enero de 2018 aplicando selección de características en origen (10 columnas clave). Los datos se almacenan en formato `.parquet` en `/data/raw/`. Se incluye un Análisis Exploratorio de Datos (EDA) inicial.
- **Entorno:** Contenedor Dockerizado con Python 3.11.