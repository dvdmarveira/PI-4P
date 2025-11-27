from flask import Flask, request, jsonify, send_from_directory, redirect
import os
import socket
from flask_cors import CORS
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

app = Flask(__name__)
CORS(app)

# ========== CONFIGURAÇÃO DE PASTAS ==========
# Garante que o Render ache as pastas frontend e smartbus corretamente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Pasta /backend
PROJECT_ROOT = os.path.dirname(BASE_DIR)               # Pasta raiz do projeto
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')
SMARTBUS_DIR = os.path.join(PROJECT_ROOT, 'smartbus-dashboard')

# ========== CONEXÃO COM MONGO ATLAS ==========
user = quote_plus(os.getenv("MONGO_USER", ""))
password = quote_plus(os.getenv("MONGO_PASS", ""))

colecao_leituras = None

if user and password:
    try:
        MONGO_URI = f"mongodb+srv://{user}:{password}@receitas.2dwrpuz.mongodb.net/?retryWrites=true&w=majority"
        client = MongoClient(MONGO_URI)
        db = client["iot_database"]
        colecao_leituras = db["leituras_qualidade_ar"]
        print("✅ MongoDB Atlas conectado!")
    except Exception as e:
        print(f"❌ Erro na conexão Mongo: {e}")
        colecao_leituras = None
else:
    print("⚠️ MongoDB não configurado. Usando memória RAM.")

leituras_memoria = []
thresholds = {
    "temp_max": 28.0,
    "umid_min": 40.0,
    "ar_bom": 500,
    "ar_moderado": 1500
}

# ================= ROTAS DE ARQUIVOS (FRONTEND) =================

@app.route('/')
def root():
    return redirect('/smartbus')

@app.route('/dashboard')
def serve_dashboard():
    return send_from_directory(FRONTEND_DIR, 'dashboard.html')

@app.route('/dashboard/<path:filename>')
def serve_dashboard_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@app.route('/smartbus')
def serve_smartbus():
    return send_from_directory(SMARTBUS_DIR, 'index.html')

@app.route('/smartbus/<path:filename>')
def serve_smartbus_static(filename):
    return send_from_directory(SMARTBUS_DIR, filename)


# ================= ROTAS DA API =================

@app.route('/api/leituras', methods=['POST'])
def receber_leitura():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Nenhum dado enviado"}), 400
        
        dados["timestamp"] = datetime.now().isoformat()
        
        # CORREÇÃO CRÍTICA DO PYMONGO AQUI
        if colecao_leituras is not None:
            colecao_leituras.insert_one(dados)
        else:
            leituras_memoria.append(dados)
            if len(leituras_memoria) > 100:
                leituras_memoria.pop(0)
        
        print(f"✅ Leitura: Temp={dados.get('temperatura')} Umid={dados.get('umidade')}")
        
        return jsonify({"status": "sucesso", "mensagem": "Salvo"}), 201
    except Exception as e:
        print(f"❌ Erro POST: {e}")
        return jsonify({"erro": str(e)}), 400

@app.route('/api/leituras', methods=['GET'])
def obter_leituras():
    try:
        limite = request.args.get('limite', default=10, type=int)
        
        # CORREÇÃO CRÍTICA DO PYMONGO AQUI
        if colecao_leituras is not None:
            # Pega do banco real
            docs = list(colecao_leituras.find().sort("_id", -1).limit(limite))
            for doc in docs:
                doc["_id"] = str(doc["_id"])
            return jsonify({"total": len(docs), "leituras": docs})
        else:
            # Pega da memória RAM
            docs = leituras_memoria[-limite:] if leituras_memoria else []
            # Inverte para mostrar mais recente primeiro se necessário, 
            # mas na lista appendada o ultimo é o mais recente.
            return jsonify({"total": len(leituras_memoria), "leituras": list(reversed(docs))})
            
    except Exception as e:
        print(f"❌ Erro GET: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route('/api/thresholds', methods=['GET'])
def obter_thresholds():
    return jsonify(thresholds), 200

@app.route('/api/thresholds', methods=['PUT'])
def atualizar_thresholds():
    try:
        novos = request.get_json()
        if not novos: return jsonify({"erro": "Vazio"}), 400
        for k in thresholds:
            if k in novos: thresholds[k] = novos[k]
        return jsonify({"status": "ok", "thresholds": thresholds}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

if __name__ == '__main__':
    port = int(os.getenv("API_PORT", 5001))
    app.run(host='0.0.0.0', port=port)
