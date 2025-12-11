Baby Beacon Project
1. Hardware requirements:
    - LoRaWAN ESP32V3 Microcontroller
    - MPU6050 Gryoscope/Temperature Sensor
    - Adafruit I2S MEMS Microphone
2. Hardware Setup (Libraries and Pin Connections)
    - Libraries: ArduinoSound; Adafruit MPU6050; Heltec ESP32 Dev-boards; File called 'secrets.h' with wifi SSID and password saved as WIFI_SSID, WIFI_PASS
    - Disclaimer: If this web app was truly deployed, server URL variable in BabyBeacon.ino would reflect it. However, a placeholder is put in for localhost, but needs to be changed to host computers IPV4 address.
    - Microphone: GND - GND; VCC - 3.3v; SEL - GND; LRCL - GPIO2; DOUT - GPIO39; BCLK - GPIO3
    - MPU6050: GND - GND; VCC - 3.3V; SDA - GPIO41; SCL - GPIO42
3. Running Web application
    - Requirements: Python 3.x; django (python module)
    - Navigate to Baby Beacon (lowest directory folder)
    - Type 'python manage.py runserver'
4. Mock data from microcontroller
    - Use tester.py to mock the microcontroller
    - type 'python tester.py'
