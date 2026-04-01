from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# URLs e IDs
POWER_AUTOMATE_URL = "https://default4a187474b69b445f9d2db39f721fca.7f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/513438aec46b482e99c4f26ad207b02a/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=_1v0sPD-AVA9nzZujCt-z2QnTZcJ6Ph68bUShDToMAI"

TARGET_PROJECT_GID = "1211142309362230"  # projeto de destino
SOURCE_PROJECT_GIDS = [
    "1211494910632910",
    "1213819553879211"
]  # projeto de origem (onde as tarefas vêm)
ASANA_TOKEN = os.environ.get("ASANA_TOKEN")  # defina como variável de ambiente

@app.route("/asana-webhook", methods=["POST"])
def asana_webhook():
    # Handshake inicial do Asana
    if "X-Hook-Secret" in request.headers:
        response = jsonify({"status": "ok"})
        response.headers["X-Hook-Secret"] = request.headers["X-Hook-Secret"]
        return response, 200

    data = request.json
    print("📩 Webhook recebido:", data)

    if not data or "events" not in data:
        return jsonify({"status": "no events"}), 200

    for event in data["events"]:
        parent = event.get("parent")
        resource = event.get("resource", {})

        # Filtra somente tarefas adicionadas ao projeto de destino
        if (
            event.get("action") == "added"
            and parent
            and parent.get("gid") == TARGET_PROJECT_GID
            and resource.get("resource_type") == "task"
        ):
            task_id = resource.get("gid")

            # 🔍 Verifica se a tarefa também pertence ao projeto de origem
            try:
                headers = {"Authorization": f"Bearer {ASANA_TOKEN}"}
                resp = requests.get(f"https://app.asana.com/api/1.0/tasks/{task_id}/projects", headers=headers)
                resp.raise_for_status()
                projects = [p["gid"] for p in resp.json().get("data", [])]

                if any(proj in projects for proj in SOURCE_PROJECT_GIDS):
                    # ✅ É uma tarefa vinda do projeto de origem
                    projects = [p["gid"] for p in resp.json().get("data", [])]

                    if any(proj in projects for proj in SOURCE_PROJECT_GIDS):
                        payload = {
                            "events": [
                                        {
                                            "taskId": task_id,
                                            "taskName": resource.get("name", "Tarefa sem nome")
                                        }
                                      ]
                                  }

                        response = requests.post(POWER_AUTOMATE_URL, json=payload, timeout=10)

                    if response.status_code == 200:
                        print("✅ Enviado para Power Automate:", payload)
                    else:
                        print(f"❌ Falha ao enviar para Power Automate. Status: {response.status_code}, Conteúdo: {response.text}")
                else:
                    print(f"⚠️ Tarefa {task_id} não veio do projeto de origem. Ignorada.")

            except Exception as e:
                print("❌ Erro ao consultar projetos da tarefa:", e)

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)












