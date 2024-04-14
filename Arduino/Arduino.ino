#include <Servo.h>
#define DATA_RECV_LENGTH 6
#define MOTOR_COUNT 6

int servo_pins[MOTOR_COUNT] = {3, 5, 6, 9, 10, 11};

Servo servo[MOTOR_COUNT];

// characters read from serial port
unsigned char buffer[64];
int bytes_consumed = 0;

// integers read from port
int data_recv[DATA_RECV_LENGTH];
int data_recv_consumed = 0;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(20);

  for (int i = 0; i < MOTOR_COUNT; ++i) {
    servo[i].attach(servo_pins[i]);
  }
  
  Serial.println("Begin.");
}

void loop() {
  while (Serial.available()) {
    handleSerial();
  }

  delay(20);
}

void handleSerial() {
  // grab a byte
  int c = Serial.read();

  // add it to the buffer
  buffer[bytes_consumed++] = c;

  // every time 4 bytes are read, parse an integer
  if (bytes_consumed >= 4) {
    parse_int();
    bytes_consumed = 0;
  }

  // when we've read all 6 values, reset back to start
  if (data_recv_consumed >= DATA_RECV_LENGTH) {
    print_data_recv();
    set_motors();
    data_recv_consumed = 0;
  }
}

// sending bytes from lowest to highest
void parse_int() {
  // grab first byte
  int ans = buffer[0];

  int offset = 8;
  
  // iterate through rest of bytes
  for (int i = 1; i < 4; ++i) {
      // shift them over to right order of magnitude
      int c = buffer[i];
      ans += c << offset;

      // the next byte will be another 8 bits to the left
      offset += 8;
  }
  
  data_recv_consumed[data_recv_consumed++] = ans;
}

void set_motors() {
  for (int i = 0; i < MOTOR_COUNT; ++i) {
    servo[i].writeMicroseconds(data_recv_consumed[i]);
  }
}

void print_data_recv() {
  for (int i = 0; i < DATA_RECV_LENGTH; ++i) {
    Serial.print(data_recv_consumed[i]);
    Serial.print(";");
  }
  Serial.println("");
}
