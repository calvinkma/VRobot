 // Based on:
 // http://tmrh20.github.io/RF24/
 //~ - CONNECTIONS: nRF24L01 Modules See:
 //~ http://arduino-info.wikispaces.com/Nrf24L01-2.4GHz-HowTo
 //~ 1 - GND
 //~ 2 - VCC 3.3V !!! NOT 5V
 //~ 3 - CE to Arduino pin 7
 //~ 4 - CSN to Arduino pin 2
 //~ 5 - SCK to Arduino pin 13
 //~ 6 - MOSI to Arduino pin 11
 //~ 7 - MISO to Arduino pin 12
 //~ 8 - UNUSED

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define CE_PIN  7
#define CSN_PIN 2

const uint64_t slaveID = 0xE8E8F0F0E1LL;

RF24 radio(CE_PIN, CSN_PIN); // Create a Radio

void setup() {
    Serial.begin(115200);
    radio.begin();
    radio.setDataRate(RF24_250KBPS);
    //radio.setRetries(3,2); // delay, count
}

void loop() {
    unsigned char byte_to_send;
    if(Serial.available() > 0)
    {
        byte_to_send = Serial.read();
        radio.openWritingPipe(slaveID);
        bool rslt = radio.write(&byte_to_send, sizeof(byte_to_send));
    }
}
