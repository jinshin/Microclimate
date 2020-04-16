# Microclimate

At start, this project aim was to create ventilation system that requires almost zero end-user interaction, using CO2 level as trigger.
I'm using two Blauberg Vento systems - protocol is here:
https://blaubergventilatoren.de/uploads/download/ventoexpertduowsmarthousev11en2.pdf
for ventilation, Winsen MH-Z19b - for monitoring CO2 level and (currently) Orange Pi Zero Plus2 for putting things together.
Tested for  two years now, everything works good.

Now i have extended the system with BME280 sensor, heater control, and small http server (some code changed to allow server-side scripts execution).

More about heater control here:
https://docs.google.com/document/d/1_drADWenzFtNRgrBaX9dGQfiQEofACiw6MladfzTkYg
