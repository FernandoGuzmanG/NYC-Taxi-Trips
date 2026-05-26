import pandas as pd
import logging
import os
from google.cloud import bigquery

# Configuración de Logs (Evidencia para el informe y consola)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def preparar_entorno():
    """Crea la estructura de directorios requerida por el pipeline."""
    carpetas = ['data/raw', 'data/processed', 'data/reports']
    for carpeta in carpetas:
        os.makedirs(carpeta, exist_ok=True)
    logging.info("Estructura de directorios verificada/creada.")

def ingestar_datos():
    """Extrae datos de BigQuery y los guarda en local."""
    logging.info("Iniciando proceso de ingesta de datos...")
    
    # Autenticación si estás en Colab (si es local con SDK, elimina esta línea)
    # auth.authenticate_user() 
    
    # Reemplaza con el ID de tu proyecto en Google Cloud
    project_id = 'inner-tokenizer-491314-d3' 
    client = bigquery.Client(project=project_id)
    
    # Extraemos los campos actualizados para el esquema de 2018
    query = """
        SELECT 
            vendor_id, pickup_datetime, dropoff_datetime, 
            passenger_count, trip_distance, 
            pickup_location_id, dropoff_location_id, 
            fare_amount, tip_amount, total_amount
        FROM 
            `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2018`
        WHERE 
            pickup_datetime >= '2018-01-01' AND pickup_datetime < '2018-02-01'
        LIMIT 100000
    """
    
    logging.info("Ejecutando consulta en BigQuery (NYC Taxi 2018)...")
    query_job = client.query(query)
    
    logging.info("Convirtiendo resultados a DataFrame...")
    df_raw = query_job.to_dataframe()
    
    # Guardar en formato Parquet (Consistente con tu propuesta técnica de la Ev1)
    ruta_raw = 'data/raw/nyc_taxi_2018_raw.parquet'
    df_raw.to_parquet(ruta_raw, index=False)
    logging.info(f"Ingesta finalizada exitosamente. Archivo en: {ruta_raw}")
    
    return df_raw

def analisis_exploratorio(df):
    """Realiza el EDA exigido en la retroalimentación."""
    logging.info("--- Iniciando Análisis Exploratorio (EDA) ---")
    
    print("\n1. Información General del Dataset:")
    print(df.info())
    
    print("\n2. Detección de Valores Nulos:")
    print(df.isnull().sum())
    
    print("\n3. Estadísticas Descriptivas (Detección de Anomalías):")
    # Formateamos para evitar notación científica y facilitar la lectura
    print(df.describe().apply(lambda s: s.apply('{0:.2f}'.format)))
    
    logging.info("--- EDA Finalizado ---")

if __name__ == "__main__":
    preparar_entorno()
    df_origen = ingestar_datos()
    analisis_exploratorio(df_origen)