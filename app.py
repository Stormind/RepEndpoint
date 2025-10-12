from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# URL do Power Automate
POWER_AUTOMATE_URL = "https://default4a187474b69b445f9d2db39f721fca.7f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/513438aec46b482e99c4f26ad207b02a/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=_1v0sPD-AVA9nzZujCt-z2QnTZcJ6Ph68bUShDToMAI"

# Token do Asana (adicione como variável de ambiente no Render)
ASANA_TOKEN = os.getenv("2/1208066562376675/1211268286808494:a77245df670b176f6da14811b6d792e6")

@app.route("/asana-webhook", methods=["POST", "GET"])
def asana_webhook():
    # ✅ Handshake inicial do Asana (primeira verificação do webhook)
    if "X-Hook-Secret" in request.headers:
        response = jsonify({"status": "ok"})
        response.headers["X-Hook-Secret"] = request.headers["X-Hook-Secret"]
        print("🤝 Handshake recebido e respondido com sucesso.")
        return response, 200

    # ✅ Leitura segura do corpo JSON
    data = request.get_json(silent=True)
    if not data:
        print("⚠️ Nenhum dado recebido no corpo da requisição.")
        return jsonify({"status": "no data"}), 200

    print("📩 Evento recebido:", data)

    # ✅ Processar eventos enviados pelo Asana
    for event in data.get("events", []):
        action = event.get("action")
        parent_gid = event.get("parent", {}).get("gid")
        resource = event.get("resource", {})
        resource_gid = resource.get("gid")
        resource_type = resource.get("resource_type")

        print(f"➡️ Ação: {action}, Tipo: {resource_type}, GID: {resource_gid}, Parent: {parent_gid}")

        # 🔒 Só continua se for um evento relevante
        if action == "added" and parent_gid == "1211142309362230" and resource_type == "task":
            task_name = None

            # ⚙️ Tenta buscar o nome da tarefa via API (pois 'name' pode não vir no webhook)
            if ASANA_TOKEN and resource_gid:
                try:
                    resp = requests.get(
                        f"https://app.asana.com/api/1.0/tasks/{resource_gid}",
                        headers={"Authorization": f"Bearer {ASANA_TOKEN}"},
                        timeout=10
                    )
                    if resp.status_code == 200:
                        task_data = resp.json().get("data", {})
                        task_name = task_data.get("name", "Sem nome")
                        print(f"📝 Nome da tarefa obtido via API: {task_name}")
                    else:
                        print(f"⚠️ Erro ao buscar tarefa {resource_gid}: {resp.status_code}")
                except Exception as e:
                    print("❌ Erro ao buscar detalhes da tarefa:", e)

            # Se mesmo assim não tiver nome, define um genérico
            if not task_name:
                task_name = resource.get("name", "Tarefa sem nome")

            # ✅ Envia para o Power Automate
            try:
                response = requests.post(
                    POWER_AUTOMATE_URL,
                    json={"newFolderName": task_name},
                    timeout=10
                )
                print(f"📤 Enviado para Power Automate: {task_name} | Status: {response.status_code}")
            except Exception as e:
                print("❌ Erro ao enviar para o Power Automate:", e)

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
