from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

POWER_AUTOMATE_URL = "https://default4a187474b69b445f9d2db39f721fca.7f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/513438aec46b482e99c4f26ad207b02a/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=_1v0sPD-AVA9nzZujCt-z2QnTZcJ6Ph68bUShDToMAI"

PROJETO_ALVO = "1211142309362230"

@app.route("/asana-webhook", methods=["POST"])
def asana_webhook():
    # Handshake do Asana
    if "X-Hook-Secret" in request.headers:
        print("🔑 Handshake recebido do Asana")
        return "", 200, {"X-Hook-Secret": request.headers["X-Hook-Secret"]}

    data = request.get_json(force=True)
    print("📩 Webhook recebido:", data)

    events_para_automate = []

    for event in data.get("events", []):
        # Pega ID da tarefa dependendo do evento
        task_id = None
        task_name = "Tarefa sem nome"

        resource = event.get("resource", {})
        if resource.get("resource_type") == "task":
            task_id = resource.get("gid")
            task_name = resource.get("name", "Tarefa sem nome")

        parent = event.get("parent")
        parent_gid = parent.get("gid") if parent else None

        # Filtra apenas tarefas adicionadas ao projeto alvo
        if task_id and parent_gid == PROJETO_ALVO:
            events_para_automate.append({
                "taskId": task_id,
                "taskName": task_name
            })
            # Envia para Power Automate
            try:
                resp = requests.post(POWER_AUTOMATE_URL, json={"events": events_para_automate}, timeout=10)
                if resp.status_code == 200:
                    print(f"✅ Enviado para Power Automate! Task ID: {task_id}")
                else:
                    print(f"❌ Falha ao enviar para Power Automate. Status: {resp.status_code}, Conteúdo: {resp.text}")
            except Exception as e:
                print("❌ Erro ao enviar para Power Automate:", e)

    return jsonify({"events": events_para_automate}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)









