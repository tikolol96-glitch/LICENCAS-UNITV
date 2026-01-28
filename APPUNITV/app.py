from flask import Flask, Response, render_template
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

UPDATE_URL = (
    "http://s1ug.owue1ac.com/MarketServer/update"
    "?action=checkUpdate"
    "&packagenamesAndVersioncodes=com.integration.unitvsiptv%2C40210"
    "&language=pt"
    "&sn=BpulGtLFEZ8eSiMlMSFKXY%2FzOYqcsC9d"
    "&userId=516228738"
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/update")
def update():
    r = requests.get(UPDATE_URL, timeout=10)
    root = ET.fromstring(r.text)

    app_node = root.find(".//App")
    apk_url = app_node.findtext("url")

    return Response(apk_url, mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
