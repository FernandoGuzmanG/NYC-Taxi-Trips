import pandas as pd
import logging

# Configuración de Logs (Evidencia para la consola y el video)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def limpiar_datos():
    logging.info("--- Iniciando Actividad 2.2.2: Limpieza y Transformación ---")
    
    # Rutas relativas según la estructura solicitada
    ruta_raw = 'data/raw/nyc_taxi_2018_raw.parquet'
    ruta_processed = 'data/processed/nyc_taxi_2018_clean.parquet'

    # 1. Cargar datos desde la carpeta raw 
    logging.info(f"Cargando dataset en crudo desde {ruta_raw}...")
    df = pd.read_parquet(ruta_raw)
    registros_iniciales = len(df)
    
    # 2. Eliminar nulos y duplicados 
    logging.info("Eliminando valores nulos y registros duplicados...")
    df = df.dropna()
    df = df.drop_duplicates()

    # 3. Limpieza de anomalías lógicas y valores fuera de rango 
    logging.info("Aplicando filtros lógicos de negocio...")
    df = df[(df['trip_distance'] > 0) & (df['trip_distance'] < 150)] # Viajes válidos
    df = df[(df['passenger_count'] > 0) & (df['passenger_count'] <= 6)] # Capacidad normal de taxi
    df = df[df['fare_amount'] >= 0]
    df = df[df['total_amount'] >= 0]

    # 4. Estandarizar formatos de fecha 
    logging.info("Estandarizando tipos de datos (Fechas)...")
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
    df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])

    # 5. Transformación: Crear nuevas columnas 
    logging.info("Creando columna derivada: trip_duration_minutes...")
    df['trip_duration_minutes'] = (df['dropoff_datetime'] - df['pickup_datetime']).dt.total_seconds() / 60.0
    # Descartamos viajes con duración negativa o absurda
    df = df[(df['trip_duration_minutes'] > 0) & (df['trip_duration_minutes'] < 300)]

    # Resumen de operaciones
    registros_finales = len(df)
    eliminados = registros_iniciales - registros_finales
    logging.info(f"Limpieza completada. Registros eliminados (anomalías/nulos): {eliminados}")
    logging.info(f"Total de registros limpios resultantes: {registros_finales}")

    # 6. Guardar el nuevo dataset procesado 
    df.to_parquet(ruta_processed, index=False)
    logging.info(f"Dataset limpio guardado exitosamente en: {ruta_processed}")

if __name__ == "__main__":
    limpiar_datos()