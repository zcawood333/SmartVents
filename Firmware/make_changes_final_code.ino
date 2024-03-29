#include <WiFi.h>
#include <esp_timer.h>
#include <Stepper.h>
#include "esp_system.h"
#include "esp_spi_flash.h"
#include "driver/rtc_io.h"
#include <ESP_LM35.h>
#include <WiFiUdp.h>
#include <OneWire.h>
#include <DallasTemperature.h>

ESP_LM35 temp(36);
#define ONE_WIRE_BUS 26
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
const uint64_t MY_UUID = 200;
const uint8_t VENT_TO_HUB_HEADER = 0;
const uint8_t HUB_TO_VENT_HEADER = 1;
const int stepsPerRevolution = 2048;    // total number of steps in a full revolution
Stepper my_stepper(stepsPerRevolution, 16, 13, 17, 15);
const int motionSensor = 12;
//const int motion_vcc = 12;
RTC_DATA_ATTR bool bootCount = LOW;
RTC_DATA_ATTR int position_value;
RTC_DATA_ATTR int Position_Stepper_Motor;
RTC_DATA_ATTR int Counter;
unsigned long startTime;
unsigned long sleepInterval = 30000000;  // time interval in microseconds after which ESP32 will go to sleep
RTC_DATA_ATTR int x;
int Motion_Wakeup = 0;
int Send_Count = 0;

const char* ssid = "Galaxy S21 FE 5Gd44f";
const char* password = "muffaqamjah";
IPAddress local_IP(192,168,0,10);
IPAddress gateway( 192,168,194,153);
IPAddress subnet(255,255,255,0);
unsigned int localPort = 5005;  // local port to listen for UDP packets
IPAddress multicast_IP(239, 255, 255, 249);  // Multicast IP address for ESP32s

char packetBuffer[ETH_MAX_PACKET_SIZE];  // buffer to hold incoming packet
WiFiUDP udp;



typedef struct {
  uint8_t header = VENT_TO_HUB_HEADER;
  uint64_t uuid = MY_UUID;
  float temperature;
  uint8_t motion;
} outPacket;

typedef struct {
  uint8_t header;
  uint64_t uuid;
  float louver_position;
} inPacket;

void sendData(float temperature, bool motion) {                                       
  Serial.println("Sending packet");
  Serial.print("Temperature is ");
  Serial.println(temperature);
  Serial.print("Motion is ");
  Serial.println(motion);
  uint8_t packet[sizeof(uint8_t) + sizeof(uint64_t) + sizeof(float) + sizeof(uint8_t)];
  uint8_t *p = packet;

  *p++ = VENT_TO_HUB_HEADER;
  memcpy(p, (uint8_t*)&MY_UUID, sizeof(uint64_t));
  p += sizeof(uint64_t);
  memcpy(p, (uint8_t*)&temperature, sizeof(float));
  p += sizeof(float);
  *p++ = motion ? 1 : 0;

  udp.beginPacket(multicast_IP, localPort);
  udp.write(packet, sizeof(packet));
  udp.endPacket();
}


inPacket receiveData() {
  inPacket received_packet = {0, 0, -1};
  int packetSize = udp.parsePacket();
  if (packetSize) {
    Serial.println("Got a message from the hub");
    udp.read(packetBuffer, packetSize);
    received_packet.header = packetBuffer[0];
    received_packet.uuid = *(uint64_t*)(packetBuffer + 1);
    if (received_packet.header == HUB_TO_VENT_HEADER && received_packet.uuid == MY_UUID) {
      received_packet.louver_position = *(float*)(packetBuffer + 9);
      printPacket(received_packet);
      int position_servo = received_packet.louver_position;
     


    // Convert the position servo value to degrees and calculate the new steps
        float position =  (position_servo - Position_Stepper_Motor) / 360.0;
        Serial.print("The adjusted angle is ");
        Serial.println(position_servo - Position_Stepper_Motor);
        
        float new_steps = (stepsPerRevolution * position);

    // Move the stepper motor to the new position
        my_stepper.step(new_steps);
        Position_Stepper_Motor = position_servo;
        Serial.print("The flash stepper motor value is ");
        Serial.println( Position_Stepper_Motor);
    } else {
      Serial.println("Packet not for me");
    }
  }
  return received_packet;
}

void printPacket(inPacket packet) {
  Serial.print("Header: ");
  Serial.println(packet.header);
  Serial.print("UUID: ");
  Serial.println(packet.uuid);
  Serial.print("Louver position: ");
  Serial.println(packet.louver_position);
}






void setup() 
{
  Serial.begin(115200);
  sensors.begin();
  esp_sleep_enable_ext0_wakeup(GPIO_NUM_12, 1);
  esp_sleep_enable_timer_wakeup(30000000);
  Serial.println("Woke up");
  my_stepper.setSpeed(7);
  pinMode(motionSensor, INPUT);

  Serial.println("IP address: " + WiFi.localIP().toString());

  WiFi.config(local_IP, gateway, subnet);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi!");
  print_wakeup_reason();

  udp.beginMulticast(multicast_IP, localPort);    // Start UDP server
  Serial.println("UDP server started");
  
  startTime = millis();
  delay(3500);
}

void print_wakeup_reason(){
  esp_sleep_wakeup_cause_t wakeup_reason;

  wakeup_reason = esp_sleep_get_wakeup_cause();

  switch(wakeup_reason)
  {
    case ESP_SLEEP_WAKEUP_EXT0 : Serial.println("Wakeup caused by external signal using RTC_IO"); x = 1;Motion_Wakeup = 1; break;
    case ESP_SLEEP_WAKEUP_EXT1 : Serial.println("Wakeup caused by external signal using RTC_CNTL"); break;
    case ESP_SLEEP_WAKEUP_TIMER : Serial.println("Wakeup caused by timer"); break;
    case ESP_SLEEP_WAKEUP_TOUCHPAD : Serial.println("Wakeup caused by touchpad"); break;
    case ESP_SLEEP_WAKEUP_ULP : Serial.println("Wakeup caused by ULP program"); break;
    default : Serial.printf("Wakeup was not caused by deep sleep: %d\n",wakeup_reason);Serial.println("120 degrees");my_stepper.step(682); break;
  }
  
}

void loop()
{
  
  //read motion data
  bool sensorValue = digitalRead(motionSensor);
  Serial.println(sensorValue);
  
  sensors.requestTemperatures(); 

  if( Motion_Wakeup == 1 )
  {
    sensorValue = HIGH;
    Motion_Wakeup = 0;
  }


   if(Send_Count == 0 || sensorValue == HIGH )
  {
    
    sendData(sensors.getTempFByIndex(0), sensorValue);
    Send_Count +=1; 
       
  }
 
 
  delay(1000);
  inPacket received_packet = receiveData();
  
  
   if (millis() - startTime >= sleepInterval / 1000 )
  {
    
    delay(5000);
    Serial.println("sleep for 0.5 minute");
    esp_deep_sleep_start();               // go to sleep 
  }
  
}
