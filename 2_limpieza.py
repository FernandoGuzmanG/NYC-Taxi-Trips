import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def procesar_datos():
    logging.info("--- Paso 2: Limpieza y Feature Engineering ---")
    
    ruta_raw = 'data/raw/nyc_taxi_2018_raw.parquet'
    ruta_processed = 'data/processed/nyc_taxi_2018_clean.parquet'

    logging.info("Cargando dataset en crudo...")
    df = pd.read_parquet(ruta_raw)
    registros_iniciales = len(df)
    
    # 1. Limpieza de anomalías para el modelo predictivo
    logging.info("Eliminando valores nulos y ruido estadístico...")
    df = df.dropna(subset=['pickup_location_id', 'dropoff_location_id', 'payment_type'])
    df = df.drop_duplicates()
    
    # Filtramos viajes inválidos (distancias en cero o tarifas negativas)
    df = df[(df['trip_distance'] > 0) & (df['trip_distance'] < 150)]
    df = df[(df['total_amount'] > 0)]
    df = df[(df['passenger_count'] > 0) & (df['passenger_count'] <= 6)]

    # 2. Estandarización de Fechas
    logging.info("Estandarizando tipos de datos temporales...")
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
    df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])

    # 3. Transformación (Feature Engineering) para ML
    logging.info("Extrayendo dimensiones temporales para el Esquema en Estrella...")
    df['hora_del_dia'] = df['pickup_datetime'].dt.hour
    df['dia_de_la_semana'] = df['pickup_datetime'].dt.dayofweek + 1 # Lunes=1, Domingo=7
    
    # Variable booleana (1 si es sábado o domingo, 0 si es día de semana)
    df['es_fin_de_semana'] = df['dia_de_la_semana'].apply(lambda x: 1 if x >= 6 else 0)

    # Resumen
    registros_finales = len(df)
    logging.info(f"Limpieza completada. Descartados por ruido: {registros_iniciales - registros_finales}")
    logging.info(f"Total de registros listos para modelamiento: {registros_finales}")

    # Guardar
    df.to_parquet(ruta_processed, index=False)
    logging.info(f"Dataset de alta calidad guardado en: {ruta_processed}")

if __name__ == "__main__":
    procesar_datos()