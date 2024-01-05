#include <iostream>
#include <string>
#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"
#include <cstdlib>
#include <ctime>
#include <BH1750.h>
#include <Wire.h>
#include <ArduinoJson.h>
#include <WiFiClientSecure.h>

using namespace std;
const char* ssid = "aaa ";
const char* password = "anacondaxs5";
//const char* mqtt_server = "192.168.239.2";
const char* mqtt_server = "08e56ac55e6545fd9c563fdbafc7e768.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;  // Sử dụng cổng 8883 cho mqtts
const char* mqttUser = "olympic963";
const char* mqttPassword = "Anacondaxs5";

#define DHTPIN 4   
#define DHTTYPE DHT11   
#define DEVICE1PIN 18   
#define DEVICE2PIN 19 
#define DEVICE3PIN 23   
#define ALARM 33
#define GAS_AO 13
#define GAS_DO 32
#define BUTTON1 25
#define BUTTON2 26
#define BUTTON3 27
#define DEBOUNCE_TIME 200
bool lastButton1State = LOW;
bool lastButton2State = LOW;
bool lastButton3State = LOW;
unsigned long lastButton1PressTime = 0;
unsigned long lastButton2PressTime = 0;
unsigned long lastButton3PressTime = 0;
DHT dht(DHTPIN, DHTTYPE);

//WiFiClient espClient;
WiFiClientSecure espClient;
PubSubClient client(espClient);
BH1750 lightMeter;

// struct LuxRange {
//     int min;
//     int max;
// };
// LuxRange getLuxRange(const String& date, int hour) {
//     // Phân loại mùa dựa trên ngày
//     int day = date.substring(0, 2).toInt();
//     int month = date.substring(3, 5).toInt();
//     LuxRange range;   
//     if(month >= 2 && month <= 4) {
//         if(hour >= 6 && hour < 9) range = {10000, 20000};
//         else if(hour >= 9 && hour < 15) range = {20000, 100000};
//         else if(hour >= 15 && hour < 18) range = {10000, 20000};
//         else range = {0, 500};
//     }
//     else if(month >= 5 && month <= 8) {
//         if(hour >= 5 && hour < 8) range = {10000, 50000};
//         else if(hour >= 8 && hour < 16) range = {50000, 100000};
//         else if(hour >= 16 && hour < 19) range = {10000, 50000};
//         else range = {0, 500};
//     }
//     else if(month >= 9 && month <= 11 ) {
//         if(hour >= 5 && hour < 8) range = {10000, 20000};
//         else if(hour >= 8 && hour < 16) range = {20000, 80000};
//         else if(hour >= 16 && hour < 19) range = {10000, 20000};
//         else range = {0, 500};
//     }
//     else{
//         if(hour >= 6 && hour < 9) range = {5000, 10000};
//         else if(hour >= 9 && hour < 16) range = {10000, 50000};
//         else if(hour >= 16 && hour < 18) range = {5000, 10000};
//         else range = {0, 500};
//     } 
//     return range;
// }
// int randomLuxValue(const LuxRange& range) {
//     return range.min + rand() % (range.max - range.min + 1);
// }

void setup_wifi() {
  delay(10);
  WiFi.begin(ssid, password);
  int connectionAttempts = 0;
  while (WiFi.status() != WL_CONNECTED && connectionAttempts < 15) {
  // while (!isWiFiConnected() && connectionAttempts < 15) {
    Serial.print("Connecting to ");
    Serial.print(ssid);
    Serial.println("...");
    delay(1000);
    connectionAttempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Wifi connected");
    espClient.setInsecure();
  } else {
    Serial.println("Failed to connect to Wi-Fi.");
  }
}

