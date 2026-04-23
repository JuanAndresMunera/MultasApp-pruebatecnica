# Sistema de Consulta Automatizada SIMIT - Analista N2

##  Descripción General

Solución técnica integral para la **extracción, procesamiento, consulta y persistencia de comparendos vehiculares en SIMIT**, desarrollada bajo principios de arquitectura limpia y automatización programática, **sin uso de herramientas RPA tradicionales**, cumpliendo las restricciones técnicas planteadas.

La solución implementa:

* Backend API con **FastAPI**
* Automatización web encapsulada con **Playwright**
* Persistencia con **PostgreSQL** y **SQLAlchemy**
* Frontend liviano en **HTML, CSS y JavaScript**
* Auditoría histórica de consultas
* Consulta individual y masiva de placas

---

# Arquitectura de la Solución

La solución sigue una **arquitectura por capas**, separando responsabilidades:

## Capa de Exposición (API)

* API REST construida con **FastAPI**
* Endpoints para:

  * Consulta individual
  * Consulta masiva
  * Histórico de consultas
* Validaciones de entrada con **Pydantic**
* Documentación interactiva con Swagger

---

## Capa de Automatización

Se utiliza **Playwright** como mecanismo técnico encapsulado para interactuar con la fuente externa (SIMIT).

Características:

* Intercepción de respuestas HTTP internas
* Bloqueo de recursos no necesarios para optimización
* Captura estructurada de datos
* Manejo de errores y timeouts
* Estrategia resiliente frente a mecanismos anti-bot

---

## Capa de Persistencia

Base de datos relacional con **PostgreSQL** para:

* Histórico de consultas
* Auditoría de respuestas crudas
* Registro de errores
* Trazabilidad operativa

ORM:

* **SQLAlchemy**

---

## Capa Frontend

Interfaz web ligera para:

* Consultar placas individuales
* Ejecutar consultas masivas
* Visualizar histórico

Tecnologías:

* HTML5
* CSS3
* JavaScript Vanilla

---

#  Bitácora de Ingeniería: Decisión Técnica sobre la Fuente Externa

Durante la investigación técnica se realizó ingeniería inversa del portal **SIMIT** usando herramientas DevTools.

Se identificó:

* Flujo con desafío matemático (**Proof of Work**)
* Cookies dinámicas ligadas al navegador
* Mecanismos de fingerprinting
* Validaciones de sesión que impedían consumo estable vía requests crudos

Inicialmente se intentó replicar el flujo con:

* `httpx`
* Consumo directo HTTP

Resultado:

* Baja estabilidad
* Tokens dinámicos inválidos
* Riesgo de bloqueo

## Decisión adoptada

Se optó por **Playwright + Chromium** para que el motor del navegador gestione:

* Sesiones
* Tokens
* Cookies
* Desafíos de seguridad

Esto permitió:

* Alta resiliencia
* Estabilidad operativa
* Automatización encapsulada sin RPA

---

#  Estructura del Proyecto

```bash
project/
│
├── backend/
│   ├── main.py
│   ├── scraper.py
│   ├── externalRequest.py
│   ├── database.py
│   ├── models.py
│   └── db/
│       └── schema.sql
│
├── frontend/
│   └── index.html
│
├── postman/
├── .env
├── requirements.txt
└── README.md
```

---

#  Guía de Ejecución Paso a Paso

## 1. Clonar el proyecto

```bash
git clone <repositorio>
cd <nombre-proyecto>
```

---

## 2. Configuración de Base de Datos (PostgreSQL)

Crear base de datos:

```sql
CREATE DATABASE multas_db;
```

Ejecutar script de esquema:

```bash
backend/db/schema.sql
```

Este script crea:

* Tabla de consultas
* Índices
* Estructura para auditoría

---

## 3. Configuración de variables de entorno

