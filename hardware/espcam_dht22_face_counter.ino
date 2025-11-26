
// ========== BIBLIOTECAS ==========
#include "WiFi.h"
#include "esp_camera.h"
#include "Arduino.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "driver/rtc_io.h"
#include <String.h>
#include <ArduinoJson.h>
#include "esp_http_client.h"
#include "DHT.h"

// ========== CONFIGURAÇÕES DE HARDWARE ==========
// Pinos da câmera (AI-Thinker ESP32-CAM)
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// Pino do sensor DHT22
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// ========== CONFIGURAÇÕES DE REDE E API ==========
const char* ssid = "minhaRede";
const char* password = "12345678";
const char* api_url = "http://192.168.1.103:5001/api/leituras"; // <<-- Altere para o IP do seu computador

// ========== VARIÁVEIS GLOBAIS ==========
unsigned long tempoAnterior = 0;
const unsigned long intervaloContagem = 60000; // 1 minuto (editável)
int contagemRostos = 0;

// ========== FUNÇÕES AUXILIARES ==========
void configurarCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  // Inicializa a câmera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Falha ao inicializar a câmera: 0x%x", err);
    return;
  }
}

void conectarWiFi() {
  Serial.print("Conectando ao WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("
WiFi conectado!");
  Serial.print("Endereço IP: ");
  Serial.println(WiFi.localIP());
}

void enviarDados(float temperatura, float umidade, int rostos) {
  if (WiFi.status() == WL_CONNECTED) {
    StaticJsonDocument<200> doc;
    doc["temperatura"] = temperatura;
    doc["umidade"] = umidade;
    doc["faces_detectadas"] = rostos;

    String json;
    serializeJson(doc, json);

    esp_http_client_config_t config = {
      .url = api_url,
      .method = HTTP_METHOD_POST,
      .timeout_ms = 5000,
      .is_async = false,
    };
    esp_http_client_handle_t client = esp_http_client_init(&config);
    esp_http_client_set_header(client, "Content-Type", "application/json");
    esp_http_client_set_post_field(client, json.c_str(), json.length());

    esp_err_t err = esp_http_client_perform(client);
    if (err == ESP_OK) {
      Serial.printf("Status da resposta HTTP: %d
", esp_http_client_get_status_code(client));
    } else {
      Serial.printf("Falha na requisição HTTP: %s
", esp_err_to_name(err));
    }
    esp_http_client_cleanup(client);
  } else {
    Serial.println("WiFi desconectado. Não foi possível enviar os dados.");
  }
}

// ========== SETUP ==========
void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  configurarCamera();
  dht.begin();
  conectarWiFi();

  // Desativa o brownout detector
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
}

// ========== LOOP ==========
void loop() {
  unsigned long tempoAtual = millis();

  // Detecta rostos
  camera_fb_t *fb = esp_camera_fb_get();
  if (fb) {
    // Lógica de detecção de rosto (simplificada)
    // Para uma detecção real, você precisaria de uma biblioteca de visão computacional
    // Aqui, vamos simular a detecção de um rosto a cada 5 segundos
    if (tempoAtual % 5000 < 100) { // Simula detecção
        contagemRostos++;
        Serial.printf("Rosto detectado! Contagem atual: %d
", contagemRostos);
    }
    esp_camera_fb_return(fb);
  }

  // Verifica se o intervalo de 1 minuto foi atingido
  if (tempoAtual - tempoAnterior >= intervaloContagem) {
    tempoAnterior = tempoAtual;

    // Lê os sensores
    float umidade = dht.readHumidity();
    float temperatura = dht.readTemperature();

    if (isnan(umidade) || isnan(temperatura)) {
      Serial.println("Falha ao ler do sensor DHT!");
    } else {
      Serial.printf("Temperatura: %.2f °C, Umidade: %.2f %%
", temperatura, umidade);
      Serial.printf("Enviando dados para a API... (contagem de rostos: %d)
", contagemRostos);
      enviarDados(temperatura, umidade, contagemRostos);
    }

    // Zera a contagem de rostos
    contagemRostos = 0;
  }
}
