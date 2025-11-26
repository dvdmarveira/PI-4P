# 🌐 Projeto: Automação IoT com Sensores e Regras Híbridas

## 📖 Visão Geral


## ✨ Autores

**Grupo: Evellyn Silva, Deyvid Diogo, Stella Albertina, Marcos Victor, José Eduardo, Rafael Luiz e Isadora Francisca** 
**Disciplina:** IoT e Big Data

Este projeto implementa um sistema de automação e monitoramento IoT que utiliza um ESP-CAM para contagem de rostos e um sensor DHT22 para medir temperatura e umidade. Os dados são enviados para uma API em Flask e visualizados em um dashboard web.

### 🎯 Objetivo
Demonstrar a integração de um ESP-CAM com um backend em Flask e um frontend em tempo real, mostrando a contagem de rostos, temperatura e umidade.

---

##  fluxo do Sistema

1.  **ESP-CAM:**
    *   Conecta-se ao Wi-Fi.
    *   Lê a temperatura e umidade do sensor DHT22.
    *   Utiliza a câmera para detectar e contar rostos em um intervalo de 1 minuto.
    *   Envia os dados (temperatura, umidade e contagem de rostos) para a API a cada minuto.

2.  **Backend (API Flask):**
    *   Recebe os dados do ESP-CAM no endpoint `/api/leituras`.
    *   Armazena os dados em um banco de dados MongoDB.

3.  **Frontend (Dashboard):**
    *   Busca os dados da API a cada 3 segundos.
    *   Exibe a contagem de rostos, temperatura e umidade em tempo real.
    *   Mostra um histórico dos dados em um gráfico.

---

## 🔧 Componentes do Projeto

### 1. **Hardware (ESP-CAM)**
| Componente | Função | Pino |
|------------|--------|------|
| ESP-CAM | Processamento e câmera | - |
| DHT22 | Sensor de temperatura e umidade | GPIO 4 |

**Diagrama de Pinos (ESP-CAM e DHT22):**

```
+-----------------+      +---------+
| ESP-CAM         |      | DHT22   |
|                 |      |         |
|   5V            +------+ VCC     |
|   GND           +------+ GND     |
|   GPIO 4        +------+ DATA    |
|                 |      |         |
+-----------------+      +---------+
```

### 2. **Software Backend (API)**
- **Tecnologia:** Python 3.7+ com Flask
- **Porta:** 5000
- **Endpoints:**
    - `POST /api/leituras`: Recebe dados dos sensores e salva no banco
    - `GET /api/leituras`: Retorna últimas leituras do MongoDB

### 3. **Interface (Dashboard)**
- **Tecnologia:** HTML5 + JavaScript + Chart.js
- **Atualização:** Automática a cada 3 segundos
- **Features:** Visualização em tempo real, gráficos, contagem de rostos

---

## 📦 Instalação e Configuração

### **Pré-requisitos**

#### Hardware:
- [x] ESP-CAM
- [x] Sensor DHT22
- [x] Protoboard e jumpers
- [x] Cabo USB para programação

#### Software:
- [x] Arduino IDE 1.8+ ou PlatformIO
- [x] Python 3.7+
- [x] Navegador web moderno (Chrome, Firefox, Edge)

---

### **PASSO 1: Configurar o Ambiente**

```bash
./setup.sh
```

Este script irá:

*   Verificar se o Python 3 e o pip estão instalados.
*   Criar um ambiente virtual na pasta `backend`.
*   Instalar as dependências do Python.

### **Configuração de Variáveis de Ambiente**

Para que o backend e o frontend se comuniquem corretamente, é necessário configurar o IP da sua máquina e a porta da API.

#### Backend (`backend/.env`)

Crie um arquivo `.env` na pasta `backend` com o seguinte conteúdo:

```
API_HOST=SEU_IP_LOCAL
API_PORT=5001
```

*   **`SEU_IP_LOCAL`**: Substitua por o endereço IP da sua máquina na rede local (ex: `192.168.1.100`). Você pode obter seu IP local executando `ifconfig` (Linux/macOS) ou `ipconfig` (Windows) no terminal.
*   **`API_PORT`**: A porta em que a API Flask será executada. O padrão é `5001`.

