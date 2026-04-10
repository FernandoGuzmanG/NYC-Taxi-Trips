# NYC Taxi Trips (2018) - Gestión de Datos para IA

Este repositorio contiene la arquitectura y el flujo de procesamiento de datos para el caso de estudio **Google Cloud NYC Taxi Trips (2018)**. 

El proyecto fue desarrollado bajo un enfoque académico utilizando una **Arquitectura de Pipeline Híbrido de IA**, ideal para procesar grandes volúmenes de datos históricos (lotes) y preparar la información para el entrenamiento de modelos de Machine Learning.

## Arquitectura y Tecnologías

El flujo de trabajo se divide en 4 fases basadas en la metodología PMBOK, utilizando el siguiente stack tecnológico:

* **Extracción y EDA:** Google Cloud BigQuery (SQL)
* **Transformación y Limpieza (Silver/Gold):** Python, Pandas, Apache Spark (Jupyter Notebooks)
* **Contenedores y Portabilidad:** Docker
* **Automatización CI/CD:** GitHub Actions

## Estructura del Repositorio

* `/docs`: Documentación técnica (DFD, PMBOK, WBS, Diccionario de Datos).
* `/notebooks`: Cuadernos de Jupyter para análisis exploratorio (EDA) y limpieza.
* `/scripts`: Scripts de procesamiento en Python.
* `.github/workflows`: Archivos de configuración para el pipeline automatizado (CI/CD).
* `Dockerfile`: Instrucciones para levantar el entorno contenerizado.

## Cómo ejecutar este proyecto localmente

Sigue estos pasos para levantar el entorno de desarrollo en tu máquina asegurando la misma configuración para todo el equipo.

### Prerrequisitos
* Tener [Docker](https://www.docker.com/) instalado en tu equipo.
* Tener Git instalado.

### Instalación

1. Clona este repositorio en tu máquina local:
   ```bash
   git clone [https://github.com/TU-USUARIO/nyc-taxi-trips-2018.git](https://github.com/TU-USUARIO/nyc-taxi-trips-2018.git)
   cd nyc-taxi-trips-2018
