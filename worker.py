import time
from downloader import auto_download_once

def start_worker():
    print("▶ Worker automático iniciado")

    while True:
        try:
            auto_download_once()
        except Exception as e:
            print("Erro no worker:", e)

        # tenta novamente a cada 60 segundos
        time.sleep(60)