#### Frontend (`frontend/config.js`)

O frontend também precisa saber o IP e a porta da API. Um arquivo `config.js` já foi criado na pasta `frontend`. Edite-o com o IP da sua máquina:

```javascript
const API_HOST = "SEU_IP_LOCAL"; // Substitua pelo IP da sua máquina
const API_PORT = 5001;
const API_URL = `http://${API_HOST}:${API_PORT}/api`;
```

*   **`SEU_IP_LOCAL`**: Substitua pelo mesmo endereço IP usado no `.env` do backend.
*   **`API_PORT`**: Mantenha `5001` ou a porta que você configurou no backend.

---

### **PASSO 2: Configurar o Backend (API)**

Após configurar as variáveis de ambiente no arquivo `backend/.env` (conforme descrito acima), o backend estará pronto para ser iniciado.

```bash
# 1. Clone ou baixe o projeto
cd backend

# 2. Crie um ambiente virtual (recomendado) - Já feito pelo setup.sh
# python -m venv venv

# Windows:
# venv\Scripts\activate

# 3. Instale as dependências - Já feito pelo setup.sh
# pip install -r requirements.txt

# 4. Execute a API (será feito pelo start_dev.sh)
# ./venv/bin/python api.py
```

### **PASSO 2: Configurar o ESP-CAM**

1.  Abra o arquivo `hardware/espcam_dht22_face_counter.ino` na Arduino IDE.
2.  **Instale as bibliotecas necessárias:**
    *   `DHT sensor library` (by Adafruit)
    *   `Adafruit Unified Sensor`
    *   `ArduinoJson` (versão 6.x)
3.  **Configure a placa:**
    *   Vá em **File → Preferences** e adicione a seguinte URL em "Additional Board Manager URLs":
        ```
        https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
        ```
    *   Vá em **Tools → Board → Boards Manager** e instale o **esp32**.
    *   Selecione a placa **AI Thinker ESP32-CAM** em **Tools → Board**.
4.  **Altere as seguintes variáveis no código:**
    ```cpp
    const char* ssid = "minhaRede";
    const char* password = "12345678";
    const char* api_url = "http://<SEU_IP_AQUI>:<PORTA_API>/api/leituras"; // <<-- Altere para o IP e Porta da sua API (definidos no .env)
    ```
5.  Conecte o ESP-CAM ao computador e faça o upload do código.

### **PASSO 3: Iniciar o Ambiente de Desenvolvimento**

Para facilitar os testes, utilize o script `start_dev.sh`:

```bash
./start_dev.sh
```

Este script irá:

*   Iniciar a API do backend (utilizando o `API_HOST` e `API_PORT` do `.env`).
*   Iniciar o simulador de sensores (utilizando o `API_HOST` e `API_PORT` do `.env`).
*   Abrir o dashboard no seu navegador padrão (que buscará a API usando o `API_HOST` e `API_PORT` do `config.js`).

---


## ✅ Checklist de Verificação

### **1. Verificar API (Backend)**

**Status:** A API está rodando corretamente?

| Teste | Como Verificar | Resultado Esperado |
|-------|----------------|-------------------|
| API Online | Acesse `http://localhost:5001` no navegador | JSON com `"status": "API IoT Online"` |
| Endpoint Leituras | `curl http://localhost:5001/api/leituras` | JSON com `"total": 0, "leituras": []` |
| Endpoint Thresholds | `curl http://localhost:5001/api/thresholds` | JSON com `temp_max`, `umid_min`, `luz_min` |

**Console da API deve mostrar:**
```
🚀 Iniciando API IoT...
📍 Acesse: http://localhost:5001
 * Running on http://0.0.0.0:5001
```

---

### **2. Verificar ESP32 (Hardware)**

**Status:** O ESP32 está conectado e enviando dados?

