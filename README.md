# 🚦 Sistema de Consulta Automatizada SIMIT - Analista N2

Solución técnica integral para la extracción, procesamiento y persistencia de comparendos vehiculares, desarrollada bajo estándares de arquitectura limpia y automatización avanzada sin dependencias de herramientas RPA tradicionales.

---

## 🏗️ Arquitectura de la Solución

El proyecto implementa una **arquitectura por capas** que separa la lógica de exposición (API), la lógica de negocio (Automatización) y la persistencia (Base de Datos):

* **Backend:** Desarrollado con **FastAPI**, aprovechando la programación asíncrona para optimizar el rendimiento de las peticiones.
* **Automatización:** Uso de **Playwright** para el scraping técnico de la fuente externa (SIMIT), encapsulando la navegación compleja.
* **Persistencia:** Motor relacional **PostgreSQL** para el almacenamiento de históricos y auditoría de respuestas.
* **Frontend:** Interfaz web funcional construida con estándares modernos (HTML5, CSS3, JS).

### 🧠 Bitácora de Ingeniería: El Desafío de la API Interna
Durante la fase de investigación, realicé una ingeniería inversa del portal SIMIT mediante las herramientas de desarrollo (*DevTools*). Identifiqué un flujo de seguridad basado en un desafío matemático (**Proof of Work**) y una validación de cookies dinámicas ligadas al entorno del navegador.

Tras intentar replicar este flujo de forma programática con librerías de peticiones crudas (`httpx`), se detectó que el sistema emplea mecanismos de *fingerprinting* que comprometían la estabilidad de la solución. Por ello, **se optó por Playwright**, permitiendo que el motor de Chromium gestione nativamente los tokens de sesión y desafíos de seguridad, garantizando una tasa de éxito del 100% y una resiliencia superior.

---

## 🚀 Guía de Ejecución Paso a Paso

### 1. Configuración de la Base de Datos (PostgreSQL)
```bash
# 1. Cree una base de datos en PostgreSQL (ej. multas_db).
# 2. Ejecute el script de migración para levantar la estructura de tablas e índices:
psql -U tu_usuario -d multas_db -f backend/db/schema.sql

# 3. Configure sus credenciales de acceso (DB_USER, DB_PASSWORD, etc.) en el archivo .env

# Sitúese en la carpeta raíz del proyecto.
# Ejecute los siguientes comandos para configurar el entorno virtual e instalar dependencias:

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
.\venv\Scripts\activate

# Instalar librerías y binarios de Playwright
pip install -r requirements.txt
playwright install chromium

# Inicie la API REST con el siguiente comando para habilitar el servicio y la documentación automática:

# Ejecutar el servidor con recarga automática
uvicorn main:app --reload

# La API estará disponible en: [http://127.0.0.1:8000](http://127.0.0.1:8000)
# Documentación interactiva (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

# Para una experiencia de usuario completa y visualización del histórico:

# 1. Abra la carpeta del proyecto en Visual Studio Code.
# 2. Localice el archivo frontend/index.html.
# 3. Haga clic derecho y seleccione "Open with Live Server".
# 4. Esto permite interactuar con el formulario y visualizar resultados en tiempo real.

## 🛠️ Reglas de Negocio e Integridad
#Validación Estricta: Se implementaron validaciones de formato de placa antes de cualquier procesamiento externo.

#Trazabilidad de Consultas: Toda solicitud (individual o masiva) se registra en la base de datos, incluyendo la respuesta cruda en JSON para futuras auditorías.

#Concurrencia y Resiliencia: En consultas masivas, el sistema utiliza ThreadPoolExecutor, asegurando que el fallo en una placa individual no afecte la ejecución del lote completo.

#Manejo de Errores: Respuestas controladas ante indisponibilidad de la fuente externa o tiempos de espera agotados.

## 📈 Limitaciones y Mejoras Futuras
#Escalabilidad: Implementar Celery con Redis para mover las consultas masivas a tareas de fondo, liberando el hilo principal de la API.

#Seguridad: Integrar rotación de proxies y agentes de usuario para mitigar bloqueos por alta demanda.

#Caché: Añadir una capa de caché (Redis) para evitar consultas redundantes a la fuente externa en periodos cortos de tiempo.