from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import re

def limpiar_texto(texto: str) -> str:
    # Eliminar saltos de línea y espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

def extraer_valor_limpio(texto: str) -> str:
    # Quedarse solo con el primer valor monetario encontrado
    match = re.search(r'\$[\s\d\.]+', texto)
    if match:
        return match.group(0).strip()
    return texto.strip()

def consultar_simit(placa: str) -> dict:
    placa = placa.upper().strip()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print(f"Consultando SIMIT para placa: {placa}")
            page.goto("https://www.fcm.org.co/simit/#/estado-cuenta", timeout=30000)
            page.wait_for_timeout(4000)

            campo = page.get_by_placeholder("Número de identificación o placa del vehículo")
            campo.wait_for(timeout=10000)
            campo.fill(placa)
            page.wait_for_timeout(1000)
            campo.press("Enter")

            print("Esperando resultados...")
            page.wait_for_timeout(8000)

            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        multas = []
        vistos = set()  # Para evitar duplicados

        tabla = soup.find("table", {"id": "multaTable"})

        if tabla:
            filas = tabla.select("tr.page-row")
            for fila in filas:
                # Saltar filas ocultas
                estilo = fila.get("style", "")
                if "display: none" in estilo:
                    continue

                def get_celda(label):
                    td = fila.find("td", {"data-label": label})
                    return limpiar_texto(td.get_text()) if td else ""

                tipo       = get_celda("Tipo")
                secretaria = get_celda("Secretaría")
                infraccion = get_celda("Infracción")
                estado_raw = get_celda("Estado")
                valor_raw  = get_celda("Valor")
                vpagar_raw = get_celda("Valor a pagar")

                # Limpiar estado — quedarse solo con la primera palabra clave
                estado = "Pendiente" if "Pendiente" in estado_raw else \
                         "Pagado"    if "Pagado"    in estado_raw else \
                         estado_raw.split()[0] if estado_raw else ""

                # Limpiar tipo — quedarse solo con la primera línea
                tipo_limpio = tipo.split("Fecha")[0].strip()

                # Limpiar valores monetarios
                valor       = extraer_valor_limpio(valor_raw)
                valor_pagar = extraer_valor_limpio(vpagar_raw)

                # Evitar duplicados usando tipo+valor como clave
                clave = f"{tipo_limpio}_{valor}"
                if clave in vistos or not tipo_limpio:
                    continue
                vistos.add(clave)

                multas.append({
                    "tipo":        tipo_limpio,
                    "secretaria":  secretaria,
                    "infraccion":  infraccion,
                    "estado":      estado,
                    "valor":       valor,
                    "valorAPagar": valor_pagar,
                })

        print(f"Multas encontradas: {len(multas)}")

        return {
            "placa":          placa,
            "fechaConsulta":  datetime.utcnow().isoformat(),
            "estado":         "EXITOSO",
            "cantidadMultas": len(multas),
            "multas":         multas,
            "error":          None
        }

    except Exception as e:
        print(f"Error en scraper: {e}")
        return {
            "placa":          placa,
            "fechaConsulta":  datetime.utcnow().isoformat(),
            "estado":         "ERROR",
            "cantidadMultas": 0,
            "multas":         [],
            "error":          str(e)
        }