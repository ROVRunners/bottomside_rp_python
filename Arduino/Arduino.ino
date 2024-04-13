#define VALUE_LENGTH 6

// characters read from serial port
char buffer[64];
int read_bytes = 0;

// integers read from port
int values[VALUE_LENGTH];
int read_values = 0;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(20);

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
  buffer[read_bytes++] = c;

  // every time 4 bytes are read, parse an integer
  if (read_bytes >= 4) {
    parse_int();
    read_bytes = 0;
  }

  // when we've read all 6 values, reset back to start
  if (read_values >= VALUE_LENGTH) {
    print_values();
    read_values = 0;
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
      int c = buffer[i] << offset;
      ans += c;

      // the next byte will be another 8 bits to the left
      offset += 8;
  }

  values[read_values++] = ans;
}

void print_values() {
  for (int i = 0; i < VALUE_LENGTH; ++i) {
    Serial.print(values[i]);
    Serial.print(";");
  }
  Serial.println("");
  read_values = 0;
}