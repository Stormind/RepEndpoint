from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/asana-webhook", methods=["POST", "GET"])
def asana_webhook():
    # Validação inicial do Asana
    if request.method == "GET":
        hook_secret = request.headers.get("X-Hook-Secret")
        if hook_secret:
            response = jsonify({"message": "Asana webhook validation"})
            response.headers["X-Hook-Secret"] = hook_secret
            return response, 200
        return "OK", 200

    # Recebe eventos reais
    if request.method == "POST":
        data = request.get_json()
        print("🔔 Webhook recebido:", data, flush=True)
        
        # Evita crash quando 'name' não existe
        try:
            for event in data.get("events", []):
                resource_gid = event["resource"]["gid"]
                resource_type = event["resource"]["resource_type"]
                print(f"Evento recebido: {resource_type} - {resource_gid}", flush=True)
        except Exception as e:
            print("Erro ao processar evento:", e, flush=True)

        return jsonify({"status": "ok"}), 200

@app.route("/")
def home():
    return "Webhook ativo 🚀", 200




