from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from database import Base

class Consulta(Base):
    __tablename__ = "consultas"

    id_consulta   = Column(Integer, primary_key=True, index=True)
    placa         = Column(String(10), nullable=False)
    fecha_consulta= Column(DateTime, default=datetime.utcnow)
    tipo_consulta = Column(String(20), nullable=False)  # individual / masiva
    estado        = Column(String(20), nullable=False)  # EXITOSO / ERROR
    respuesta_cruda = Column(Text, nullable=True)
    cantidad_multas = Column(Integer, default=0)
    mensaje_error = Column(Text, nullable=True)