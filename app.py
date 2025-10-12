from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

POWER_AUTOMATE_URL = "https://default4a187474b69b445f9d2db39f721fca.7f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/513438aec46b482e99c4f26ad207b02a/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=_1v0sPD-AVA9nzZujCt-z2QnTZcJ6Ph68bUShDToMAI"

@app.route("/asana-webhook", methods=["POST"])
def asana_webhook():
    # 🔹 Handshake do Asana (primeiro contato para validar o webhook)
    if "X-Hook-Secret" in request.headers:
        response = jsonify({"status": "ok"})
        response.headers["X-Hook-Secret"] = request.headers["X-Hook-Secret"]
        return response, 200

    # 🔹 Processa os eventos reais
    data = request.get_json(force=True, silent=True)

    if data and "events" in data:
        for event in data["events"]:
            # Filtra tarefas adicionadas a um projeto específico
            if event.get("action") == "added" and event.get("parent", {}).get("gid") == "1211142309362230":
                task_id = event["resource"]["gid"]      # ID da tarefa
                task_name = event["resource"].get("name", "Tarefa sem nome")

                payload = {
                    "taskId": task_id,
                    "taskName": task_name
                }

                try:
                    resp = requests.post(POWER_AUTOMATE_URL, json=payload, timeout=10)
                    print(f"✅ Enviado ao Power Automate: {payload} | Resposta: {resp.status_code}")
                except Exception as e:
                    print("❌ Erro ao enviar para o Power Automate:", e)

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)







