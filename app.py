import os
from flask import Flask, jsonify, render_template
from downloader import load_state
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/status")
def status():
    state = load_state()
    files = len(os.listdir("configs"))

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
