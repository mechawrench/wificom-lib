# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Audio prompts for Pendulum X RTB

## [0.7.0] - 2023-02-02
### Added
- Ack for webapp sent commands
- Sound output with various beeps for different menu actions
### Changed
- UI object now exists even when there is no display
- wificom modules are no longer in subpackages
- realtime.py (with the real-time battle logic) moved to wificom-lib from dmcomm-python
- Cleaned up serial messages regarding MQTT
- Moved NINA-specific socket setting to `wifi_nina`
### Removed
- Old version of Legendz RTB classes
### Tested with
- CircuitPython 8.0.0-beta-4
- adafruit-circuitpython-bundle-8.x-mpy-20221104 except `adafruit_minimqtt` [8.x-mpy-5.5.1](https://github.com/adafruit/Adafruit_CircuitPython_MiniMQTT/releases/tag/5.5.1)
- dmcomm-python 2022-10-22 fd8a61a

## [0.6.0] - 2022-11-07
### Added
- UI with screen and 3 buttons
- Mode selection menu
- Standalone punchbag feature
- Mode switching via reboot and instructions saved in NVM
  - "Dev mode" (button released during startup) provides unprotected access to all features without rebooting
### Changed
- WiFi/Serial/Drive are now separate modes (WiFi mode no longer listens on serial)
- Default CIRCUITPY state is now read-only instead of hidden
- Fixed RAM waste importing `adafruit_esp32spi` on Pico W
- Minimqtt class introduced in place of PlatformIO
### Removed
- PlatformIO dependency
### Tested with
- CircuitPython 8.0.0-beta-4
- adafruit-circuitpython-bundle-8.x-mpy-20221104 except `adafruit_minimqtt` [8.x-mpy-5.5.1](https://github.com/adafruit/Adafruit_CircuitPython_MiniMQTT/releases/tag/5.5.1)
- dmcomm-python 2022-10-22 fd8a61a

## [0.5.0] - 2022-10-28
### Added
- Pico W support
- Support for an external LED on an alternative pin

### Tested with
- CircuitPython 8.0.0-beta-3
- adafruit-circuitpython-bundle-8.x-mpy-20221025
    - An issue was found later: recommend downgrading `adafruit_minimqtt` to 5.5.1
- dmcomm-python 2022-10-22 fd8a61a

## [0.4.0] - 2022-08-22
### Added
- Added board detection to boot.py
- Realtime battles for Legendz and Digimon Pendulum X
- Shared topics added for Realtime battles
- Realtime battles now has its own callback
- Realtime battles output now goes to a separate function
- Added serial only mode (enabled by holding the button on the board throughout startup until the LED comes on and then starts flashing or goes dim)
- Added WiFiCom mode w/ drive access (enabled by holding the button on the board on startup, then releasing when the LED comes on)
- Added LED status indicators 

### Changed
- Fixed heartbeat during RTB
- Updated secrets.py.example to reflect current state of configuration

### Removed
- Removed PlatformIO class

## [0.3.1] - 2022-08-06
### Removed
- Custom MQTT port in favor of default SSL port, now required for mqtt access

## [0.3.0] - 2022-08-05
### Added
- Added lowercase checks to fix mixed case bug for topic subscriptions
- Raspberry Pi Pico with Airlift module support for WiFi
- Fixes for develop to work when subscribing to it's topic
- board_config.py added for board pin assignments and auto-detection of used board
### Changed
- Added proper button pin per BladeSabre recommendation (Set for Arduino Nano Connect by default)
- Update topic to use username instead of email
### Removed
- Removed timezone from secrets.py.example

## [0.2.1] - 2022-07-28
### Removed
- Added Pylint GitHub action to ensure code meets standards on PR, and other pushes
- Refactored all .py files to meet Pylint standards set out
- Added .pylintrc file for CI

## [0.2.0] - 2022-07-28
### Added
- Added Pylint GitHub action to ensure code meets standards on PR, and other pushes
- Refactored all .py files to meet Pylint standards set out
- Added .pylintrc file for CI

## [0.1.0] - 2022-07-28
### Added
- Added ability for app users to hide output on the serial console for WebApp interactions

## [0.0.1] - 2022-07-28
### Added
- License using MIT, based on BladeSabre base license
- Added application_uuid to MQTT messages on device to enable parsing of which application should get output back

[Unreleased]: https://github.com/mechawrench/wificom-lib/compare/v0.7.0...develop
[0.7.0]: https://github.com/mechawrench/wificom-lib/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/mechawrench/wificom-lib/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/mechawrench/wificom-lib/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/mechawrench/wificom-lib/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/mechawrench/wificom-lib/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/mechawrench/wificom-lib/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/mechawrench/wificom-lib/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mechawrench/wificom-lib/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/mechawrench/wificom-lib/compare/v0.0.1