| Teste | Como Verificar | Resultado Esperado |
|-------|----------------|-------------------|
| WiFi Conectado | Serial Monitor (115200 baud) | `WiFi conectado! IP: 192.168.x.x` |
| Leituras DHT11 | Serial Monitor | `Temp: 25.0°C │ Umid: 60.0%` |
| Leituras LDR | Serial Monitor | `Luz: 1500` (valor entre 0-4095) |
| Envio para API | Serial Monitor | `✅ Resposta API: 201` |
| Busca Thresholds | Serial Monitor | `✅ Thresholds recebidos!` |

**Serial Monitor deve mostrar algo como:**
```
========== SISTEMA INICIADO ==========
Conectando ao WiFi...
WiFi conectado!
IP: 192.168.1.101

--- REGRA LOCAL ---
Temp: 24.5°C | Umid: 55.0% | Luz: 1200
Limites: Temp>28.0 | Umid<40.0 | Luz<300
🔴 LED: DESLIGADO

📤 Enviando para API...
✅ Resposta API: 201
```

**Console da API deve mostrar (quando ESP32 envia):**
```
✅ Leitura recebida: Temp=24.5°C, Umid=55.0%, Luz=1200
```

---

### **3. Verificar Dashboard (Frontend)**

**Status:** O dashboard está exibindo dados corretamente?

| Elemento | Como Verificar | Resultado Esperado |
|----------|----------------|-------------------|
| Cards de Leitura | Observe os valores | Números atualizando a cada 3s |
| Status Normal/Alerta | Provoque condições de alerta | Badge muda de "Normal" (verde) para "Alerta" (vermelho) |
| LED Indicator | Cubra o LDR ou esquente o DHT11 | Bolinha vermelha acende quando LED ativa |
| Gráfico | Aguarde 30 segundos | Linhas começam a aparecer no gráfico |
| Console do Navegador | F12 → Console | Sem erros vermelhos |

**Console do navegador deve mostrar (F12):**
```
✅ Dados atualizados com sucesso
```

---

## 🧪 Testes de Funcionalidade

### **Teste 1: Decisão Local (Edge Computing)**

**Objetivo:** Verificar que o ESP32 toma decisões mesmo sem API.

**Procedimento:**
1. **Desligue a API** (Ctrl+C no terminal)
2. Cubra o LDR com a mão (simular escuro)
3. Observe o LED físico

**✅ Resultado Esperado:**
- LED acende automaticamente (< 1 segundo)
- Serial Monitor mostra: `⚠️ Luminosidade BAIXA!` e `🔴 LED: LIGADO`
- Mensagem: `❌ WiFi desconectado. Dados não enviados.` (normal)

**❌ Se falhar:**
- Verifique fiação do LED (GPIO 5)
- Verifique valor de `luzMin` no código (padrão: 300)
- Teste manualmente: `digitalWrite(LED_PIN, HIGH);`

---

### **Teste 2: Integração com API (Cloud)**

**Objetivo:** Verificar envio e recebimento de dados.

**Procedimento:**
1. **API rodando** ✓
2. **ESP32 conectado ao WiFi** ✓
3. Aguarde 10 segundos
4. Acesse `http://localhost:5001/api/leituras` no navegador

**✅ Resultado Esperado:**
```json
{
  "total": 5,
  "leituras": [
    {
      "temperatura": 24.5,
      "umidade": 55.0,
      "luminosidade": 1200,
      "led_ativo": false,
      "timestamp": 1234567890
    },
    ...
  ]
}
```

**❌ Se falhar:**
- Verifique se o IP da API no código ESP32 está correto
- Ping o IP do PC: `ping 192.168.1.100`
- Verifique firewall (pode estar bloqueando porta 5000)

---

### **Teste 3: Ajuste Remoto de Thresholds**

**Objetivo:** Verificar que limites podem ser alterados remotamente.

**Procedimento:**
1. Abra o Dashboard
2. Altere "Temperatura Máxima" para `25.0`
3. Clique em "💾 Salvar Limites"
4. Esquente o DHT11 com a mão (ou aproxime de fonte de calor)
5. Aguarde 1 minuto (ESP32 busca thresholds a cada 60s)

