#include "secrets.h"
#include <WiFi.h>
#include <Wire.h>
#include <heltec_unofficial.h>
#include <driver/i2s.h>
#include <HTTPClient.h>

#define I2S_WS   2    // J3 pin 13 (LRCLK)
#define I2S_SCK  3    // J3 pin 14 (BCLK)
#define I2S_SD   39   // J3 pin 10 (DOUT from mic)

const uint8_t MPU_ADDR = 0x68;

String API_KEY = "";

// Replace address with deployed server address or host computers IPV4 address
const char* serverURL = "http://127.0.0.1:8000/api/data";

void sendData(float temperature, float amplitude) {
  if (WiFi.status() == WL_CONNECTED && API_KEY != "") {

    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"api_key\":\"" + API_KEY +
                     "\",\"temperature\":" + String(temperature, 2) +
                     ",\"amplitude\":" + String(amplitude, 8) + "}";

    int response = http.POST(payload);

    Serial.print("POST status: ");
    Serial.println(response);

    http.end();
  }
}


String fetchAPIKey() {
    HTTPClient http;
    // Replace address with deployed server address or host computers IPV4 address
    http.begin("http://127.0.0.1:8000/api/getToken");

    int code = http.GET();
    if (code != 200) {
        Serial.println("Failed to fetch API key");
        return "";
    }

    String response = http.getString();
    Serial.println("Raw key response: " + response);

    int start = response.indexOf("\"api_key\":\"");
    if (start == -1) return "";

    start += 11;

    int end = response.indexOf("\"", start);
    if (end == -1) return "";

    String key = response.substring(start, end);
    return key;
}


void setup() {
  // WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.begin(115200);

  Serial.println("Connecting to WiFi...");

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  int attempts = 0;

  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
      attempts++;

      if (attempts > 40) {
          Serial.println("\nFailed to connect to WiFi. Restarting...");
          ESP.restart();
      }
  }
  Serial.println("\nWiFi connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  while (API_KEY == "") {
      Serial.println("Fetching API key...");
      API_KEY = fetchAPIKey();
      delay(1000);
  }
  Serial.println("API Key loaded: " + API_KEY);

  // Wake up MPU6050 (it starts in sleep mode)
  Wire.begin();
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);Wire.write(0);
  Wire.endTransmission(true);

  delay(100);

  i2s_config_t i2s_config = {
      .mode = i2s_mode_t(I2S_MODE_MASTER | I2S_MODE_RX),
      .sample_rate = 16000,
      .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
      .channel_format = I2S_CHANNEL_FMT_ONLY_RIGHT,
      .communication_format = i2s_comm_format_t(I2S_COMM_FORMAT_I2S),
      .intr_alloc_flags = 0,
      .dma_buf_count = 8,
      .dma_buf_len = 1024,
      .use_apll = false,
      .tx_desc_auto_clear = false,
      .fixed_mclk = 0
  };

  i2s_pin_config_t pin_config = {
      .bck_io_num = I2S_SCK,
      .ws_io_num = I2S_WS,
      .data_out_num = I2S_PIN_NO_CHANGE,
      .data_in_num = I2S_SD
  };

  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin_config);
  i2s_set_clk(I2S_NUM_0, 16000, I2S_BITS_PER_SAMPLE_32BIT, I2S_CHANNEL_MONO);

}

void loop() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x41);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 2, true);

  int16_t rawTemp = (Wire.read() << 8) | Wire.read();
  float temperatureC = (rawTemp / 340.0) + 36.53;

  Serial.print("Temperature: ");
  Serial.print(temperatureC);
  Serial.println(" °C");

  int32_t samples[1024];
  size_t bytesRead = 0;
  i2s_read(I2S_NUM_0, (char*)samples, sizeof(samples), &bytesRead, portMAX_DELAY);

  int sampleCount = bytesRead / sizeof(int32_t);
  double avgAmplitude = 0;
  for (int i = 0; i < sampleCount; i++) {
    avgAmplitude += abs(samples[i] >> 14);
  }
  avgAmplitude /= sampleCount;

  Serial.print("Average Amplitude: ");
  Serial.println(avgAmplitude);

  sendData(temperatureC, avgAmplitude);

  delay(1000);
}
