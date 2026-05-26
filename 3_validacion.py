import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validar_calidad_datos():
    logging.info("--- Validación Estructural y Semántica ---")
    
    ruta_processed = 'data/processed/nyc_taxi_2018_clean.parquet'
    ruta_reporte = 'data/reports/reporte_errores.txt'
    
    # Crea la carpeta de reportes si no existe
    os.makedirs('data/reports', exist_ok=True)
    
    logging.info("Cargando dataset transformado...")
    try:
        df = pd.read_parquet(ruta_processed)
    except Exception as e:
        logging.error(f"Error al cargar archivo: {e}")
        return
        
    errores = []
    
    # 1. Validación Estructural: Columnas obligatorias (Nuestro Esquema Estrella)
    logging.info("Ejecutando Validación Estructural...")
    cols_requeridas = [
        'vendor_id', 'trip_distance', 'pickup_location_id', 
        'dropoff_location_id', 'total_amount', 'hora_del_dia', 
        'dia_de_la_semana', 'es_fin_de_semana'
    ]
    for col in cols_requeridas:
        if col not in df.columns:
            errores.append(f"[ESTRUCTURAL] Falta columna obligatoria para ML: {col}")

    # 2. Validación Semántica: Reglas de Negocio Estrictas
    logging.info("Ejecutando Validación Semántica...")
    
    # Regla: Las tarifas base mínimas en NYC rondan los $2.50. 
    # Tarifas totales excesivamente bajas (ej. menores a $1) son anomalías.
    tarifas_anomalas = df[df['total_amount'] < 1.0]
    if not tarifas_anomalas.empty:
        errores.append(f"[SEMÁNTICA] Se detectaron {len(tarifas_anomalas)} viajes con un total_amount menor a $1.00 USD (Posible error de taxímetro).")
        
    # Regla: Distancias absurdamente altas dentro de NYC (ej. > 100 millas)
    distancias_anomalas = df[df['trip_distance'] > 100.0]
    if not distancias_anomalas.empty:
        errores.append(f"[SEMÁNTICA] Se detectaron {len(distancias_anomalas)} viajes con distancias superiores a 100 millas (Posible error de GPS).")
        
    # Regla: Coherencia temporal
    incoherencias_tiempo = df[df['pickup_datetime'] >= df['dropoff_datetime']]
    if not incoherencias_tiempo.empty:
        errores.append(f"[SEMÁNTICA] Se detectaron {len(incoherencias_tiempo)} viajes donde dropoff_datetime <= pickup_datetime.")

    # 3. Generación del Reporte (Exigencia de la Rúbrica)
    logging.info("Generando reporte de auditoría automático...")
    with open(ruta_reporte, 'w', encoding='utf-8') as f:
        f.write("=== REPORTE DE CALIDAD DE DATOS (DATA QUALITY) ===\n")
        f.write("Proyecto: NYC Taxi Trips - Modelo Predictivo de Tarifas\n")
        f.write("====================================================\n\n")
        
        if not errores:
            f.write("ESTADO: APROBADO (🟢)\n")
            f.write("No se detectaron errores estructurales ni violaciones a reglas de negocio.\n")
            f.write("El dataset está certificado para su inserción en PostgreSQL.\n")
            logging.info("Validación exitosa (0 errores). Dataset certificado.")
        else:
            f.write(f"ESTADO: ADVERTENCIA (🟡) - {len(errores)} anomalías detectadas.\n\n")
            for error in errores:
                f.write(f"- {error}\n")
            logging.warning(f"Se detectaron {len(errores)} anomalías. Revise {ruta_reporte}")

if __name__ == "__main__":
    validar_calidad_datos()