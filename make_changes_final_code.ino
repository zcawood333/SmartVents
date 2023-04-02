#include <WiFi.h>
#include <esp_timer.h>
#include <Stepper.h>
#include "esp_system.h"
#include "esp_spi_flash.h"
#include "driver/rtc_io.h"
#include <WiFiUdp.h>


const int stepsPerRevolution = 2048;    // total number of steps in a full revolution
Stepper my_stepper(stepsPerRevolution, 15, 0, 2, 4);
const int motionSensor = 14;
const int motion_vcc = 12;
RTC_DATA_ATTR bool bootCount = LOW;
RTC_DATA_ATTR int elapsed_time;
RTC_DATA_ATTR int Counter;
unsigned long startTime;
unsigned long sleepInterval = 60000000;  // time interval in microseconds after which ESP32 will go to sleep
RTC_DATA_ATTR int x;

const char* ssid = "Qayyum";
const char* password = "ammin1000";

IPAddress local_IP(192,168,0,10);
IPAddress gateway(192,168,0,1);
IPAddress subnet(255,255,255,0);
unsigned int localPort = 5005;  // local port to listen for UDP packets
IPAddress multicast_IP(239, 255, 255, 249);  // Multicast IP address for ESP32s

char packetBuffer[ETH_MAX_PACKET_SIZE];  // buffer to hold incoming packet
WiFiUDP udp;


void print_wakeup_reason(){
  esp_sleep_wakeup_cause_t wakeup_reason;

  wakeup_reason = esp_sleep_get_wakeup_cause();

  switch(wakeup_reason)
  {
    case ESP_SLEEP_WAKEUP_EXT0 : Serial.println("Wakeup caused by external signal using RTC_IO"); x = 1; break;
    case ESP_SLEEP_WAKEUP_EXT1 : Serial.println("Wakeup caused by external signal using RTC_CNTL"); break;
    case ESP_SLEEP_WAKEUP_TIMER : Serial.println("Wakeup caused by timer"); break;
    case ESP_SLEEP_WAKEUP_TOUCHPAD : Serial.println("Wakeup caused by touchpad"); break;
    case ESP_SLEEP_WAKEUP_ULP : Serial.println("Wakeup caused by ULP program"); break;
    default : Serial.printf("Wakeup was not caused by deep sleep: %d\n",wakeup_reason); break;
  }
  
}




void setup() 
{
  Serial.begin(115200);
  esp_sleep_enable_ext0_wakeup(GPIO_NUM_14, 1);
  esp_sleep_enable_timer_wakeup(60000000);
  Serial.println("Woke up");
  my_stepper.setSpeed(7);
  pinMode(motionSensor, INPUT);
  pinMode(motion_vcc, OUTPUT);
  delay(1000);

  
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
  

  digitalWrite(motion_vcc, HIGH); // Power up the motion sensor VCC
  rtc_gpio_hold_dis(GPIO_NUM_12);
  rtc_gpio_hold_en(GPIO_NUM_12);
  delay(67);
  rtc_gpio_set_level(GPIO_NUM_12, HIGH);

  

  startTime = millis();
  //delay(1500);
}

void loop()
{
  
  
  Counter++;
  //Serial.println(Counter);
  
  /*if (Counter >= 120)
  {
   
    bootCount = HIGH;
    Serial.print("BootCount is ");
    Serial.println(bootCount);
    Counter = 0;
    Serial.print("No motion detected and motion vcc is High");

    
  //send message to python
  char message[] = "No motion for 120 seconds";
  udp.beginPacket(multicast_IP, localPort);
  udp.write((uint8_t*)message, strlen(message));
  udp.endPacket();
  delay(1000);


  }
  
  /*if(digitalRead(motionSensor) == HIGH || x == 1 )
  {
    //y = elapsed_time;    
    Serial.println("Motion Sensor is HIGH");
    bootCount = LOW;
    x = 0;
    //Counter = 0;
  }*/
 



  //read data value of temperature
  
  // Define the data to be sent
  // Send the packet
  unsigned char header = 0x01;
  IPAddress uuid(192, 168, 0, 5);
  float temperature = 25.5;
  unsigned char motion = 0x01;

// Create a buffer to hold the packet data
  unsigned char Send_Packet[9];

// Pack the data into the packet buffer
  Send_Packet[0] = header;
  memcpy(&Send_Packet[1], &uuid, 4);
  memcpy(&Send_Packet[5], &temperature, 4);
  Send_Packet[9] = motion;

  udp.beginPacket(multicast_IP, localPort);
  udp.write(Send_Packet, 9);
  udp.endPacket();
  delay(1000);


  // receive data
  int packetSize = udp.parsePacket();
if (packetSize) {
  // Read the packet into the buffer
  udp.read(packetBuffer, packetSize);

  // Unpack the binary data into variables
  unsigned char header = packetBuffer[0];
  if(header == 1)
  {
    
  
  byte uuid_bytes[4];
  memcpy(uuid_bytes, &packetBuffer[1], 4);
  byte louver_position[4];
  memcpy(&louver_position, &packetBuffer[5], 4);  // Change to read 8 bytes instead of 4 bytes

  // Convert the UUID bytes to IP address format
  String uuidIpAddress = "";
  for (int i = 0; i < 4; i++) {
    uuidIpAddress += String(uuid_bytes[i], DEC);
    if (i < 3) {
      uuidIpAddress += ".";
    }
  }

  String louver_data = "";
  for (int i = 0; i < 4; i++) {
    louver_data += String(louver_position[i], DEC);
    if (i < 1) {
      louver_data += ".";
    }
    else{
      louver_data +="";
    }
  }

  // Print the values
  Serial.print("Header: ");
  Serial.println(header);
  Serial.print("UUID: ");
  Serial.println(uuidIpAddress);
  Serial.print("Louver Position: ");
  Serial.println(louver_data);

  
  IPAddress ip_address(uuid_bytes[0], uuid_bytes[1], uuid_bytes[2], uuid_bytes[3]);
  if (local_IP == ip_address)
    {

      if( louver_position[3] == 1 )
      {

      
    // Extract the position servo value from the message
      int position_servo = atoi(louver_data.c_str());


    // Convert the position servo value to degrees and calculate the new steps
      float position = position_servo / 360.0;
      float new_steps = (stepsPerRevolution * position);

    // Move the stepper motor to the new position
      my_stepper.step(-new_steps);
      }

      else
      {
        int position_servo = atoi(louver_data.c_str());


    // Convert the position servo value to degrees and calculate the new steps
        float position = position_servo / 360.0;
        float new_steps = (stepsPerRevolution * position);

    // Move the stepper motor to the new position
        my_stepper.step(new_steps);
      }
      
    }
  }
}

  /*if (millis() - startTime >= sleepInterval / 1000)
  {
    //bootCount  = ! bootCount;

    digitalWrite(motion_vcc, bootCount); // Power down motion sensor
    rtc_gpio_hold_dis(GPIO_NUM_12);
    rtc_gpio_hold_en(GPIO_NUM_12);
    delay(67);
    rtc_gpio_set_level(GPIO_NUM_12, bootCount); // Set GPIO 12 to high
    delay(5000);
    Serial.println("BootCount is " + String(bootCount));
    Serial.println("sleep for 1 minute");
    esp_deep_sleep_start();   // go to sleep 
  }*/
  
}
