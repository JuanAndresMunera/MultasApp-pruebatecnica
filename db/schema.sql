-- Script de creación de tabla para histórico de consultas SIMIT
CREATE TABLE IF NOT EXISTS consultas (
    id_consulta SERIAL PRIMARY KEY,
    placa VARCHAR(10) NOT NULL,
    fecha_consulta TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tipo_consulta VARCHAR(20) NOT NULL, -- 'individual' o 'masiva'
    estado VARCHAR(20) NOT NULL,        -- 'EXITOSO' o 'ERROR'
    respuesta_cruda TEXT,               -- JSON completo de la fuente externa
    cantidad_multas INTEGER DEFAULT 0,
    mensaje_error TEXT                  -- Detalle en caso de falla controlada
);

-- Índice para optimizar la consulta del histórico por placa
CREATE INDEX IF NOT EXISTS idx_consultas_placa ON consultas(placa);