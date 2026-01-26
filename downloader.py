import requests
import json
import re
from datetime import datetime, timedelta
from supabase_client import supabase

API_URL = "https://ftzxkevtyjipibozansl.supabase.co/functions/v1/api-config"
STATE_FILE = "state.json"

def default_state():
    state = {
        "blocked_until": None,
        "last_message": "Inicializado"
    }
    save_state(state)
    return state

def load_state():
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

    if is_blocked(state):
        return

    r = requests.post(API_URL, timeout=20)

    if r.status_code == 429 or "Limite atingido" in r.text:
        msg = r.json().get("error", "Limite atingido")
        m = re.search(r"(\d+)", msg)
        minutes = int(m.group(1)) if m else 60

        state["blocked_until"] = (
            datetime.now() + timedelta(minutes=minutes)
        ).isoformat()

        state["last_message"] = msg
        save_state(state)
        return

    data = r.json()
    url = data["url"]
    filename = data["filename"]

    content = requests.get(url, timeout=20).text

    # 🔑 nome único
    filename = f"{int(datetime.now().timestamp())}_{filename}"

    # ☁️ upload no Supabase
    supabase.storage.from_("configs").upload(
        filename,
        content.encode("utf-8"),
        {"content-type": "text/plain"}
    )

    state["last_message"] = f"Baixado: {filename}"
    save_state(state)
