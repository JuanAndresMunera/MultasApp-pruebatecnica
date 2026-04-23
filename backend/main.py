from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import List
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import logging

from database import engine, get_db, Base, SessionLocal  # ← añadimos SessionLocal
from models import Consulta
from scrapy import consultar_simit

Base.metadata.create_all(bind=engine)

# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(title="API Consulta Multas SIMIT", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Utilidad compartida ──────────────────────────────────────────────────────

REGEX_PLACA = re.compile(r"^[A-Z]{3}\d{3}$")

def es_placa_valida(placa: str) -> bool:
    return bool(REGEX_PLACA.match(placa))

# ─── Modelos ──────────────────────────────────────────────────────────────────

class ConsultaIndividualRequest(BaseModel):
    placa: str

    @validator("placa")
    def validar_placa(cls, v):
        v = v.upper().strip()
        if not es_placa_valida(v):
            raise ValueError("Formato de placa inválido. Ejemplo válido: ABC123")
        return v

class ConsultaMasivaRequest(BaseModel):
    placas: List[str]

    @validator("placas")
    def validar_placas(cls, v):
        if len(v) == 0:
            raise ValueError("Debe enviar al menos una placa")
        if len(v) > 50:
            raise ValueError("Máximo 50 placas por consulta masiva")
        return v

# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/")
def raiz():
    return {"mensaje": "API Consulta Multas SIMIT activa", "version": "1.0.0"}


@app.post("/consulta-individual")
def consulta_individual(
    request: ConsultaIndividualRequest,
    db: Session = Depends(get_db)
):
    placa = request.placa
    resultado = consultar_simit(placa)

    logger.info(
        f"Consulta individual — placa={placa} "
        f"estado={resultado['estado']} multas={resultado['cantidadMultas']}"
    )

    registro = Consulta(
        placa=placa,
        fecha_consulta=datetime.now(timezone.utc),
        tipo_consulta="individual",
        estado=resultado["estado"],
        respuesta_cruda=json.dumps(resultado, ensure_ascii=False),
        cantidad_multas=resultado["cantidadMultas"],
        mensaje_error=resultado.get("error")
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)

    return resultado


@app.post("/consulta-masiva")
def consulta_masiva(
    request: ConsultaMasivaRequest,
    db: Session = Depends(get_db)
):
    def procesar_placa(placa_raw: str) -> dict:
        """
        Cada hilo crea su propia sesión de BD — SessionLocal no es thread-safe
        cuando se comparte entre hilos.
        """
        placa = placa_raw.upper().strip()

        if not es_placa_valida(placa):              # ← función central
            resultado = {
                "placa": placa,
                "fechaConsulta": datetime.now(timezone.utc).isoformat(),
                "estado": "ERROR",
                "cantidadMultas": 0,
                "multas": [],
                "totalDeuda": 0,
                "error": "Formato de placa inválido"
            }
        else:
            resultado = consultar_simit(placa)

        # ── Cada hilo usa su propia sesión ────────────────────────────────────
        hilo_db = SessionLocal()
        try:
            registro = Consulta(
                placa=resultado["placa"],
                fecha_consulta=datetime.now(timezone.utc),  # ← timezone.utc
                tipo_consulta="masiva",
                estado=resultado["estado"],
                respuesta_cruda=json.dumps(resultado, ensure_ascii=False),
                cantidad_multas=resultado["cantidadMultas"],
                mensaje_error=resultado.get("error")
            )
            hilo_db.add(registro)
            hilo_db.commit()
            logger.info(
                f"Consulta masiva — placa={resultado['placa']} "
                f"estado={resultado['estado']} multas={resultado['cantidadMultas']}"
            )
        except Exception as e:
            hilo_db.rollback()
            logger.error(f"Error guardando en BD para {placa}: {e}")
        finally:
            hilo_db.close()         # ← siempre se cierra, con o sin error

        return resultado

    # ── Ejecutar en paralelo, máximo 3 workers ────────────────────────────────
    resultados_map = {}

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(procesar_placa, placa): placa
            for placa in request.placas
        }
        for future in as_completed(futures):
            placa_original = futures[future]
            try:
                resultado = future.result()
            except Exception as e:
                logger.error(f"Error no controlado — placa={placa_original}: {e}")
                resultado = {
                    "placa": placa_original.upper().strip(),
                    "fechaConsulta": datetime.now(timezone.utc).isoformat(),
                    "estado": "ERROR",
                    "cantidadMultas": 0,
                    "multas": [],
                    "totalDeuda": 0,
                    "error": str(e)
                }
            resultados_map[placa_original] = resultado

    # Preservar el orden original de las placas
    resultados = [resultados_map[p] for p in request.placas]
    return {"total": len(resultados), "resultados": resultados}


@app.get("/historico")
def historico(db: Session = Depends(get_db)):
    registros = (
        db.query(Consulta)
        .order_by(Consulta.fecha_consulta.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": r.id_consulta,
            "placa": r.placa,
            "fechaConsulta": r.fecha_consulta.isoformat(),
            "tipoConsulta": r.tipo_consulta,
            "estado": r.estado,
            "cantidadMultas": r.cantidad_multas,
            "mensajeError": r.mensaje_error
        }
        for r in registros
    ]