#include <Servo.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

Servo servo;  // create servo object to control a servo
RF24 radio(7, 2); // CE, CSN
const byte address[6] = "00001";
//int ackData[1] = {12};
int text = 0xFF;
int Left_motor_go=8;
int Left_motor_back=9; 
int Right_motor_go=3;
int Right_motor_back=4;
bool aval=true;
const uint64_t deviceID = 0xE8E8F0F0E1LL;
int servo_pos = 180;    // variable to store the servo position

void setup() {
  // RF Init
  Serial.begin(9600);
  delay(1000);
  radio.begin();
  radio.setDataRate(RF24_250KBPS);
  radio.openReadingPipe(1,deviceID);
  radio.startListening();  
  //radio.enableAckPayload();
  //radio.writeAckPayload(1, ackData, sizeof(ackData));
  //radio.openReadingPipe(0, address);
  //radio.setPALevel(RF24_PA_MIN);
  //radio.startListening();
  
  // Servo Init
  servo.attach(6);  // attaches the servo on pin 6
  servo.write(servo_pos);
  //Serial.println("sadf");
  //radio.startListening();
}


//---------------Direct---------------
void moveServo(int pos) {
  servo.write(pos);
  delay(15);
}

//---------------Drive---------------
void back(int time)
{
  digitalWrite(Right_motor_go,LOW);
  digitalWrite(Right_motor_back,HIGH);
  //analogWrite(Right_motor_go,0);
  //analogWrite(Right_motor_back,150);
  digitalWrite(Left_motor_go,HIGH);
  digitalWrite(Left_motor_back,LOW);
  //analogWrite(Left_motor_go,150);
  //analogWrite(Left_motor_back,0);
  delay(time * 100);
}

void brake(int time)
{
  digitalWrite(Right_motor_go,LOW);
  digitalWrite(Right_motor_back,LOW);
  digitalWrite(Left_motor_go,LOW);
  digitalWrite(Left_motor_back, LOW);
  delay(time * 100);
}

void go(int time)
{
  digitalWrite(Right_motor_go,HIGH); 
  digitalWrite(Right_motor_back,LOW);     
  //analogWrite(Right_motor_go,200);
  //analogWrite(Right_motor_back,0);
  digitalWrite(Left_motor_go,LOW); 
  digitalWrite(Left_motor_back,HIGH);
  //analogWrite(Left_motor_go,0);
  //analogWrite(Left_motor_back,200);
  delay(time * 100);
}
//---------------Main---------------
void loop()
{
  while(1)
  {
    //Serial.println("1");
    if (radio.available())
    {
      //Serial.println("2");
      radio.read(&text, sizeof(text));
      Serial.println(text);
      if (text==0xFF)
      {
        delayMicroseconds(250);
        break;
      }
    }
  }

  while (!radio.available());
  
  radio.read(&text, sizeof(text));
  //Serial.println(text);
  delayMicroseconds(250);
  
  servo.write((int)text);
  if (radio.available())
  {
    radio.read(&text, sizeof(text));
    Serial.println("3");
    //Serial.println(text);
  }
  
  if (((int)text)>25 && ((int)text<100))
  {
    go(10);
  }
  
  else if (((int)text)<-25 && ((int)text)>-100)
  {
    back(10);
  }
  
  else
  {
    brake(10);
  }
}
