#include <CurieBLE.h>
#include <Servo.h>


Servo myservo;

int inByte = 0;
int currentByteRange = 0;
int state = 0;

boolean connectState = true;

BLEDevice peripheral;
BLECharacteristic controlChar;

BLEService ledService("19B10001-E8F3-537F-4F6D-D104768A1216"); // create service
// create switch characteristic and allow remote device to read and write
BLECharCharacteristic switchChar("19B10001-E8F3-537F-4F6D-D104768A1216", BLERead | BLEWrite);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  BLE.begin();
  myservo.attach(9);
  myservo.write(120);
  BLE.scanForUuid("19B10000-E8F2-537E-4F6C-D104768A1214");
}
 

void loop() {
  // put your main code here, to run repeatedly:
    
    BLEDevice peripheral = BLE.available();
    
    if (peripheral) {
      // discovered a peripheral, print out address, local name, and advertised service
      Serial.print("Found ");
      Serial.print(peripheral.address());
      Serial.print(" '");
      Serial.print(peripheral.localName());
      Serial.print("' ");
      Serial.print(peripheral.advertisedServiceUuid());
      Serial.println();
      // stop scanning
      BLE.stopScan();
    }
    Serial.println("Connecting ...");

    if (peripheral.connect()) {
      Serial.println("Connected");
    } else {
      Serial.println("Failed to connect!");
      return;
    }
  
    // discover peripheral attributes
    Serial.println("Discovering attributes ...");
    if (peripheral.discoverAttributes()) {
      Serial.println("Attributes discovered");
    } else {
      Serial.println("Attribute discovery failed!");
      peripheral.disconnect();
      return;
    }
  
    // retrieve the LED characteristic
   BLECharacteristic controlChar = peripheral.characteristic("19B10001-E8F2-537E-4F6C-D104768A1216");
  
    if (!controlChar) {
      Serial.println("Peripheral does not have LED characteristic!");
      peripheral.disconnect();
      return;
    } else if (!controlChar.canWrite()) {
      Serial.println("Peripheral does not have a writable LED characteristic!");
      peripheral.disconnect();
      return;
    }

    while (peripheral.connected()) {
      if (Serial.available()){
        inByte = (int)Serial.read();
        Serial.print(inByte);
        if (inByte >= 90 && inByte <= 150){
          myservo.write(inByte);
          Serial.println("ServoMove!");
        }else{
          controlChar.writeByte(inByte);
          Serial.println("Sent");
        }
      }
    }
}


