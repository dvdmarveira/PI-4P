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

// ========== CONFIGURAÇÕES DE HARDWARE (ESP32-CAM) ==========
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

// Pino do sensor DHT22 (GPIO 4 no ESP32-CAM costuma ser o LED Flash, cuidado. 
// Se estiver usando adaptador, verifique se é o pino 4 ou 13, 14, etc.)
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// ========== CONFIGURAÇÕES DE REDE E API ==========
const char* ssid = "minhaRede";        // <--- SEU WIFI
const char* password = "12345678";    // <--- SUA SENHA

const char* api_url = "https://pi-4p.onrender.com/api/leituras"; 

// ========== VARIÁVEIS GLOBAIS ==========
unsigned long tempoAnterior = 0;
const unsigned long intervaloContagem = 60000; // 1 minuto
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
  config.frame_size = FRAMESIZE_QVGA; // Baixa resolução para processar rápido
  config.jpeg_quality = 12;
  config.fb_count = 1;

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
  Serial.println("\nWiFi conectado!");
}

void enviarDados(float temperatura, float umidade, int rostos) {
  if (WiFi.status() == WL_CONNECTED) {
    StaticJsonDocument<200> doc;
    doc["temperatura"] = temperatura;
    doc["umidade"] = umidade;
    doc["faces_detectadas"] = rostos;
    
    // Adicione campos extras para evitar erro no simulador se houver validação
    doc["qualidadeAr"] = 0; 
    doc["nivelCO"] = 0;

    String json;
    serializeJson(doc, json);

    // CONFIGURAÇÃO HTTPS (SSL)
    esp_http_client_config_t config = {
      .url = api_url,
      .method = HTTP_METHOD_POST,
      .timeout_ms = 10000,
      .cert_pem = NULL, 
      .skip_cert_common_name_check = true,  // IMPORTANTE PARA RENDER/HTTPS
    };

    esp_http_client_handle_t client = esp_http_client_init(&config);
    esp_http_client_set_header(client, "Content-Type", "application/json");
    esp_http_client_set_post_field(client, json.c_str(), json.length());

    esp_err_t err = esp_http_client_perform(client);
    if (err == ESP_OK) {
      Serial.printf("Status HTTP: %d\n", esp_http_client_get_status_code(client));
    } else {
      Serial.printf("Falha HTTP: %s\n", esp_err_to_name(err));
    }
    esp_http_client_cleanup(client);
  } else {
    Serial.println("WiFi desconectado.");
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
  
  // Desativa Brownout Detector
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
}

// ========== LOOP ==========
void loop() {
  unsigned long tempoAtual = millis();
  
  // Simples detecção de movimento/rosto (simulado para este exemplo)
  // Em projeto real, usaríamos detecção na imagem do frame buffer
  camera_fb_t *fb = esp_camera_fb_get();
  if (fb) {
    esp_camera_fb_return(fb);
    // Lógica simples: incrementa aleatoriamente para teste
    // Remova o if abaixo se tiver lógica real de detecção
    if (random(0, 100) > 95) { 
       contagemRostos++;
       Serial.println("Rosto detectado (simulado)!");
    }
  }

  if (tempoAtual - tempoAnterior >= intervaloContagem) {
    tempoAnterior = tempoAtual;

    float umidade = dht.readHumidity();
    float temperatura = dht.readTemperature();

    if (isnan(umidade) || isnan(temperatura)) {
      Serial.println("Falha sensor DHT!");
      // Envia zeros ou tenta ler de novo
      enviarDados(0, 0, contagemRostos);
    } else {
      Serial.printf("Temp: %.1f C, Umid: %.1f %%\n", temperatura, umidade);
      enviarDados(temperatura, umidade, contagemRostos);
    }
    contagemRostos = 0;
  }
  delay(100); // Pequeno delay para não travar CPU
}