**✅ Resultado Esperado:**
- Alert "✅ Limites atualizados com sucesso!"
- Serial Monitor mostra: `Novos limites: Temp=25.0`
- LED acende quando temperatura > 25°C

**❌ Se falhar:**
- Verifique console do navegador (F12)
- Teste manualmente: `curl -X PUT http://localhost:5001/api/thresholds -H "Content-Type: application/json" -d '{"temp_max":25.0}'`
- Verifique CORS na API (Flask-CORS instalado?)

---

### **Teste 4: Fail-Safe (Resiliência)**

**Objetivo:** Sistema continua funcionando mesmo sem internet.

**Procedimento:**
1. Sistema funcionando normalmente
2. **Desligue o roteador WiFi** (ou desconecte o PC da rede)
3. Cubra o LDR

**✅ Resultado Esperado:**
- LED continua acionando normalmente
- Serial Monitor mostra: `❌ WiFi desconectado. Usando thresholds locais.`
- Sistema funciona com valores padrão hardcoded

**❌ Se falhar:**
- Código não implementou fail-safe corretamente
- Verifique se `tempMax`, `umidMin`, `luzMin` estão definidos no início do código

---

## 🐛 Troubleshooting (Solução de Problemas)

### **Problema 1: ESP32 não conecta ao WiFi**

**Sintomas:**
```
Conectando ao WiFi...................
Falha na conexão WiFi. Usando modo offline.
```

**Soluções:**
- [ ] Verifique SSID e senha (case-sensitive!)
- [ ] ESP32 só funciona com WiFi 2.4GHz (não conecta em 5GHz)
- [ ] Verifique se WiFi tem autenticação WPA2 (não funciona com WEP)
- [ ] Rede corporativa pode bloquear ESP32
- [ ] Aumente timeout: `while (WiFi.status() != WL_CONNECTED && tentativas < 30)`

---

### **Problema 2: DHT11 retorna NaN ou -999**

**Sintomas:**
```
Erro ao ler DHT11!
Temp: nan°C | Umid: nan%
```

**Soluções:**
- [ ] Verifique fiação: VCC → 3.3V, GND → GND, DATA → GPIO 4
- [ ] Adicione resistor pull-up 10kΩ entre DATA e VCC
- [ ] DHT11 precisa de 2 segundos entre leituras: `delay(2000);`
- [ ] Sensor pode estar danificado (teste com outro)
- [ ] Verifique se `#define DHTPIN 4` corresponde ao pino físico

**Teste manual:**
```cpp
void loop() {
  float t = dht.readTemperature();
  Serial.println(t);
  delay(2000);
}
```

---

### **Problema 3: API retorna erro 404**

**Sintomas:**
```
❌ Erro no envio: http://192.168.1.100:5000/api/leituras not found
```

**Soluções:**
- [ ] Verifique se API está rodando: `curl http://localhost:5001`
- [ ] IP correto? Use `ipconfig` (Windows) ou `ifconfig` (Linux/Mac)
- [ ] Porta 5000 livre? Teste: `netstat -an | grep 5000`
- [ ] Firewall bloqueando? Adicione exceção para porta 5000
- [ ] URL no código está correta? `/api/leituras` (com `/api`)

---

### **Problema 4: Dashboard não atualiza**

**Sintomas:**
- Cards mostram `--`
- Console do navegador tem erros

**Soluções:**
- [ ] F12 → Console, verifique erros
- [ ] CORS bloqueado? Verifique se `flask-cors` está instalado
- [ ] IP da API correto no `dashboard.html`?
- [ ] API está retornando dados? Teste: `curl http://localhost:5001/api/leituras`
- [ ] Desabilite extensões de bloqueio (AdBlock, uBlock)

**Teste manual no console do navegador:**
```javascript
fetch('http://192.168.1.100:5001/api/leituras')
  .then(r => r.json())
  .then(d => console.log(d));
```

---

### **Problema 5: LED não acende**

**Sintomas:**
- Condições de alerta satisfeitas mas LED continua apagado
- Serial Monitor mostra `🔴 LED: LIGADO` mas fisicamente está apagado

