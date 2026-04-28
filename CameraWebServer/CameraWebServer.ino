#include "esp_camera.h"
#include <WiFi.h>

#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

// WiFi credentials
const char *ssid = "Kailu";
const char *password = "kailash@171206";

void startCameraServer();

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(false);  // 🔥 disable debug logs

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

  // 🚀 LOW LATENCY SETTINGS
  config.xclk_freq_hz = 10000000;  // lower clock = stable + less lag
  config.pixel_format = PIXFORMAT_JPEG;

  config.frame_size = FRAMESIZE_QQVGA;    // 160x120 (fastest)
  config.jpeg_quality = 15;               // higher = more compression
  config.fb_count = 1;                    // 🔥 no buffering
  config.grab_mode = CAMERA_GRAB_LATEST;  // always latest frame
  config.fb_location = CAMERA_FB_IN_PSRAM;

  // Init camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed: 0x%x\n", err);
    return;
  }

  // 🔧 Disable heavy processing for speed
  sensor_t *s = esp_camera_sensor_get();
  s->set_brightness(s, 0);
  s->set_contrast(s, 0);
  s->set_saturation(s, 0);

  s->set_gain_ctrl(s, 0);      // disable auto gain
  s->set_exposure_ctrl(s, 0);  // disable auto exposure
  s->set_awb_gain(s, 0);       // disable white balance

  // WiFi connect
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);  // 🔥 reduces latency

  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");

  // Start streaming server
  startCameraServer();

  Serial.print("Stream URL: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/stream");
}

void loop() {
  delay(10000);  // nothing here
}