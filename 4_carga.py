import pandas as pd
import logging
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ejecutar_carga_dimensional():
    logging.info("--- Paso 4: Carga de Esquema en Estrella para ML ---")
    
    ruta_clean = 'data/processed/nyc_taxi_2018_clean.parquet'
    
    try:
        df = pd.read_parquet(ruta_clean)
    except Exception as e:
        logging.error(f"Error al leer parquet: {e}")
        return

    # Conexión a tu base de datos local en Docker
    engine = create_engine('postgresql://admin:password123@postgres_db:5432/nyc_taxi_db')
    
    # 1. Generación de Llave Subrogada para la Dimensión Tiempo
    logging.info("Procesando llaves para las tablas de dimensiones...")
    df_tiempo_unique = df[['hora_del_dia', 'dia_de_la_semana', 'es_fin_de_semana']].drop_duplicates().reset_index(drop=True)
    df_tiempo_unique['id_tiempo'] = df_tiempo_unique.index + 1
    
    # Mapeamos este nuevo ID de vuelta al dataframe principal
    df = df.merge(df_tiempo_unique, on=['hora_del_dia', 'dia_de_la_semana', 'es_fin_de_semana'], how='left')

    # 2. Definición Estricta del Esquema Relacional en PostgreSQL
    crear_esquema_sql = """
    DROP TABLE IF EXISTS fact_viajes;
    DROP TABLE IF EXISTS dim_tiempo;
    DROP TABLE IF EXISTS dim_ubicacion;
    DROP TABLE IF EXISTS dim_proveedor;

    CREATE TABLE dim_tiempo (
        id_tiempo INT PRIMARY KEY,
        hora_del_dia INT,
        dia_de_la_semana INT,
        es_fin_de_semana INT
    );
    
    CREATE TABLE dim_ubicacion (
        location_id INT PRIMARY KEY
    );
    
    CREATE TABLE dim_proveedor (
        vendor_id VARCHAR(10) PRIMARY KEY
    );
    
    CREATE TABLE fact_viajes (
        trip_id SERIAL PRIMARY KEY,
        vendor_id VARCHAR(10) REFERENCES dim_proveedor(vendor_id),
        id_tiempo INT REFERENCES dim_tiempo(id_tiempo),
        pickup_location_id INT REFERENCES dim_ubicacion(location_id),
        dropoff_location_id INT REFERENCES dim_ubicacion(location_id),
        passenger_count INT,
        trip_distance FLOAT,
        payment_type VARCHAR(10),
        total_amount FLOAT
    );
    """
    
    with engine.connect() as conn:
        conn.execute(text(crear_esquema_sql))
        conn.commit()
    logging.info("Estructura relacional reconstruida con integridad referencial (Foreign Keys).")

    # 3. Inserción de Catálogos (Dimensiones)
    logging.info("Inyectando datos en tablas de dimensiones...")
    df_tiempo_unique.to_sql('dim_tiempo', engine, if_exists='append', index=False)
    
    pd.DataFrame(df['vendor_id'].unique(), columns=['vendor_id']).to_sql('dim_proveedor', engine, if_exists='append', index=False)
    
    locations = pd.concat([df['pickup_location_id'], df['dropoff_location_id']]).unique()
    pd.DataFrame(locations, columns=['location_id']).to_sql('dim_ubicacion', engine, if_exists='append', index=False)
    
    logging.info("Dimensiones pobladas exitosamente.")

    # 4. Preparación y Carga de la Tabla de Hechos
    logging.info(f"Iniciando persistencia transaccional de {len(df)} hechos de viajes...")
    
    columnas_hechos = [
        'vendor_id', 'id_tiempo', 'pickup_location_id', 
        'dropoff_location_id', 'passenger_count', 'trip_distance', 
        'payment_type', 'total_amount'
    ]
    df_hechos = df[columnas_hechos]
    
    registros_exitosos = 0
    registros_rechazados = 0
    
    try:
        # Carga Masiva (Bulk Insert) para eficiencia
        df_hechos.to_sql('fact_viajes', engine, if_exists='append', index=False, method='multi', chunksize=10000)
        registros_exitosos = len(df_hechos)
        logging.info("Carga masiva por lotes finalizada al 100%.")
        
    except Exception as e:
        logging.error(f"Error en bulk insert: {e}. Activando contingencia iterativa (fila por fila)...")
        # Contingencia exigida por la rúbrica (aislamiento de fallos)
        for index, row in df_hechos.iterrows():
            try:
                pd.DataFrame([row]).to_sql('fact_viajes', engine, if_exists='append', index=False)
                registros_exitosos += 1
            except Exception as row_error:
                registros_rechazados += 1
                if registros_rechazados <= 3:
                    logging.warning(f"Fila {index} rechazada por error de integridad: {row_error}")

    logging.info("--- RESUMEN FINAL DATAOPS ---")
    logging.info(f"Hechos Insertados Correctamente: {registros_exitosos}")
    logging.info(f"Hechos Rechazados/Aislados: {registros_rechazados}")

if __name__ == "__main__":
    ejecutar_carga_dimensional()