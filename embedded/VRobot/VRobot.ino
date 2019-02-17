#include <Servo.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

Servo servo;  // create servo object to control a servo
RF24 radio(7, 2); // CE, CSN
const byte address[6] = "00001";
char text[1] = {0xFF};
int Left_motor_go=0;
int Left_motor_back=1; 
int Right_motor_go=2;
int Right_motor_back=3;

int servo_pos = 90;    // variable to store the servo position

void setup() {
  // RF Init
  Serial.begin(9600);
  radio.begin();
  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_MIN);
  radio.startListening();
  
  // Servo Init
  servo.attach(6);  // attaches the servo on pin 6
  servo.write(servo_pos);

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
  analogWrite(Right_motor_go,0);
  analogWrite(Right_motor_back,150);
  digitalWrite(Left_motor_go,HIGH);
  digitalWrite(Left_motor_back,LOW);
  analogWrite(Left_motor_go,150);
  analogWrite(Left_motor_back,0);
  delay(time * 100);
}

void brake(int time)
{
  analogWrite(Right_motor_go,0);
  analogWrite(Right_motor_back,0);
  analogWrite(Left_motor_go,0);
  analogWrite(Left_motor_back,0);
  delay(time * 100);
}

void run(int time)
{
  //digitalWrite(Right_motor_go,HIGH); 
  //digitalWrite(Right_motor_back,LOW);     
  analogWrite(Right_motor_go,200);
  analogWrite(Right_motor_back,0);
  digitalWrite(Left_motor_go,LOW); 
  digitalWrite(Left_motor_back,HIGH);
  analogWrite(Left_motor_go,0);
  analogWrite(Left_motor_back,200);
  delay(time * 100);
}
//---------------Main---------------
void loop() {
   while(1){
      if ( radio.available() ) {
        radio.read(&text, sizeof(text));
        Serial.println(text);
        if (((int)text)!=0xFF){
          break;}
        }
  }
  if ( radio.available() ) {
        radio.read(&text, sizeof(text));
        Serial.println(text);
}
  servo.write((int)text);
   if ( radio.available() ) {
        radio.read(&text, sizeof(text));
        Serial.println(text);
}
   if (((int)text)>0) {
    run(10);
    }
   if (((int)text)<0) {
    back(10);
   }
   if (((int)text)==0) {
    brake(10);
   }
}
