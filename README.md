# NYC Taxi Trips (2018) - DataOps Pipeline para Machine Learning

Este repositorio contiene la implementación técnica de un pipeline de datos (DataOps) enfocado en la preparación, limpieza y modelado dimensional del dataset público de viajes en taxi de Nueva York (2018). 

**Objetivo de Negocio:** La arquitectura conceptual de este proyecto está diseñada explícitamente para alimentar un **Modelo de Regresión de Machine Learning** cuyo propósito es predecir la tarifa total (`total_amount`) de un viaje basándose en factores geográficos y temporales.

---

## Arquitectura y Tecnologías
El proyecto implementa un flujo híbrido escalable utilizando las siguientes tecnologías:
* **Google Cloud BigQuery:** Como Data Warehouse de origen para la extracción optimizada mediante SQL.
* **Python (Pandas):** Para el procesamiento en memoria, limpieza, Feature Engineering y validación semántica.
* **Docker & Docker Compose:** Para garantizar la portabilidad total del entorno de ejecución e infraestructura.
* **PostgreSQL (Esquema en Estrella):** Como repositorio relacional de destino optimizado para consultas analíticas.
* **Formato Parquet:** Para la persistencia eficiente de datos intermedios.

---

## Requisitos Previos (Prerequisites)
Para ejecutar este pipeline desde cero en cualquier máquina, necesitas contar con:
1. **Docker Desktop** instalado y en ejecución.
2. Una cuenta activa en **Google Cloud Platform (GCP)**.
3. Un archivo de credenciales de cuenta de servicio de GCP (`credentials.json`) con permisos de **Usuario de BigQuery** en el proyecto correspondiente.

---

## Guía de Instalación y Configuración

Sigue estos pasos para levantar el entorno:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/NYC-Taxi-Trips.git](https://github.com/TU_USUARIO/NYC-Taxi-Trips.git)
   cd NYC-Taxi-Trips