from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

POWER_AUTOMATE_URL = "https://default4a187474b69b445f9d2db39f721fca.7f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/513438aec46b482e99c4f26ad207b02a/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=_1v0sPD-AVA9nzZujCt-z2QnTZcJ6Ph68bUShDToMAI"

ASANA_TOKEN = os.environ.get("ASANA_TOKEN")  # Token configurado no Render

@app.route("/asana-webhook", methods=["POST"])
def asana_webhook():
    # 1️⃣ Handshake inicial
    if "X-Hook-Secret" in request.headers:
        response = jsonify({"status": "ok"})
        response.headers["X-Hook-Secret"] = request.headers["X-Hook-Secret"]
        print("🤝 Handshake recebido do Asana.")
        return response, 200

    # 2️⃣ Processamento normal
    try:
        data = request.get_json(force=True)
    except Exception as e:
        print("❌ Erro ao ler JSON:", e)
        return jsonify({"error": "invalid_json"}), 400

    print("📩 Evento recebido do Asana:", data)

    if data and "events" in data:
        for event in data["events"]:
            try:
                # Verifica se é adição de tarefa no projeto alvo
                if event.get("action") == "added" and event.get("parent", {}).get("gid") == "1211142309362230":
                    resource_gid = event.get("resource", {}).get("gid")
                    task_name = event.get("resource", {}).get("name", None)

                    # Se não veio o nome, busca via API
                    if not task_name and ASANA_TOKEN and resource_gid:
                        asana_url = f"https://app.asana.com/api/1.0/tasks/{resource_gid}"
                        headers = {"Authorization": f"Bearer {ASANA_TOKEN}"}
                        resp = requests.get(asana_url, headers=headers, timeout=10)
                        if resp.status_code == 200:
                            task_name = resp.json()["data"].get("name")

                    if not task_name:
                        print("⚠️ Nenhum nome de tarefa encontrado, evento ignorado.")
                        continue

                    # Envia ao Power Automate
                    print(f"📤 Enviando tarefa '{task_name}' ao Power Automate...")
                    resp = requests.post(POWER_AUTOMATE_URL, json={"newFolderName": task_name}, timeout=10)
                    print(f"✅ Power Automate respondeu {resp.status_code}")

            except Exception as e:
                print("❌ Erro ao processar evento individual:", e)

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