void reconnect() {
  while (!client.connected() && WiFi.status() == WL_CONNECTED) {
    Serial.println("Connecting MQTT...");
    if (client.connect("ESP32Client" ,mqttUser, mqttPassword)) {
      client.subscribe("ESP32/deviceControl");
      // client.subscribe("ESP32/timestamp");
      client.subscribe("ESP32/Wifi");
      client.subscribe("ESP32/setInterval");    
    } else {
      Serial.print("MQTT connection failed. Reason: ");
      Serial.println(client.state());
      delay(500);
    }
  }
  Serial.println("MQTT connected");
}

void reportDeviceStatus(int devicePin, const char* status) {
  char topic[50];
  int display = devicePin - 17;
  sprintf(topic, "ESP32/Device/%d", display);
  if(client.connected()){
    client.publish(topic, status);
    Serial.print("Publish to topic ");
    Serial.print(topic);
    Serial.print(" state: ");
    Serial.println(status);
  }
}

void curInterval(int itv) {
  char current[50];
  sprintf(current, "%d", itv); 
  if(client.connected()){
    client.publish("ESP32/curInterval", current );
    Serial.print("Publish to topic ESP32/curInterval value:");
    Serial.println(current);
  }
}

String lastMessage1 = "";
String lastMessage2 = "";
String lastMessage3 = "";
unsigned long MESSAGE_INTERVAL = 10000;

void callback(char* topic, byte* message, unsigned int length) {
  String messageTemp;
  for (int i = 0; i < length; i++) {
    messageTemp += (char)message[i];
  }
  if (String(topic) == "ESP32/deviceControl") {
  Serial.print("Received message from topic ESP32/deviceControl: ");
  Serial.println(messageTemp);
    if (messageTemp == "on1" && messageTemp != lastMessage1) {
      digitalWrite(DEVICE1PIN, HIGH);
      reportDeviceStatus(DEVICE1PIN, "ON");
      lastMessage1 = messageTemp;
    } 
    else if (messageTemp == "off1" && messageTemp != lastMessage1) {
      digitalWrite(DEVICE1PIN, LOW);
      reportDeviceStatus(DEVICE1PIN, "OFF");
      lastMessage1 = messageTemp;
    }
    else if (messageTemp == "on2" && messageTemp != lastMessage2) {
      digitalWrite(DEVICE2PIN, HIGH);
      reportDeviceStatus(DEVICE2PIN, "ON");
      lastMessage2 = messageTemp;
    } 
    else if (messageTemp == "off2" && messageTemp != lastMessage2) {
      digitalWrite(DEVICE2PIN, LOW);
      reportDeviceStatus(DEVICE2PIN, "OFF");
      lastMessage2 = messageTemp;
    }
    else if (messageTemp == "on3" && messageTemp != lastMessage3) {
      digitalWrite(DEVICE3PIN, HIGH);
      reportDeviceStatus(DEVICE3PIN - 3, "ON");
      lastMessage3 = messageTemp;
    } 
    else if (messageTemp == "off3" && messageTemp != lastMessage3) {
      digitalWrite(DEVICE3PIN, LOW);
      reportDeviceStatus(DEVICE3PIN - 3, "OFF");
      lastMessage3 = messageTemp;
    }
  }
  // if (String(topic) == "ESP32/timestamp") {
  //   resDate = messageTemp; // Lấy chuỗi ISO từ thông điệp 
  //   // Serial.println(isoDate);
  // }
  if (String(topic) == "ESP32/setInterval") {
    Serial.print("Received message from topic ESP32/setInterval: ");
    Serial.println(messageTemp);
    MESSAGE_INTERVAL = messageTemp.toInt() * 1000; 
    curInterval(MESSAGE_INTERVAL/1000);
  }
}
void checkButtonStateAndToggleLight(int buttonPin, int devicePin, String& lastMessage, bool& lastButtonState, unsigned long& lastPressTime) {
    bool currentState = digitalRead(buttonPin);
    unsigned long currentTime = millis();
    if (currentState != LOW && lastButtonState == LOW && (currentTime - lastPressTime) > DEBOUNCE_TIME) {
        lastPressTime = currentTime;        
        String topicMessage;
        if (digitalRead(devicePin) == LOW) {  
            digitalWrite(devicePin, HIGH);
            topicMessage = "ON";
        } else { 
            digitalWrite(devicePin, LOW);
            topicMessage = "OFF";
        }
        if(client.connected()){
          if(devicePin != 23){
            reportDeviceStatus(devicePin, topicMessage.c_str());
          }else{
            reportDeviceStatus(devicePin - 3, topicMessage.c_str());
          }
        }
        lastMessage = topicMessage;
    }
    lastButtonState = currentState;
}
void buttonTask(void * parameter) {
  for(;;) {
    checkButtonStateAndToggleLight(BUTTON1, DEVICE1PIN, lastMessage1, lastButton1State, lastButton1PressTime);
    checkButtonStateAndToggleLight(BUTTON2, DEVICE2PIN, lastMessage2, lastButton2State, lastButton2PressTime);
    checkButtonStateAndToggleLight(BUTTON3, DEVICE3PIN, lastMessage3, lastButton3State, lastButton3PressTime);
    delay(50);
  }
}
void setup() {
  Serial.begin(115200);
  pinMode(DEVICE1PIN, OUTPUT);
  pinMode(BUTTON1, INPUT);
  pinMode(DEVICE2PIN, OUTPUT);
  pinMode(BUTTON2, INPUT);
  pinMode(DEVICE3PIN, OUTPUT);
  pinMode(BUTTON2, INPUT);
  pinMode(ALARM, OUTPUT);
  pinMode(GAS_DO, INPUT);
  xTaskCreate(
    buttonTask,            // Hàm thực thi
    "Button Check Task",   // Tên của task
    2048,                  // Kích thước ngăn xếp (stack size)
    NULL,                  // Tham số truyền vào cho hàm task (không sử dụng)
    1,                     // Độ ưu tiên
    NULL                   // Task handle
  );
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  //client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  reconnect();
  dht.begin();
  Wire.begin();
  // lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE, 0x5C); //chân ADO nối với 3v3
  lightMeter.begin(); //chân ADO nối với GND 
  srand(millis()); 
  reportDeviceStatus(DEVICE1PIN, "OFF");
  reportDeviceStatus(DEVICE2PIN, "OFF");
  curInterval(MESSAGE_INTERVAL/1000);
}