Crear archivo `.env`

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=multas_db
DB_USER=postgres
DB_PASSWORD=tu_password
```

---

## 4. Preparar entorno virtual

```bash
python -m venv venv
```

Activar entorno:

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

---

## 5. Instalar dependencias

```bash
pip install -r requirements.txt
```

Instalar navegador para Playwright:

```bash
playwright install chromium
```

---

## 6. Levantar el Backend

Ubicarse en `/backend`

```bash
uvicorn main:app --reload
```

Servidor:

```bash
http://127.0.0.1:8000
```

Swagger:

```bash
http://127.0.0.1:8000/docs
```

---

## 7. Ejecutar Frontend

Abrir el proyecto en Visual Studio Code.

Ir a:

```bash
frontend/index.html
```

Ejecutar con:

```bash
Open with Live Server
```

---

# 🔌 Endpoints Disponibles

## Health Check

```http
GET /
```

Respuesta:

```json
{
  "mensaje":"API Consulta Multas SIMIT activa"
}
```

---

## Consulta Individual

```http
POST /consulta-individual
```

Payload:

```json
{
  "placa":"ABC123"
}
```

---

## Consulta Masiva

```http
POST /consulta-masiva
```

Payload:

```json
{
  "placas":[
    "ABC123",
    "XYZ987"
  ]
}
```

---

## Histórico

```http
GET /historico
```

---

#  Reglas de Negocio e Integridad

## Validación estricta

Formato soportado:

```bash
ABC123
```

Se rechazan placas inválidas antes de consultar fuente externa.

---

## Trazabilidad

Cada consulta almacena:

* Placa
* Fecha
* Estado
* Cantidad de multas
* Respuesta cruda JSON
* Error si existe

---

## Resiliencia

* Fallo de una placa no rompe consulta masiva
* Manejo de timeouts
* Respuestas controladas ante caída de la fuente
* Aislamiento por consulta

---

## Optimización implementada

Bloqueo de recursos no esenciales:

```bash
Imágenes
Fonts
Media
Analytics
Trackers
```

Intercepción del endpoint interno en vez de scraping visual tradicional.

---

#  Stack Tecnológico

## Backend

```bash
Python
FastAPI
SQLAlchemy
Pydantic
Playwright
```

## Base de Datos

```bash
PostgreSQL
```

## Frontend

```bash
HTML5
CSS3
JavaScript
```

---

# Cumplimiento de Restricciones Técnicas

La solución cumple la restricción principal:

## No utiliza

```bash
UiPath
Automation Anywhere
Power Automate Desktop
Selenium como robot RPA
Macros tipo click-bot
```

## Sí utiliza (permitido)

```bash
Backend consumiendo servicios HTTP
Control web encapsulado técnicamente
APIs REST
Automatización con Python
Base de datos relacional
Frontend liviano
```

La automatización con Playwright se utiliza como:

* Encapsulamiento técnico
* Intercepción de tráfico
* Cliente de automatización programática

No como herramienta RPA.

---

# Modelo de Datos

Tabla principal:

```sql
consultas
```

Campos:

```bash
id_consulta
placa
fecha_consulta
tipo_consulta
estado
respuesta_cruda
cantidad_multas
mensaje_error
```

---

# Pruebas

Colección de pruebas:

```bash
/postman
```

Incluye:

* Consulta individual
* Consulta masiva
* Casos de error
* Validaciones

---

# Limitaciones y Mejoras Futuras

## 1. Escalabilidad

Implementar:

```bash
Celery + Redis
```

Para mover consultas masivas a tareas en background.

---

## 2. Seguridad

Agregar:

```bash
Rotación de proxies
User agents dinámicos
Rate limiting
```

---

## 3. Caché

Posible integración:

```bash
Redis Cache
```

Evitar consultas repetidas en ventanas cortas.

---

## 4. Mejoras arquitectónicas futuras

```bash
Docker Compose
Alembic migrations
Observabilidad y logging estructurado
Procesamiento concurrente distribuido
```

---

# Ejecución Rápida

```bash
git clone <repo>
cd proyecto
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
uvicorn main:app --reload
```

Abrir:

```bash
http://127.0.0.1:8000/docs
```

---

# 👨‍💻 Autor

Proyecto desarrollado como solución técnica para prueba de **Analista N2**, enfocado en:

* Automatización sin RPA
* Integración de servicios
* Persistencia y trazabilidad
* Diseño modular
* Buenas prácticas de ingeniería


