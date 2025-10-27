#include "secrets.h"
#include <WiFi.h>
#include <Wire.h>
#include <heltec_unofficial.h>
#include <driver/i2s.h>
#include <HTTPClient.h>

#define I2S_WS   2    // J3 pin 13 (LRCLK)
#define I2S_SCK  4    // J3 pin 14 (BCLK)
#define I2S_SD   38   // J3 pin 10 (DOUT from mic)

const uint8_t MPU_ADDR = 0x68;

const char* serverURL = "http://127.0.0.1:8000/data";

void sendData(float temperature, float amplitude) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"temperature\":" + String(temperature, 2) +
                     ",\"amplitude\":" + String(amplitude, 2) + "}";

    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0) {
      Serial.print("POST Response: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Error: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("WiFi disconnected.");
  }
}

void setup() {
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.begin(115200);

  // Wake up MPU6050 (it starts in sleep mode)
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);Wire.write(0);
  Wire.endTransmission(true);

  delay(100);

  i2s_config_t i2s_config = {
      .mode = i2s_mode_t(I2S_MODE_MASTER | I2S_MODE_RX),
      .sample_rate = 16000,
      .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
      .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
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
  // put your main code here, to run repeatedly:
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x41);  // Starting register for temperature
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
    avgAmplitude += abs(samples[i] >> 14); // scale down 32-bit
  }
  avgAmplitude /= sampleCount;

  Serial.print("Average Amplitude: ");
  Serial.print(avgAmplitude);

  sendData(temperatureC, avgAmplitude);

  delay(500);
}