unsigned long lastMessage = 0;
void loop() {
  if(WiFi.status() != WL_CONNECTED) {
    setup_wifi();
  }
  else if (!client.connected() && WiFi.status() == WL_CONNECTED) {
    reconnect();
  } 
  else {
    client.loop(); 
  }
  unsigned long now = millis();  
  if (now - lastMessage > MESSAGE_INTERVAL) {
    lastMessage = now;
    float h = dht.readHumidity();
    float t = dht.readTemperature(); 
    float b = lightMeter.readLightLevel();
    //float b = 0.0f + static_cast<float>(std::rand()) / (static_cast<float>(RAND_MAX/99999.0f));
    if (isnan(h) || isnan(t)|| isnan(b)) {
    // if (isnan(b)) {
      Serial.println("Failed to read data from sensor!");
    }
    if (client.connected()) {
      Serial.println("Send to MQTT server:");
      char tempMsg[50];
      // int hour = resDate.substring(0, 2).toInt();
      // Serial.println(hour);
      // String date = resDate.substring(9, 11) + "/" + resDate.substring(12, 14);
      // Serial.println(date);
      // LuxRange range = getLuxRange(date, hour);
      // int b = 0;
      // b = randomLuxValue(range);
      snprintf(tempMsg, 50, "%.1f,%.1f,%.0f", t, h, b);
      // snprintf(tempMsg, 50, "%.0f", b);
      client.publish("ESP32/temperature_humidity_brightness", tempMsg);
      Serial.println(tempMsg);
    } 
    else {
      Serial.println("Not connected to MQTT server");
    }    
  }
  delay(200); 
}