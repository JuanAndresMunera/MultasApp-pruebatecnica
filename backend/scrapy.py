import logging
from datetime import datetime, timezone          # ← agregado timezone
 
logger = logging.getLogger(__name__)
 
from playwright.sync_api import sync_playwright
 
 
def consultar_simit(placa: str) -> dict:
    placa = placa.upper().strip()
 
    try:
        logger.info(f"Consultando SIMIT para placa: {placa}")
        resultado_api = None
        api_recibida  = False
 
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-gpu",
                    "--disable-dev-shm-usage",
                    "--disable-extensions",
                    "--blink-settings=imagesEnabled=false",
                ]
            )
 
            context = browser.new_context()
 
            def bloquear_recursos(route):
                tipo = route.request.resource_type
                url  = route.request.url
                if tipo in ["image", "font", "media"]:
                    route.abort()
                elif any(dominio in url for dominio in [
                    "google-analytics", "googletagmanager", "facebook",
                    "doubleclick", "googlesyndication", "insuit.net"
                ]):
                    route.abort()
                else:
                    route.continue_()
 
            page = context.new_page()
            page.route("**/*", bloquear_recursos)
 
            def capturar_respuesta(response):
                nonlocal resultado_api, api_recibida
                if "estadocuenta/consulta" in response.url:
                    try:
                        resultado_api = response.json()
                        api_recibida  = True
                        logger.info(f"API interceptada: {len(resultado_api.get('multas', []))} multas")
                    except Exception as e:
                        logger.error(f"Error parseando respuesta: {e}")  # ← print → logger.error
                        api_recibida = True
 
            page.on("response", capturar_respuesta)
 
            page.goto(
                "https://www.fcm.org.co/simit/#/estado-cuenta",
                timeout=30000,
                wait_until="domcontentloaded"
            )
 
            campo = page.get_by_placeholder("Número de identificación o placa del vehículo")
            campo.wait_for(timeout=10000)
            campo.fill(placa)
            campo.press("Enter")
 
            logger.info("Esperando respuesta de SIMIT...")
 
            for _ in range(60):
                if api_recibida:
                    break
                page.wait_for_timeout(500)
 
            browser.close()
 
        if resultado_api is None:
            return {
                "placa":          placa,
                "fechaConsulta":  datetime.now(timezone.utc).isoformat(),  # ← utcnow → now(timezone.utc)
                "estado":         "ERROR",
                "cantidadMultas": 0,
                "multas":         [],
                "totalDeuda":     0,
                "error":          "No se recibió respuesta de la API de SIMIT"
            }
 
        multas_raw = resultado_api.get("multas", [])
        multas     = []
 
        for m in multas_raw:
            estado = m.get("estadoComparendo") or m.get("estadoCartera") or "Sin estado"
            numero = m.get("numeroComparendo") or m.get("numeroResolucion") or ""
            fecha  = m.get("fechaComparendo")  or m.get("fechaResolucion") or ""
 
            # Limpiar fecha — quitar la hora si viene incluida
            if fecha and " " in fecha:
                fecha = fecha.split(" ")[0]
 
            multas.append({
                "numero": numero,
                "valor":  m.get("valor", 0),
                "estado": estado,
                "fecha":  fecha,
            })
 
        total_deuda = resultado_api.get("totalGeneral", 0)
        paz_salvo   = resultado_api.get("pazSalvo", False)
 
        logger.info(f"Total multas: {len(multas)} | Deuda total: ${total_deuda:,}")
 
        return {
            "placa":          placa,
            "fechaConsulta":  datetime.now(timezone.utc).isoformat(),  # ← utcnow → now(timezone.utc)
            "estado":         "EXITOSO",
            "cantidadMultas": len(multas),
            "totalDeuda":     total_deuda,
            "pazSalvo":       paz_salvo,
            "multas":         multas,
            "error":          None
        }
 
    except Exception as e:
        logger.error(f"Error en scraper: {e}")
        return {
            "placa":          placa,
            "fechaConsulta":  datetime.now(timezone.utc).isoformat(),  # ← utcnow → now(timezone.utc)
            "estado":         "ERROR",
            "cantidadMultas": 0,
            "multas":         [],
            "totalDeuda":     0,
            "error":          str(e)
        }