import pandas as pd
import logging
import os
from google.cloud import bigquery

# Configuración de Logs (Evidencia para el informe y consola)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def preparar_entorno():
    carpetas = ['data/raw', 'data/processed', 'data/reports']
    for carpeta in carpetas:
        os.makedirs(carpeta, exist_ok=True)
    logging.info("Estructura de directorios verificada/creada.")

def ingestar_datos():
    logging.info("Iniciando proceso de ingesta de datos (Muestra 10% - Enero 2018)...")
    
    project_id = 'inner-tokenizer-491314-d3' 
    client = bigquery.Client(project=project_id)
    
    # Consulta orientada al modelo predictivo de tarifas
    query = """
        SELECT 
            vendor_id, pickup_datetime, dropoff_datetime, 
            passenger_count, trip_distance, 
            pickup_location_id, dropoff_location_id, 
            payment_type, total_amount
        FROM 
            `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2018`
        WHERE 
            pickup_datetime >= '2018-01-01' AND pickup_datetime < '2018-02-01'
            AND RAND() < 0.1
    """
    
    query_job = client.query(query)
    logging.info("Convirtiendo resultados a DataFrame (Esto puede tardar unos segundos)...")
    df_raw = query_job.to_dataframe()
    
    ruta_raw = 'data/raw/nyc_taxi_2018_raw.parquet'
    df_raw.to_parquet(ruta_raw, index=False)
    logging.info(f"Ingesta finalizada. {len(df_raw)} registros guardados en: {ruta_raw}")
    
    return df_raw

def analisis_exploratorio(df):
    logging.info("--- Iniciando Análisis Exploratorio (EDA) Orientado a ML ---")
    print("\n1. Información General del Dataset:")
    print(df.info())
    print("\n2. Detección de Valores Nulos:")
    print(df.isnull().sum())
    print("\n3. Distribución de la Variable Objetivo (total_amount):")
    print(df['total_amount'].describe().apply(lambda s: '{0:.2f}'.format(s)))
    logging.info("--- EDA Finalizado ---")

if __name__ == "__main__":
    preparar_entorno()
    df_origen = ingestar_datos()
    analisis_exploratorio(df_origen)