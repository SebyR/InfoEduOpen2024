#include <Servo.h>

int pinRot = 4;
int pinTragaci = 3;
int pinTensiune = 2;

Servo rot;
Servo tragaci;  
Servo tensiune;

int serial_data[3];  // Array to hold servo positions

void setup() {
    Serial.begin(115200);
    rot.attach(pinRot);
    tragaci.attach(pinTragaci);
    tensiune.attach(pinTensiune);
    rot.write(90);
    tragaci.write(90);
    tensiune.write(100);
}

void loop() {
    if (Serial.available()) {
        String data = Serial.readStringUntil('\n');  // Read the string until newline character

        char data_char[data.length() + 1];  // Create a mutable character array
        data.toCharArray(data_char, data.length() + 1);  // Copy string to char array

        int i = 0;
        char* token = strtok(data_char, " ");  
        
        while (token != NULL && i < 3) {
            serial_data[i] = atoi(token);  
            Serial.println(serial_data[i]);
            token = strtok(NULL, " ");
            i++;
        }
        
        // Update servo positions
        if (serial_data[0] >= 5 && serial_data[0] <= 175) {
            rot.write(serial_data[0]);
        }
        
        if (serial_data[1] >= 0 && serial_data[1] <= 200) {
            tensiune.write(serial_data[1]);
        }
        
        if (serial_data[2] >= 10 && serial_data[2] <= 180) {
            tragaci.write(serial_data[2]);
        }

    }
}