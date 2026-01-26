import time
from downloader import auto_download_once, load_state, save_state
from datetime import datetime
import requests
import re

API_URL = "https://ftzxkevtyjipibozansl.supabase.co/functions/v1/api-config"

print("▶ Worker automático iniciado")

CHECK_INTERVAL = 300  # 5 minutos

while True:
    state = load_state()

    # Se está bloqueado, revalida ocasionalmente
    if state["blocked_until"]:
        remaining = (
            datetime.fromisoformat(state["blocked_until"]) - datetime.now()
        ).total_seconds()

        if remaining > 0:
            try:
                r = requests.post(API_URL, timeout=15)

                if "Limite atingido" in r.text:
                    msg = r.json().get("error", "")
                    m = re.search(r"(\d+)", msg)
                    if m:
                        minutes = int(m.group(1))
                        state["blocked_until"] = (
                            datetime.now() + timedelta(minutes=minutes)
                        ).isoformat()
                        state["last_message"] = msg
                        save_state(state)
            except:
                pass

            time.sleep(CHECK_INTERVAL)
            continue

    # Se não está bloqueado, tenta baixar
    auto_download_once()
    time.sleep(30)
