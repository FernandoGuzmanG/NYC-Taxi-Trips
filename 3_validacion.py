import pandas as pd
import logging

# Configuración de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validar_datos():
    logging.info("--- Iniciando Actividad 2.3.2: Validación Estructural y Semántica ---")
    
    ruta_processed = 'data/processed/nyc_taxi_2018_clean.parquet'
    ruta_reporte = 'data/reports/reporte_errores.txt'
    
    logging.info(f"Cargando dataset procesado desde {ruta_processed}...")
    try:
        df = pd.read_parquet(ruta_processed)
    except Exception as e:
        logging.error(f"Error al cargar el archivo: {e}")
        return
        
    errores = []
    
    # 1. Validación Estructural: Columnas obligatorias
    logging.info("Realizando validación estructural...")
    cols_requeridas = ['vendor_id', 'pickup_datetime', 'dropoff_datetime', 'passenger_count', 'trip_distance', 'total_amount']
    for col in cols_requeridas:
        if col not in df.columns:
            errores.append(f"[ESTRUCTURAL] Falta columna obligatoria: {col}")
            
    # 2. Validación Estructural: Tipos de datos
    if not pd.api.types.is_numeric_dtype(df['total_amount']):
        errores.append("[ESTRUCTURAL] La columna 'total_amount' no es de tipo numérico.")

    # 3. Validación Semántica: Coherencia temporal
    logging.info("Realizando validación semántica (Reglas de Negocio)...")
    incoherencias_tiempo = df[df['pickup_datetime'] >= df['dropoff_datetime']]
    if not incoherencias_tiempo.empty:
        errores.append(f"[SEMÁNTICA] Se encontraron {len(incoherencias_tiempo)} viajes donde la fecha de término es igual o anterior a la de inicio.")
        
    # 4. Validación Semántica: Lógica financiera
    incoherencias_tarifa = df[df['total_amount'] < df['fare_amount']]
    if not incoherencias_tarifa.empty:
        errores.append(f"[SEMÁNTICA] Se encontraron {len(incoherencias_tarifa)} viajes donde el total cobrado es menor a la tarifa base.")

    # 5. Generación del Reporte Automático
    logging.info("Generando reporte de validación en /data/reports/ ...")
    with open(ruta_reporte, 'w', encoding='utf-8') as f:
        f.write("=== REPORTE DE VALIDACIÓN: NYC TAXI TRIPS 2018 ===\n\n")
        if not errores:
            f.write("ESTADO: ÉXITO.\nNo se detectaron errores estructurales ni semánticos en el dataset procesado.")
            logging.info("Validación exitosa. Cero errores detectados. Reporte generado.")
        else:
            f.write(f"ESTADO: ADVERTENCIA - Se detectaron {len(errores)} anomalías.\n\n")
            for error in errores:
                f.write(f"- {error}\n")
            logging.warning(f"Se detectaron {len(errores)} advertencias. Revise el reporte en {ruta_reporte}")

if __name__ == "__main__":
    validar_datos()