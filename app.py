from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# URL do Power Automate ou outro endpoint que deseja chamar
POWER_AUTOMATE_URL = "https://default4a187474b69b445f9d2db39f721fca.7f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/513438aec46b482e99c4f26ad207b02a/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=_1v0sPD-AVA9nzZujCt-z2QnTZcJ6Ph68bUShDToMAI"

@app.route("/asana-webhook", methods=["POST"])
def asana_webhook():
    # Handshake do Asana
    if "X-Hook-Secret" in request.headers:
        response = jsonify({"status": "ok"})
        response.headers["X-Hook-Secret"] = request.headers["X-Hook-Secret"]
        return response, 200

    data = request.json

    # Aqui você pode processar os eventos recebidos
    if data and "events" in data:
        for event in data["events"]:
            # Filtra apenas tarefas adicionadas ao projeto certo
            if event.get("action") == "added" and event.get("parent", {}).get("gid") == "1211142309362230":
                task_name = event["resource"]["name"]
                # Exemplo: envia para Power Automate
                requests.post(POWER_AUTOMATE_URL, json={"newFolderName": task_name})

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


    app.run(host="0.0.0.0", port=5000)
