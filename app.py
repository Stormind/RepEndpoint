from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

POWER_AUTOMATE_URL = "https://default4a187474b69b445f9d2db39f721fca.7f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/513438aec46b482e99c4f26ad207b02a/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=_1v0sPD-AVA9nzZujCt-z2QnTZcJ6Ph68bUShDToMAI"

TARGET_PROJECT_GID = "1211142309362230"  # ID do projeto que queremos monitorar

@app.route("/asana-webhook", methods=["POST"])
def asana_webhook():
    # Handshake do Asana
    if "X-Hook-Secret" in request.headers:
        response = jsonify({"status": "ok"})
        response.headers["X-Hook-Secret"] = request.headers["X-Hook-Secret"]
        return response, 200

    data = request.json
    print("📩 Webhook recebido:", data)

    if data and "events" in data:
        for event in data["events"]:
            # Evita erro se parent for None
            parent = event.get("parent")
            resource = event.get("resource", {})

            # Só queremos tarefas adicionadas ao projeto TARGET_PROJECT_GID
            if event.get("action") == "added" and parent and parent.get("gid") == TARGET_PROJECT_GID and resource.get("resource_type") == "task":
                task_id = resource.get("gid")
                task_name = resource.get("name", "Tarefa sem nome")

                payload = {"taskId": task_id, "taskName": task_name}

                try:
                    response = requests.post(POWER_AUTOMATE_URL, json=payload, timeout=10)
                    if response.status_code == 200:
                        print("✅ Enviado para Power Automate:", payload)
                    else:
                        print(f"❌ Falha ao enviar para Power Automate. Status: {response.status_code}, Conteúdo: {response.text}")
                except Exception as e:
                    print("❌ Erro ao enviar para Power Automate:", e)

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)










