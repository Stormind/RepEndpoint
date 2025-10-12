from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# URL do Power Automate
POWER_AUTOMATE_URL = "https://default4a187474b69b445f9d2db39f721fca.7f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/513438aec46b482e99c4f26ad207b02a/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=_1v0sPD-AVA9nzZujCt-z2QnTZcJ6Ph68bUShDToMAI"

@app.route("/asana-webhook", methods=["POST"])
def asana_webhook():
    # Handshake do Asana
    if "X-Hook-Secret" in request.headers:
        print("🔑 Handshake recebido do Asana")
        return "", 200, {"X-Hook-Secret": request.headers["X-Hook-Secret"]}

    data = request.get_json(force=True)
    print("📩 Webhook recebido:", data)

    events = []
    task_id = data.get("taskId")
    task_name = data.get("taskName", "Tarefa sem nome")

    if task_id:
        events.append({
            "taskId": task_id,
            "taskName": task_name
        })
        # Tenta enviar para o Power Automate
        try:
            resp = requests.post(POWER_AUTOMATE_URL, json={"events": events}, timeout=10)
            if resp.status_code == 200:
                print(f"✅ Enviado para o Power Automate com sucesso! Task ID: {task_id}")
            else:
                print(f"❌ Falha ao enviar para o Power Automate! Status: {resp.status_code}, Conteúdo: {resp.text}")
        except Exception as e:
            print("❌ Erro ao enviar para o Power Automate:", e)
    else:
        print("⚠️ Nenhum taskId encontrado no webhook")

    # Retorna JSON compatível
    return jsonify({"events": events}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)







