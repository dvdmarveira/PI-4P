import requests
import random
import time
import os
import socket
from dotenv import load_dotenv

load_dotenv()

# URL do seu backend Flask (ajuste o IP se necessário)
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", 5001)
URL_API = f"http://{API_HOST}:{API_PORT}/api/leituras"

cenarios = [
    {
        "status": "EXCELENTE",
        "temp_range": (21.0, 23.0),
        "umid_range": (50.0, 60.0),
        "ar_range": (200, 350),
        "co_range": (20, 50)
    },
    {
        "status": "BOA",
        "temp_range": (25.0, 27.0),
        "umid_range": (60.0, 70.0),
        "ar_range": (400, 550),
        "co_range": (50, 100)
    },
    {
        "status": "MODERADA",
        "temp_range": (29.0, 31.0),
        "umid_range": (65.0, 75.0),
        "ar_range": (600, 750),
        "co_range": (100, 200)
    },
    {
        "status": "RUIM",
        "temp_range": (31.0, 33.0),
        "umid_range": (75.0, 85.0),
        "ar_range": (800, 1000),
        "co_range": (200, 400)
    }
]

def gerar_dados_simulados(ciclo):
    cenario = cenarios[ciclo]
    return {
        "temperatura": round(random.uniform(*cenario["temp_range"]), 1),
        "umidade": round(random.uniform(*cenario["umid_range"]), 1),
        "qualidadeAr": random.randint(*cenario["ar_range"]),
        "nivelCO": random.randint(*cenario["co_range"]),
        "statusQualidade": cenario["status"],

        "led_ativo": True if cenario["status"] == "RUIM" else False,
        "faces_detectadas": random.randint(0, 2)
    }
    
def resolve_target_host(env_host):
    host = str(env_host or "localhost")
    if host == "0.0.0.0" or host.startswith("127.") or host == "localhost":
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            host = s.getsockname()[0]
            s.close()
        except Exception:
            host = "127.0.0.1"
    return host
    
API_HOST_ENV = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", "5001")
TARGET_HOST = resolve_target_host(API_HOST_ENV)
URL_API = f"http://{TARGET_HOST}:{API_PORT}/api/leituras"
print(f"[SIM] Enviando para: {URL_API}")
    
# Loop contínuo de simulação
if __name__ == "__main__":
    ciclo = 0
    while True:
        dados = gerar_dados_simulados(ciclo)
        print(f"📡 Enviando dados simulados: {dados}")

        try:
            resposta = requests.post(URL_API, json=dados, timeout=5)
            if resposta.status_code == 201:
                print(f"✅ Servidor respondeu: {resposta.status_code} - {resposta.json()}")
            else:
                print(f"⚠️ Servidor respondeu com erro: {resposta.status_code} - {resposta.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao enviar dados: {e}")

        # Alterna o cenário
        ciclo = (ciclo + 1) % 4
        time.sleep(5)

