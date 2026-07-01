import pandas as pd
import numpy as np
import os
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, recall_score, confusion_matrix, roc_curve, auc

# Configuración de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def entrenar_y_evaluar_ia():
    logging.info("--- Paso 5: Entrenamiento y Evaluación del Modelo IA (Clasificación) ---")
    
    # 1. CONEXIÓN A POSTGRESQL
    # Ajustado a tus credenciales locales
    engine = create_engine('postgresql://admin:password123@postgres_db:5432/nyc_taxi_db')
    os.makedirs("data/reports/graficos", exist_ok=True)

    logging.info("Extrayendo datos con JOIN desde el Esquema en Estrella...")
    # Hacemos un JOIN con dim_tiempo para traer la hora y fin de semana
    query = """
        SELECT 
            f.trip_distance, 
            f.payment_type, 
            f.total_amount, 
            t.hora_del_dia,
            t.es_fin_de_semana
        FROM fact_viajes f
        JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
    """
    
    try:
        df = pd.read_sql(query, engine)
        logging.info(f"Datos extraídos con éxito: {len(df)} registros.")
    except Exception as e:
        logging.error(f"Error conectando a BD: {e}. Usando datos de prueba para avanzar...")
        # Fallback de emergencia por si Docker está apagado
        np.random.seed(42)
        df = pd.DataFrame({
            'trip_distance': np.random.uniform(0.5, 20.0, 10000),
            'payment_type': np.random.choice(['1', '2'], 10000),
            'total_amount': np.random.uniform(5.0, 80.0, 10000),
            'hora_del_dia': np.random.randint(0, 24, 10000),
            'es_fin_de_semana': np.random.choice([0, 1], 10000)
        })

    # ==========================================
    # 2. PREPARACIÓN DEL PROBLEMA (CLASIFICACIÓN)
    # ==========================================
    logging.info("Preparando variable objetivo (Transformación a Clasificación Binaria)...")

    # Definimos "Rentable" (1) si la tarifa total supera los 15 dólares
    umbral_rentabilidad = 15.0
    df['es_rentable_real'] = (df['total_amount'] >= umbral_rentabilidad).astype(int)

    # FEATURE ENGINEERING: Convertir VARCHAR a numérico para el Random Forest
    df = pd.get_dummies(df, columns=['payment_type'], drop_first=True)

    # Separamos variables predictoras (X) de la variable objetivo (y)
    X = df.drop(columns=['total_amount', 'es_rentable_real'])
    y = df['es_rentable_real']

    # ==========================================
    # 3. ANÁLISIS BIVARIADO (MATRIZ DE CORRELACIÓN)
    # ==========================================
    logging.info("Generando Matriz de Correlación (Heatmap)...")
    plt.figure(figsize=(8, 6))
    
    # Unimos temporalmente X e y para ver cómo se relacionan entre sí
    df_corr = X.copy()
    df_corr['es_rentable_real'] = y
    
    sns.heatmap(df_corr.corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Matriz de Correlación (Análisis Bivariado)")
    plt.tight_layout()
    plt.savefig("data/reports/graficos/matriz_correlacion.png")
    plt.close()

    # ==========================================
    # 4. ENTRENAMIENTO DEL MODELO (70/30)
    # ==========================================
    logging.info("Iniciando partición de datos (70% Train / 30% Test)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

    logging.info("Entrenando algoritmo Random Forest Classifier...")
    modelo_rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    modelo_rf.fit(X_train, y_train)

    # Generamos predicciones sobre el 30% que el modelo no ha visto
    y_pred = modelo_rf.predict(X_test)
    y_prob = modelo_rf.predict_proba(X_test)[:, 1] # Probabilidad porcentual de ser rentable (1)

    # ==========================================
    # 5. EVALUACIÓN Y MÉTRICAS (RÚBRICA PARCIAL 3)
    # ==========================================
    logging.info("Calculando métricas de evaluación...")
    accuracy = accuracy_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)

    # Curva ROC y AUC
    fpr, tpr, thresholds = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    gini = (2 * roc_auc) - 1 # Fórmula matemática del Gini

    # Exportar resultados a un archivo de texto para el informe
    with open("data/reports/reporte_ia_metricas.txt", "w") as f:
        f.write("=== REPORTE DE RENDIMIENTO IA (CLASIFICACIÓN) ===\n")
        f.write(f"Accuracy (Exactitud total): {accuracy:.4f}\n")
        f.write(f"Recall (Sensibilidad a viajes rentables): {recall:.4f}\n")
        f.write(f"Área bajo la Curva (AUC): {roc_auc:.4f}\n")
        f.write(f"Coeficiente de Gini: {gini:.4f}\n")
        f.write("\nNota: Se prioriza el Recall para evitar que el negocio deje pasar oportunidades rentables (Falsos Negativos).\n")

    logging.info("Generando gráfico: Matriz de Confusión...")
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Normal (0)', 'Rentable (1)'], yticklabels=['Normal (0)', 'Rentable (1)'])
    plt.title('Matriz de Confusión - Detección de Rentabilidad')
    plt.ylabel('Valor Real (Base de Datos)')
    plt.xlabel('Predicción del Modelo de IA')
    plt.tight_layout()
    plt.savefig("data/reports/graficos/matriz_confusion.png")
    plt.close()

    logging.info("Generando gráfico: Curva ROC...")
    plt.figure(figsize=(6, 4))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'Curva ROC (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlabel('Tasa de Falsos Positivos')
    plt.ylabel('Tasa de Verdaderos Positivos')
    plt.title(f'Curva ROC (Coef. Gini: {gini:.2f})')
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig("data/reports/graficos/curva_roc.png")
    plt.close()

    # ==========================================
    # 6. EXPORTAR A POSTGRESQL (INSUMO PARA DASHBOARD BI)
    # ==========================================
    logging.info("Preparando tabla de resultados finales para Power BI...")
    df_resultados = X_test.copy()
    df_resultados['es_rentable_real'] = y_test
    df_resultados['es_rentable_prediccion'] = y_pred
    df_resultados['probabilidad_rentable'] = np.round(y_prob, 2)

    try:
        # Reemplazamos la tabla si ya existe para tener siempre la última predicción
        df_resultados.to_sql('predicciones_ia', engine, if_exists='replace', index=False)
        logging.info("¡ÉXITO! La tabla 'predicciones_ia' está lista en PostgreSQL para conectar el Dashboard.")
    except Exception as e:
        logging.error(f"No se pudo guardar en PostgreSQL: {e}. Guardando CSV local como respaldo.")
        df_resultados.to_csv('data/predicciones_ia_final.csv', index=False)

    logging.info("--- Pipeline Fase 3 (IA) finalizado ---")

if __name__ == "__main__":
    entrenar_y_evaluar_ia()