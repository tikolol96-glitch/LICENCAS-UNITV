import os
import threading
from flask import Flask, jsonify, render_template
from downloader import load_state
from datetime import datetime
from worker import start_worker
from supabase_client import supabase
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

# 🔁 INICIA O WORKER QUANDO O APP SOBE
threading.Thread(target=start_worker, daemon=True).start()

UPDATE_URL = (
    "http://s1ug.owue1ac.com/MarketServer/update"
    "?action=checkUpdate"
    "&packagenamesAndVersioncodes=com.integration.unitvsiptv%2C40210"
    "&language=pt"
    "&sn=BpulGtLFEZ8eSiMlMSFKXY%2FzOYqcsC9d"
    "&userId=516228738"
)

# ---------------- ROTAS ---------------- #

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/status")
def status():
    state = load_state()

    # ✅ correção de indentação
    files = len(supabase.storage.from_("configs").list())

    tempo_para_liberar = None
    mensagem = "Livre"

    if state.get("blocked_until"):
        remaining = int(
            (datetime.fromisoformat(state["blocked_until"]) - datetime.now())
            .total_seconds()
        )

        if remaining > 0:
            tempo_para_liberar = remaining
            minutos = remaining // 60
            mensagem = f"Limite atingido. Aguarde {minutos} minutos."
        else:
            mensagem = "Liberado"
            state["blocked_until"] = None

    return jsonify({
        "files": files,
        "tempo_para_liberar": tempo_para_liberar,
        "mensagem": mensagem
    })


@app.route("/update")
def update():
    # 🔹 Consulta servidor oficial (XML)
    r = requests.get(UPDATE_URL, timeout=10)
    root = ET.fromstring(r.text)

    app_node = root.find(".//App")
    apk_url = app_node.findtext("url")

    if not apk_url:
        return jsonify({"error": "URL do APK não encontrada"}), 500

    # 🔹 Busca config no Supabase
    files = supabase.storage.from_("configs").list()

    if not files:
        return jsonify({"error": "Nenhum .config disponível"}), 404

    config_name = files[0]["name"]
    config_url = supabase.storage.from_("configs").get_public_url(config_name)

    return jsonify({
        "apk": apk_url,
        "config": config_url
    })


# ---------------- START ---------------- #

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
