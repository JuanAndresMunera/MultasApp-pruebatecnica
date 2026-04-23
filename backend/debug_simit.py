from playwright.sync_api import sync_playwright

def debug():
    logs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page    = context.new_page()

        def log_request(request):
            if "fcm.org.co" in request.url:
                logs.append(f"REQUEST:  {request.method} {request.url}")

        def log_response(response):
            if "fcm.org.co" in response.url:
                logs.append(f"RESPONSE: {response.status} {response.url}")

        page.on("request",  log_request)
        page.on("response", log_response)

        logs.append("Abriendo SIMIT...")
        page.goto("https://www.fcm.org.co/simit/#/estado-cuenta", timeout=30000)
        page.wait_for_timeout(3000)

        campo = page.get_by_placeholder("Número de identificación o placa del vehículo")
        campo.wait_for(timeout=10000)
        campo.fill("ABC123")
        page.wait_for_timeout(500)
        campo.press("Enter")

        logs.append("Esperando respuesta...")
        page.wait_for_timeout(10000)

        browser.close()

    # Guardar logs en archivo
    with open("debug_logs.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(logs))

    print("Logs guardados en debug_logs.txt")

debug()