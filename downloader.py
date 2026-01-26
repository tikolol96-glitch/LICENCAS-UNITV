import requests
import os
import json
import re
from datetime import datetime, timedelta

API_URL = "https://ftzxkevtyjipibozansl.supabase.co/functions/v1/api-config"
CONFIG_DIR = "configs"
STATE_FILE = "state.json"

os.makedirs(CONFIG_DIR, exist_ok=True)


def default_state():
    return {
        "blocked_until": None,
        "last_message": "Inicializado"
    }


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
    try:
        if not state.get("blocked_until"):
            return False
        return datetime.now() < datetime.fromisoformat(state["blocked_until"])
    except:
        state["blocked_until"] = None
        save_state(state)
        return False


def auto_download_once():
    state = load_state()

    # ⛔ ainda bloqueado
    if is_blocked(state):
        return

    try:
        r = requests.post(API_URL, timeout=20)

        # 🚫 limite atingido
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
