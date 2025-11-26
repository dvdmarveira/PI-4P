from flask import Flask, request, jsonify, send_from_directory, redirect
import os
import json
import socket
from flask_cors import CORS
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

app = Flask(__name__)
CORS(app)

# ========== CONFIGURAÇÃO CORRETA DOS PATHS ==========
# O api.py está em /backend, então precisamos voltar um nível para acessar /frontend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Isso aponta para /backend
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # Isso volta para /BigData-PI-main
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend') # Dashboard admin
SMARTBUS_DIR = os.path.join(PROJECT_ROOT, 'smartbus-dashboard') # Smartbus UI

print(f"📍 BASE_DIR: {BASE_DIR}")
print(f"📍 PROJECT_ROOT: {PROJECT_ROOT}")
print(f"📍 FRONTEND_DIR: {FRONTEND_DIR}")
print(f"📍 SMARTBUS_DIR: {SMARTBUS_DIR}")
print(f"📍 IoT Dashboard existe: {os.path.exists(os.path.join(FRONTEND_DIR, 'dashboard.html'))}")
print(f"📍 Smartbus existe: {os.path.exists(os.path.join(SMARTBUS_DIR, 'index.html'))}")

# ========== CONEXÃO COM MONGO ATLAS ==========
user = quote_plus(os.getenv("MONGO_USER", ""))
password = quote_plus(os.getenv("MONGO_PASS", ""))

colecao_leituras = None
if user and password:
    MONGO_URI = f"mongodb+srv://{user}:{password}@receitas.2dwrpuz.mongodb.net/"
    client = MongoClient(MONGO_URI)
    db = client["iot_database"]
    colecao_leituras = db["leituras_qualidade_ar"]
    print("✅ MongoDB Atlas conectado!")
else:
    print("⚠️  MongoDB não configurado. Usando modo em memória.")
    colecao_leituras = None

leituras_memoria = []
thresholds = {
    "temp_max": 28.0,
    "umid_min": 40.0,
    "ar_bom": 500,
    "ar_moderado": 1500
}

# ================= ROTAS =================

@app.route('/')
def root():
    return redirect('/smartbus')

# Rota para servir o dashboard
@app.route('/dashboard')
def serve_dashboard():
    try:
        return send_from_directory(FRONTEND_DIR, 'dashboard.html')
    except Exception as e:
        print(f"❌ Erro ao servir dashboard: {e}")
        return f"Erro: {e}", 404

# Rota para servir arquivos estáticos (CSS, JS, config.js)
@app.route('/dashboard/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory(FRONTEND_DIR, filename)
    except Exception as e:
        print(f"❌ Erro ao servir {filename}: {e}")
        return f"Arquivo não encontrado: {filename}", 404

# Rota para servir o Smartbus
@app.route('/smartbus')
def serve_smartbus():
    try:
        return send_from_directory(SMARTBUS_DIR, 'index.html')
    except Exception as e:
        return f"Erro ao servir smartbus: {e}", 500

# Rota para servir arquivos estáticos do smartbus (css/js/assets)
@app.route('/smartbus/<path:filename>')
def smartbus_static(filename):
    try:
        return send_from_directory(SMARTBUS_DIR, filename)
    except Exception as e:
        return f"Erro estático smartbus: {e}", 404

# ========== ROTAS API (mantenha as suas existentes) ==========
def salvar_leitura(leitura):
    if colecao_leituras:
        colecao_leituras.insert_one(leitura)
    else:
        leituras_memoria.append(leitura)

@app.route('/api/leituras', methods=['POST'])
def receber_leitura():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Nenhum dado enviado"}), 400
        
        dados["timestamp"] = datetime.now().isoformat()
        
        if colecao_leituras:
            colecao_leituras.insert_one(dados)
        
        leituras_memoria.append(dados)
        if len(leituras_memoria) > 100:
            leituras_memoria.pop(0)
        
        print(f"✅ Leitura recebida: Temp={dados.get('temperatura')}°C, "
              f"Umid={dados.get('umidade')}%, "
              f"Qualidade Ar={dados.get('qualidadeAr')}")
        
        return jsonify({
            "status": "sucesso",
            "mensagem": "Leitura salva com sucesso"
        }), 201
    except Exception as e:
        print(f"❌ Erro: {e}")
        return jsonify({"erro": str(e)}), 400

@app.route('/api/leituras', methods=['GET'])
def obter_leituras():
    try:
        limite = request.args.get('limite', default=10, type=int)
        
        if colecao_leituras:
            docs = list(colecao_leituras.find().sort("_id", -1).limit(limite))
            for doc in docs:
                doc["_id"] = str(doc["_id"])
        else:
            docs = leituras_memoria[-limite:]
            docs.reverse()
        
        return jsonify({
            "total": len(docs),
            "leituras": docs
        })
    except Exception as e:
        print(f"❌ Erro ao buscar leituras: {e}")
        return jsonify({
            "total": len(leituras_memoria),
            "leituras": leituras_memoria[-limite:] if leituras_memoria else []
        })

@app.route('/api/thresholds', methods=['GET'])
def obter_thresholds():
    return jsonify(thresholds), 200

@app.route('/api/thresholds', methods=['PUT'])
def atualizar_thresholds():
    try:
        novos_limites = request.get_json()
        if not novos_limites:
            return jsonify({"erro": "Nenhum dado enviado"}), 400

        for chave in thresholds:
            if chave in novos_limites:
                thresholds[chave] = novos_limites[chave]

        print(f"⚙️ Thresholds atualizados: {thresholds}")
        return jsonify({
            "status": "sucesso",
            "mensagem": "Thresholds atualizados",
            "thresholds": thresholds
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

@app.route('/api/estatisticas', methods=['GET'])
def obter_estatisticas():
    try:
        if not leituras_memoria:
            return jsonify({"mensagem": "Nenhuma leitura disponível"}), 200
        
        total = len(leituras_memoria)
        temp_media = sum(l.get('temperatura', 0) for l in leituras_memoria) / total
        umid_media = sum(l.get('umidade', 0) for l in leituras_memoria) / total
        ar_media = sum(l.get('qualidadeAr', 0) for l in leituras_memoria) / total
        
        status_count = {}
        for l in leituras_memoria:
            status = l.get('statusQualidade', 'DESCONHECIDO')
            status_count[status] = status_count.get(status, 0) + 1
        
        return jsonify({
            "total_leituras": total,
            "medias": {
                "temperatura": round(temp_media, 1),
                "umidade": round(umid_media, 1),
                "qualidadeAr": round(ar_media, 0)
            },
            "distribuicao_status": status_count
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# ================= EXECUÇÃO =================
if __name__ == '__main__':
    # Ler host/port do .env (fallback para 0.0.0.0:5001)
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 5001))

    try:
        lan_ip = socket.gethostbyname(socket.gethostname())
        if lan_ip.startswith("127.") or lan_ip == "0.0.0.0":
            # tenta alternativa
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            lan_ip = s.getsockname()[0]
            s.close()
    except Exception:
        lan_ip = "localhost"

    print("\n" + "="*50)
    print("🚀 MONITOR DE QUALIDADE DO AR - API")
    print("="*50)
    print(f"📍 Acesse Smartbus: http://{lan_ip}:{port}/smartbus")
    print(f"📊 Dashboard: http://{lan_ip}:{port}/dashboard")
    print(f"📍 (Live Server) Smartbus local: http://127.0.0.1:5500/smartbus-dashboard/index.html")
    print("="*50 + "\n")

    app.run(host=host, port=port, debug=True)