from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔹 URL do Power Automate
POWER_AUTOMATE_URL = "https://default4a187474b69b445f9d2db39f721fca.7f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/513438aec46b482e99c4f26ad207b02a/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=_1v0sPD-AVA9nzZujCt-z2QnTZcJ6Ph68bUShDToMAI"

@app.route("/asana-webhook", methods=["POST"])
def asana_webhook():
    # 🔹 Etapa 1: handshake de verificação (Asana → Render)
    if "X-Hook-Secret" in request.headers:
        secret = request.headers["X-Hook-Secret"]
        response = jsonify({"status": "handshake ok"})
        response.headers["X-Hook-Secret"] = secret
        print(f"🤝 Handshake recebido e devolvido com sucesso: {secret}")
        return response, 200

    # 🔹 Etapa 2: eventos reais do Asana
    data = request.get_json(force=True, silent=True)
    print("📩 Evento recebido do Asana:", data)

    if data and "events" in data:
        for event in data["events"]:
            # Coleta informações básicas para debug
            resource_gid = event.get("resource", {}).get("gid")
            action = event.get("action")
            print(f"➡️ Evento: {action} no recurso {resource_gid}")

            # Só envia ao Power Automate se for uma tarefa adicionada
            if event.get("resource", {}).get("resource_type") == "task" and action == "added":
                try:
                    task_name = event.get("resource", {}).get("name", "Tarefa sem nome")
                    payload = {"newFolderName": task_name}
                    r = requests.post(POWER_AUTOMATE_URL, json=payload, timeout=10)
                    print(f"✅ Enviado ao Power Automate: {r.status_code}")
                except Exception as e:
                    print("❌ Erro ao enviar para Power Automate:", e)

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)






