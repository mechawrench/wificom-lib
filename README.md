# wificom-lib (Using dmcomm-python)

<p align="center">
    <a href="https://discord.gg/yJ4Ub64zrP">
        <img src="https://dcbadge.vercel.app/api/server/yJ4Ub64zrP">
    </a>
</p>

[![Pylint](https://github.com/mechawrench/wificom-lib/actions/workflows/pylint.yml/badge.svg)](https://github.com/mechawrench/wificom-lib/actions/workflows/pylint.yml)

This library enables an RP2040+WiFi device using dmcomm-python (CircuitPython 8.x) to connect to https://wificom.dev to enable DigiRom reading and writing via HTTP API calls and MQTT for device interactions.

## Credits

This project was enabled by the great work, help, input and code additions from BladeSabre.  Find the repo this one is built on top of at https://github.com/dmcomm/dmcomm-python.

Credits to the other great developers on the WiFiCom Discord.

## RP2040 Board Support

### Supported Boards
- Raspberry Pi Pico W - RECOMMENDED OPTION
- Arduino Nano Connect
- RP2040 with AirLift co-processor module
    - Pi Pico is the only tested board so far but others should work as well

### Unsupported Boards
- RP2040 Challenger with WiFi Chip
    - Issues with SSL with onboard chip; doesn't allow for secure requests
- RP2040 Challenger with WiFi/BLE Chip
    - Issues with SSL with onboard chip; doesn't allow for secure requests

## Building a (WiFi) Pico-Com
- Visit https://dmcomm.github.io/guide/pi-pico/ for more information on this topic
- Ensure you match pins on your supported board with those found in the example "board_config.py" file.  The pins have been optimized by BladeSabre for the boards found in "board_config.py".  If you have a different board, you will need to adjust the pins in the "board_config.py" file.

## Initial Installation

1. Install CircuitPython 8.x to the board
    - Raspberry Pi Pico W: https://circuitpython.org/board/raspberry_pi_pico_w/
    - Arduino Nano RP2040 Connect: https://circuitpython.org/board/arduino_nano_rp2040_connect/
    - Pico with AirLift: https://circuitpython.org/board/raspberry_pi_pico/
1. Download the latest release from releases page, you'll be looking for a file named "wificom-lib_RELEASEVERSION.zip"
1. Extract the zip and copy the contents into the root of the CIRCUITPY drive
    - If you are using an unsupported board or custom circuit layout, then before copying to CIRCUITPY, modify "board_config.py" so that pinouts match your board
1. Copy the "secrets.py.example" to "secrets.py" and make changes to match your environment (you can get a prefilled version on the website https://wificom.dev)
1. Check that the system boots, then eject CIRCUITPY from the computer and replug the USB to enable the `boot.py` configuration
1. Test that everything works, you should see the following output from Arduino IDE Serial Monitor (Mac/Linux) / MU Editor (Windows) after the screen comes up and you select "Wifi"
    ```
    10:59:45.103 -> Connecting to WiFi network [WIFI_SSID]...
    10:59:46.387 -> Connected to WiFi network!
    10:59:46.423 -> Connecting to MQTT Broker...
    10:59:47.046 -> Connected to MQTT Broker! 
    10:59:47.481 -> Subscribed to USERNAME/f/1111111111111111-2222222222222222/wificom-input with QOS level 0
    ```
1. If you need to change any files, put the WiFiCom into drive mode (or dev mode if necessary) using the instructions below

## Upgrade Firmware
1. Backup your current files, in particular the following are commonly modified:
    - secrets.py
    - board_config.py
    - config.py (previously digiroms.py)
1. Update CircuitPython if required
1. Put the WiFiCom into drive mode so that the CIRCUITPY drive is writeable
1. Download the latest release from releases page, you'll be looking for a file named "wificom-lib_RELEASEVERSION.zip"
1. Extract the zip and copy the contents into the root of the CIRCUITPY drive
1. Compare contents of your modified files with the new files and make any necessary changes
1. Test that everything works, including connecting to WiFi and sending/receiving DigiRoms

## Screen

The UI has a small screen and 3 buttons. Some features are supported on a minimal build with only one button and no screen, but the full build is recommended.

### Buttons
- Button A: select menu options
- Button B: activate selected option
- Button C: cancel/return (needs to be held for several seconds when device is busy)

### Menu options
- WiFi: Connect to WiFi and MQTT and await instructions from the server
- Serial: Act as a normal serial com unit
- Punchbag: Communicate with the toys in a standalone mode (you can edit `config.py` to change the available options in this submenu)
- Drive: Make the CIRCUITPY drive writeable so you can edit configuration or update firmware

## LED Indicator
- Raspberry Pi Pico W: external LED is required
- Arduino Nano RP2040 Connect: on-board orange LED
- Raspberry Pi Pico: on-board green LED

### LED Meanings
- Blinking indicates connecting to WiFi and MQTT
- Solid (dimmed) LED indicates connected and no errors
- Solid (bright) LED indicates waiting for Digimon/Legendz device during real-time battle
- LED OFF indicates failure, please restart your device
- During startup, see below

## Button Usage During Startup
- To use "WiFiCom mode (with drive read-only)", do not press the button
- To use "WiFiCom mode (with full drive access)", also known as "Dev mode", hold the C button until the LED comes on, then release
- To use "Serial Only mode", hold the C button until the LED comes on, and keep holding until the LED goes dim or off

## Dependencies

Runs on CircuitPython 8.x. Check the CHANGELOG for the exact version tested with each release.

### Libraries

These are included in the release zip. If installing manually, check `sources.json` for versions. In particular, `adafruit_minimqtt` is likely to break if a different version is used from the one specified.

- dmcomm-python
- adafruit_bus_device
- adafruit_display_text
- adafruit_esp32spi
- adafruit_minimqtt
- adafruit_displayio_ssd1306
- adafruit_requests

### Server

wificom.dev is open-source. The code is available at:
- https://github.com/mechawrench/wificom-webapp/
- https://github.com/mechawrench/wificom-mosquitto-docker/
