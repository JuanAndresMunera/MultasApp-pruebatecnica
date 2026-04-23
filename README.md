# MultasApp-pruebatecnica

# 🚦 Sistema de Consulta Automatizada SIMIT - Analista N2

[cite_start]Solución integral diseñada para la extracción, procesamiento y almacenamiento de comparendos vehiculares, cumpliendo con los estándares de arquitectura de software y automatización técnica sin herramientas RPA[cite: 4, 24].

---

## [cite_start]🏗️ Arquitectura y Decisiones Técnicas [cite: 121, 123]

El proyecto se fundamenta en una **arquitectura por capas** para garantizar la separación de responsabilidades:

* [cite_start]**Backend:** Construido con **FastAPI**, permitiendo una gestión asíncrona de peticiones y validación estricta de datos con Pydantic[cite: 10, 93].
* [cite_start]**Automatización:** Uso de **Playwright** para el scraping técnico de la fuente externa (SIMIT)[cite: 8, 33].
* [cite_start]**Persistencia:** **PostgreSQL** como motor relacional para el registro histórico y auditoría de datos[cite: 12, 106].
* [cite_start]**Frontend:** Interfaz liviana y funcional para el usuario final[cite: 11, 37].

### 🧠 El Proceso de Investigación (Bitácora de Ingeniería)
Durante el desarrollo, realicé una **ingeniería inversa** del portal SIMIT para intentar conectar con su API interna directamente vía protocolos HTTP. Se identificó un flujo de seguridad basado en un desafío matemático (**Proof of Work**) y validación de cookies dinámicas. 

Aunque se logró replicar el intercambio de mensajes inicial, las medidas de seguridad del sitio (fingerprinting) sugerían una posible inestabilidad a largo plazo mediante peticiones crudas. [cite_start]Por ello, opté por **Playwright**; esta decisión técnica asegura que el flujo de autorización y gestión de cookies sea manejado nativamente por el motor del navegador, garantizando fiabilidad y resiliencia en la extracción[cite: 14].

---

## [cite_start]🚀 Guía de Ejecución Paso a Paso [cite: 122]

### 1. Preparación del Entorno
Clona el repositorio y crea un entorno virtual para aislar las dependencias:
```bash
python -m venv venv
# Activar en Windows:
.\venv\Scripts\activate
# Instalar librerías:
pip install -r requirements.txt
playwright install chromium
2. Base de Datos (PostgreSQL) La persistencia es fundamental para el cumplimiento del Módulo 4.Crea una base de datos en PostgreSQL llamada multas_db (o el nombre de tu preferencia).Ejecuta el script de migración ubicado en backend/db/schema.sql en tu gestor (pgAdmin/DBeaver) para levantar la estructura de tablas necesaria.Configura tus credenciales en el archivo .env.3. Ejecución del Backend (API REST) Para levantar el servidor de desarrollo, sitúate en la carpeta backend y ejecuta:Bashuvicorn main:app --reload
La API estará disponible en http://127.0.0.1:8000. Puedes consultar la documentación interactiva en /docs.4. Ejecución del Frontend Para visualizar la interfaz de usuario:Abre el archivo frontend/index.html en Visual Studio Code.Usa la extensión Live Server (clic derecho -> Open with Live Server).Esto levantará el formulario donde podrás realizar consultas individuales e histórico.🛠️ Reglas de Negocio Implementadas Validación de Placa: El sistema exige y valida el formato de la placa antes de procesar.Trazabilidad Total: Toda consulta, sea exitosa o fallida, se registra en la base de datos para auditoría.Resiliencia Masiva: En consultas por lote, el sistema utiliza concurrencia para asegurar que el error en una placa no detenga el procesamiento de las demás.Errores Controlados: Respuestas claras ante caídas de la fuente externa.📈 Limitaciones y Mejoras Futuras Limitación: El tiempo de respuesta depende totalmente de la latencia del portal SIMIT.Mejora: Implementar Celery con Redis para mover las consultas masivas a procesos de fondo (Background Tasks) y mejorar la experiencia de usuario.Mejora: Integrar rotación de proxies para evitar bloqueos por alta demanda de consultas.