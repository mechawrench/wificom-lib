# wificom-lib (Using dmcomm-python)

<p align="center">
    <a href="https://discord.gg/yJ4Ub64zrP">
        <img src="https://dcbadge.vercel.app/api/server/yJ4Ub64zrP">
    </a>
</p>

[![Pylint](https://github.com/mechawrench/wificom-lib/actions/workflows/pylint.yml/badge.svg)](https://github.com/mechawrench/wificom-lib/actions/workflows/pylint.yml)

This library enables an RP2040 device using dmcomm-python (CircuitPython 8.x) to connect to https://wificom.dev to enable DigiRom reading and writing via HTTP API calls and MQTT for device interactions.

## Credits

This project was enabled by the great work, help, and input from BladeSabre.  Find the repo this one is built on top of at https://github.com/dmcomm/dmcomm-python.

Credits to the other great developers on the WiFiCom Discord.

A list of contributors will come as pull requests appear

## RP2040 Board Support

### Supported Boards
- Arduino Nano Connect
- Raspberry Pi Pico W
- RP2040 with AirLift co-processor module
    - Pi Pico is the only tested board so far but others should work as well

### Unsupported Boards
- RP2040 Challenger with WiFi Chip
    - Issues with SSL with onboard chip; doesn't allow for secure requests

## Building a (WiFi) Pico-Com
- Visit https://dmcomm.github.io/guide/pi-pico/ for more information on this topic
- Ensure you match pins on your supported board with those found in the example "board_config.py" file.  The pins have been optimized by BladeSabre for the boards found in "board_config.py".  If you have a different board, you will need to adjust the pins in the "board_config.py" file.

## Installation

1. Check the version of WiFiCom you're installing in CHANGLOG.md to find the versions of dependencies we tested with it (other versions might not work)
1. Install CircuitPython to the board
1. Copy the "wificom" folder in this repository to your "lib" folder in your "CIRCUITPY" drive
1. Copy the "code.py" file to your "CIRCUITPY" drive, replace existing "code.py"
1. Copy the "boot.py" file into the "CIRCUITPY" drive, replace existing "boot.py"
1. Copy the "board_config.py" file into the "CIRCUITPY" drive, replace existing "board_config.py"
    - Keep the old version for reference if you've made modifications
1. Copy the "digiroms.py" file into the "CIRCUITPY" drive, replace existing "digiroms.py"
    - Keep the old version for reference if you've made modifications
1. Install dmcomm-python into the "CIRCUITPY" drive
    1. Copy the "lib/dmcomm" folder into the lib folder in your "CIRCUITPY" drive
1. Install the following libs, find all of these in the libs folder of the CircuitPython [AdaFruit bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases) (8.x mpy archive)
   1. adafruit_bus_device
   1. adafruit_display_text
   1. adafruit_esp32spi
   1. adafruit_minimqtt - note you may need an older version of this
   1. adafruit_displayio_ssd1306.mpy
   1. adafruit_requests.mpy
1. Copy the "secrets.py.example" to "secrets.py" and make changes to match your environment (you can get a prefilled version on the website)
1. Modify "board_config.py" so that pinouts match your board, we advise using what you find as default but you can modify as needed
1. Test that everything works, you should see the following output from Arduino IDE Serial Monitor
    ```
    10:59:45.103 -> dmcomm-python starting
    10:59:45.103 -> Connecting to WiFi network [WIFI_SSID]...
    10:59:46.387 -> Connected to WiFi network!
    10:59:46.423 -> Connecting to MQTT Broker...
    10:59:47.046 -> Connected to MQTT Broker! 
    10:59:47.481 -> Subscribed to USERNAME/f/1111111111111111-2222222222222222/wificom-input with QOS level 0
    ```
## Screen
There is an optional UI with a small screen and 3 buttons. Guide to follow.

## LED Indicator
- Arduino Nano RP2040 Connect: on-board orange LED
- Raspberry Pi Pico: on-board green LED
- Raspberry Pi Pico W: external LED is required

### LED Meanings
- Blinking indicates connecting to WiFi and MQTT
- Solid (dimmed) LED indicates connected and no errors
- Solid (bright) LED indicates waiting for Digimon/Legendz device during real-time battle
- LED OFF indicates failure, please restart your device
- During startup, see below

## Button Usage During Startup
- To use "WiFiCom mode (without drive access)", do not press the button
- To use "WiFiCom mode (with drive access)", hold button until LED comes on, then release
- To use "Serial Only Mode", hold button until LED comes on, keep holding until LED starts flashing or goes off
