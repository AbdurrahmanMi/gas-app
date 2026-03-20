#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <DHT.h>
#include <time.h>
#include <addons/TokenHelper.h>
#include <addons/RTDBHelper.h>

#define WIFI_SSID     "YOUR_WIFI_NAME"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"
#define API_KEY       "YOUR_FIREBASE_API_KEY"
#define DATABASE_URL  "YOUR_FIREBASE_DATABASE_URL"
#define USER_EMAIL    "YOUR_FIREBASE_EMAIL"
#define USER_PASSWORD "YOUR_FIREBASE_PASSWORD"
#define DHTPIN        26
#define DHTTYPE       DHT11

DHT dht(DHTPIN, DHTTYPE);
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

unsigned long lastSend = 0;
const char* ntpServer       = "pool.ntp.org";
const long  gmtOffset_sec   = 3 * 3600;
const int   daylightOffset  = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");

  configTime(gmtOffset_sec, daylightOffset, ntpServer);

  config.api_key                  = API_KEY;
  config.database_url             = DATABASE_URL;
  auth.user.email                 = USER_EMAIL;
  auth.user.password              = USER_PASSWORD;
  config.token_status_callback    = tokenStatusCallback;

  Firebase.begin(&config, &auth);
  Firebase.reconnectNetwork(true);
}

String getTimeStamp() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) return "0000-00-00_00:00:00";
  char buffer[25];
  strftime(buffer, sizeof(buffer), "%Y-%m-%d_%H:%M:%S", &timeinfo);
  return String(buffer);
}

void loop() {
  if (Firebase.ready() && millis() - lastSend > 60000) {
    lastSend = millis();

    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (isnan(h) || isnan(t)) {
      Serial.println("DHT read error!");
      return;
    }

    String path = "/dht_history/" + getTimeStamp();
    FirebaseJson json;
    json.set("temperature", t);
    json.set("humidity",    h);

    if (Firebase.RTDB.setJSON(&fbdo, path.c_str(), &json))
      Serial.println("Data sent: T=" + String(t) + " H=" + String(h));
    else
      Serial.println("Error: " + fbdo.errorReason());
  }
}
