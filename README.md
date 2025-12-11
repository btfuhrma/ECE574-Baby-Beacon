Baby Beacon Project
1. Hardware requirements:
    - LoRaWAN ESP32V3 Microcontroller
    - MPU6050 Gryoscope/Temperature Sensor
    - Adafruit I2S MEMS Microphone
2. Hardware Setup (Libraries and Pin Connections)
    - Libraries: ArduinoSound; Adafruit MPU6050; Heltec ESP32 Dev-boards
    - Microphone: GND - GND; VCC - 3.3v; SEL - GND; LRCL - GPIO2; DOUT - GPIO39; BCLK - GPIO3
    - MPU6050: GND - GND; VCC - 3.3V; SDA - GPIO41; SCL - GPIO42
3. Running Web application
    - Requirements: Python 3.x; django (python module)
    - Navigate to Baby Beacon (lowest directory folder)
    - Type 'python manage.py runserver'
