# Microclimate

At start, this project aim was to create ventilation system that requires almost zero end-user interaction, using CO2 level as trigger.
I'm using two Blauberg Vento systems - protocol is here:
https://blaubergventilatoren.de/uploads/download/ventoexpertduowsmarthousev11en2.pdf
for ventilation, Winsen MH-Z19b - for monitoring CO2 level and (currently) Orange Pi Zero Plus2 for putting things together.
Tested for  two years now, everything works good.

Now i have extended the system with BME280 sensor, heater control, and small http server (some code changed to allow server-side scripts execution).

More about heater control here:
https://docs.google.com/document/d/1_drADWenzFtNRgrBaX9dGQfiQEofACiw6MladfzTkYg

co2.py - Ventilation control. Reads CO2 level from Winsen MH-Z19b via serial and adjusts Blauberg fan speed via WiFi.

bme280.py - Heater control. Reads data (temperature, pressure, relative humidity) from BME280 sensor via i2c and controls heater via 433Mhz transmitter and receiver relay. No WiFi here as it's pretty critical.

plot.py - Graphs data.

gen.sh - Generates web-page.

micro-httpd.c - smallest http server. Not mine, i've just added basic GET form support. (/bin treated as a location with executables) 

Prereqs:
pip3 install smbus pyserial
#I couldn't install numpy from source
apt install python3-numpy python3-matplotlib
