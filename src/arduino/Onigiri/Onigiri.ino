/*
 * Copyright (c) 2016 Intel Corporation.  All rights reserved.
 * See the bottom of this file for the license terms.
 */

#define ONIGIRI_A

#include <CurieBLE.h>
#include <CurieIMU.h>
#include "notes.h"


#define NOGAME  0
#define GAME    1

const int ledPin = 13; // set ledPin to use on-board LED

// 0~11 or 151~162 means #1N, #1R, #1G, #2Y, #2N, ...
const int ledRedPins[3] = {3, 5, 7};
const int ledGreenPins[3] = {4, 6, 8};

// 12 ~ 48 or 162~198 means note C2 - C5
const int musicPin = 9;

int currentMode = NOGAME;



#ifdef ONIGIRI_A
BLEService onigiriService("19B10000-E8F2-537E-4F6C-D104768A1214");
unsigned int cmdBase = 0;
#endif

#ifdef ONIGIRI_B
BLEService onigiriService("19B10000-E8F2-537E-4F6C-D104768A1215"); 
unsigned char cmdBase = 151;
#endif

int shakeLevel = 0;
float subLevel = 1;
bool shaking = false;

BLECharCharacteristic controlChar("19B10001-E8F2-537E-4F6C-D104768A1216", BLERead | BLEWrite);
BLECharCharacteristic reportChar("19B10001-E8F2-537E-4F6C-D104768A1217", BLERead | BLENotify);

void setup() {
    Serial.begin(9600);
    pinMode(ledPin, OUTPUT); // use the LED on pin 13 as an output
    for (int i=3; i<=9; i++) {
        pinMode(i, OUTPUT);
    }

  // begin initialization
    BLE.begin();

  // set the local name peripheral advertises
#ifdef ONIGIRI_A
    BLE.setLocalName("OnigiriA");
#endif

#ifdef ONIGIRI_B
    BLE.setLocalName("OnigiriB");
#endif
    
    // set the UUID for the service this peripheral advertises
    BLE.setAdvertisedService(onigiriService);
    
    // add the characteristic to the service
    onigiriService.addCharacteristic(controlChar);
    onigiriService.addCharacteristic(reportChar);
    
    // add service
    BLE.addService(onigiriService);
    
    // assign event handlers for connected, disconnected to peripheral
    BLE.setEventHandler(BLEConnected, blePeripheralConnectHandler);
    BLE.setEventHandler(BLEDisconnected, blePeripheralDisconnectHandler);
    controlChar.setEventHandler(BLEWritten, controlCharacteristicWritten);
    controlChar.setValue(0);
    
    // start advertising
    BLE.advertise();

    CurieIMU.begin();
    CurieIMU.setAccelerometerRange(2);
    
    Serial.println(("Bluetooth device active, waiting for connections..."));
}

void loop() {
    // poll for BLE events
    BLE.poll();
#ifdef ONIGIRI_A
    float ax, ay, az;

    CurieIMU.readAccelerometerScaled(ax, ay, az);

    float norm = ax * ax + ay * ay + az * az;
    
    if (norm > 1.5) {
        shakeLevel += 10;
        subLevel = 1;
    } else {
        shakeLevel -= subLevel;
        subLevel *= 1.2;
    }

    if (shakeLevel < 0) {
        shakeLevel = 0;
        shaking = false;
    }

    if (shakeLevel > 17000 && !shaking) {
        Serial.println("Shake!");
        reportChar.writeByte((char)shakeLevel);
        shaking = true;
    }
#endif
    //Serial.println(shakeLevel);
}

void blePeripheralConnectHandler(BLEDevice central) {
    // central connected event handler
    Serial.print("Connected event, central: ");
    Serial.println(central.address());
}

void blePeripheralDisconnectHandler(BLEDevice central) {
    // central disconnected event handler
    Serial.print("Disconnected event, central: ");
    Serial.println(central.address());
}

void controlCharacteristicWritten(BLEDevice central, BLECharacteristic characteristic) {
  // central wrote new value to characteristic, update LED
    Serial.print("Characteristic event, written: ");
    unsigned char cmd = controlChar.value();
    Serial.println((int)cmd);
    if (cmd == 255) {
        currentMode = NOGAME;
        digitalWrite(ledRedPins[0], LOW);
        digitalWrite(ledGreenPins[0], LOW);
        digitalWrite(ledRedPins[1], LOW);
        digitalWrite(ledGreenPins[1], LOW);
        digitalWrite(ledRedPins[2], LOW);
        digitalWrite(ledGreenPins[2], LOW);
        return;
    }

#ifdef ONIGIRI_A
    if (cmd >= 0 and cmd <= 11) {
#endif

#ifdef ONIGIRI_B
    if (cmd >= 151 and cmd <= 162) {
#endif
        Serial.println("Set LED");
        if (cmd == cmdBase + 0) {
            digitalWrite(ledRedPins[0], LOW);
            digitalWrite(ledGreenPins[0], LOW);

        } else if (cmd == cmdBase + 1) {
            analogWrite(ledRedPins[0], 150);
            digitalWrite(ledGreenPins[0], LOW);

        } else if (cmd == cmdBase + 2) {
            analogWrite(ledRedPins[0], 150);
            analogWrite(ledGreenPins[0], 150);

        } else if (cmd == cmdBase + 3) {
            digitalWrite(ledRedPins[0], HIGH);
            digitalWrite(ledGreenPins[0], HIGH);
            Serial.println("HIGH");
        } else if (cmd == cmdBase + 4) {
            digitalWrite(ledRedPins[1], LOW);
            digitalWrite(ledGreenPins[1], LOW);

        } else if (cmd == cmdBase + 5) {
            analogWrite(ledRedPins[1], 120);
            digitalWrite(ledGreenPins[1], LOW);

        } else if (cmd == cmdBase + 6) {
            analogWrite(ledRedPins[1], 120);
            analogWrite(ledGreenPins[1], 180);

        } else if (cmd == cmdBase + 7) {
            digitalWrite(ledRedPins[1], HIGH);
            digitalWrite(ledGreenPins[1], HIGH);
            Serial.println("HIGH");
        } else if (cmd == cmdBase + 8) {
            digitalWrite(ledRedPins[2], LOW);
            digitalWrite(ledGreenPins[2], LOW);

        } else if (cmd == cmdBase + 9) {
            analogWrite(ledRedPins[2], 130);
            digitalWrite(ledGreenPins[2], LOW);

        } else if (cmd == cmdBase + 10) {
            analogWrite(ledRedPins[2], 125);
            analogWrite(ledGreenPins[2], 140);

        } else if (cmd == cmdBase + 11) {
            digitalWrite(ledRedPins[2], HIGH);
            digitalWrite(ledGreenPins[2], HIGH);
            Serial.println("HIGH");
        }
#ifdef ONIGIRI_A
    } else if (cmd > 11 && cmd < 48) {
#endif

#ifdef ONIGIRI_B
    } else if (cmd > 162 && cmd < 199) {
#endif
        int note = cmd - cmdBase - 12;
        Serial.println(note);
        tone(musicPin, freq[note], 600); 
    }
    //reportChar.setValue(switchChar.value() + 1);
}