**Soluções:**
- [ ] Verifique polaridade do LED (perna longa = ânodo/positivo)
- [ ] Resistor 220Ω presente?
- [ ] Teste manual: `digitalWrite(LED_PIN, HIGH); delay(1000); digitalWrite(LED_PIN, LOW);`
- [ ] GPIO 5 correto? Teste outro pino
- [ ] LED queimado? Teste com multímetro

---

## 📊 Monitoramento e Logs

### **Logs do ESP32 (Serial Monitor)**

**Configuração:** 115200 baud, NL & CR

**O que observar:**
```
✅ NORMAL:
- "WiFi conectado!"
- "✅ Resposta API: 201"
- "✅ Thresholds recebidos!"
- Valores de sensores atualizando

⚠️ ATENÇÃO:
- "❌ WiFi desconectado" (verificar rede)
- "Erro ao ler DHT11!" (verificar sensor)
- "❌ Erro no envio" (verificar API)
```

### **Logs da API (Terminal)**

**O que observar:**
```
✅ NORMAL:
- "✅ Leitura recebida: Temp=24.5°C..."
- "⚙️ Thresholds atualizados"
- Códigos HTTP 200, 201

❌ ERRO:
- "404 Not Found" (rota incorreta)
- "500 Internal Server Error" (bug no código)
- Exceções Python
```

### **Console do Dashboard (F12)**

**O que observar:**
```
✅ NORMAL:
- Sem erros vermelhos
- Requisições fetch com status 200

❌ ERRO:
- "CORS policy" (problema no backend)
- "Failed to fetch" (API offline ou IP errado)
- "Unexpected token" (resposta não é JSON válido)
```

---

## 📈 Métricas de Performance

### **Latências Esperadas:**

| Ação | Latência | Método |
|------|----------|--------|
| Leitura de sensor | ~100ms | Interno |
| Decisão local | < 50ms | Edge |
| Envio para API | 200-500ms | HTTP POST |
| Busca thresholds | 200-500ms | HTTP GET |
| Atualização dashboard | 3s | Polling |

### **Consumo de Recursos:**

| Componente | CPU | RAM | Rede |
|------------|-----|-----|------|
| ESP32 | ~5% | 40KB | ~1KB/s |
| API Flask | ~1% | 50MB | ~0.5KB/s |
| Dashboard | ~2% | 100MB | ~0.3KB/s |

---

## 📚 Estrutura de Arquivos

```
iot/
│
├── esp32_c3/
│   └── esp32_c3.ino          # Código ESP32 (Arduino)
│
├── backend/
│   ├── api.py                # API Flask (Python)
│   └── requirements.txt      # Dependências 
│
├── frontend/
│   ├── dashboard.html           # Dashboard Web
│   ├── styles.css          # Estilos
│   └── script.html         # Scripts
│   
│
├── hardware/
│   ├── esquema_circuito.png       # Diagrama de fiação
│   └── lista_componentes.txt      # BOM (Bill of Materials)
│
├── relatorio.md        # Relatório do Projeto
└── README.md           # Documentação do Projeto
```

---

## 🎓 Conceitos Importantes

### **Edge Computing (Computação de Borda)**
- Processamento ocorre no dispositivo (ESP32)
- Latência baixa (< 100ms)
- Funciona offline
- **Uso:** Decisões críticas, tempo real

### **Cloud Computing (Computação em Nuvem)**
- Processamento em servidor remoto
- Armazenamento centralizado
- Análise de dados históricos
- **Uso:** IA/ML, dashboards, controle remoto

### **Fail-Safe**
- Sistema continua funcionando em falhas
- Valores padrão locais se API offline
- Essencial para aplicações críticas

### **Threshold (Limite)**
- Valor de referência para tomada de decisão
- Exemplo: "temperatura > 28°C"
- Pode ser fixo (local) ou dinâmico (remoto)

---

**Dúvidas técnicas:**
- Consulte documentação oficial: [ESP32](https://docs.espressif.com/)
- Forum Arduino: https://forum.arduino.cc/
- Stack Overflow: Tag `esp32` ou `iot`

---



---
