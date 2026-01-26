import requests
import time
import os
import json
import re
from datetime import datetime, timedelta

API_URL = "https://ftzxkevtyjipibozansl.supabase.co/functions/v1/api-config"
CONFIG_DIR = "configs"
STATE_FILE = "state.json"

os.makedirs(CONFIG_DIR, exist_ok=True)

def default_state():
    state = {
        "blocked_until": None,
        "last_message": "Inicializado"
    }
    save_state(state)
    return state
def load_state():
    if not os.path.exists(STATE_FILE):
        return default_state()
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return default_state()

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def is_blocked(state):
    if not state["blocked_until"]:
        return False
    return datetime.now() < datetime.fromisoformat(state["blocked_until"])

def auto_download_once():
    state = load_state()

    # Se ainda está bloqueado, não faz nada
    if is_blocked(state):
        return

    try:
        r = requests.post(API_URL, timeout=20)

        # API informou bloqueio
        if r.status_code == 429 or "Limite atingido" in r.text:
            msg = r.json().get("error", "Limite atingido")
            minutes = 60

            m = re.search(r"(\d+)", msg)
            if m:
                minutes = int(m.group(1))

            state["blocked_until"] = (
                datetime.now() + timedelta(minutes=minutes)
            ).isoformat()
            state["last_message"] = msg
            save_state(state)
            return

        r.raise_for_status()

        data = r.json()
        url = data["url"]
        filename = data["filename"]

        content = requests.get(url, timeout=20).text

        with open(os.path.join(CONFIG_DIR, filename), "w", encoding="utf-8") as f:
            f.write(content)

        state["last_message"] = f"Baixado: {filename}"
        save_state(state)

    except Exception as e:
        state["last_message"] = f"Erro: {str(e)}"
        save_state(state)
