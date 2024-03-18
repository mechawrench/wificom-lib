# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

See [unreleased] commits. Notes are in the pull request descriptions.

## [1.2.0] - 2024-04-18
### Added
* "Settings" section in main menu
  * Version info
  * Sound ON/OFF setting
  * Drive (moved here from main menu)
  * UF2 Bootloader - for updating CircuitPython
* "i" command ("info") now works on WiFi as well as serial, and now beeps
* New "p" command ("pause") on WiFi or serial, does not beep
* Version info is reported to server with heartbeat
* Battery monitor display when in WiFi/Punchbag modes (if configured in `board_config`)
* Status and brief instructions displayed on-screen for different types of DigiROM
* Sounds to indicate "interesting" DigiROM results or errors executing the DigiROM
### Changed
* Updated dmcomm-python to v0.8.0: see [CHANGELOG](https://github.com/dmcomm/dmcomm-python/blob/main/CHANGELOG.md)
* Drive moved into Settings
* Drive no longer shows a menu, just "Hold C to exit"
* Serial mode responds immediately when no DigiROM is active
### Fixed
* Now using the device's native screen resolution
* Network failures detected more quickly
* Incorrect MQTT credentials detected more quickly
* Initial connection failure now logged on screenless units
### Removed
* "variant" from version info
### Tested with
* CircuitPython 8.2.2

## [1.1.0] - 2023-11-26
### Added
* Support for non-WiFi boards
  * `board_config` entries for P-Coms using Pi Pico or Xiao RP2040
  * On non-WiFi boards (P-Coms) only:
    * Default startup mode is Serial instead of WiFi
    * Button held on startup enters Dev Mode even if not released before LED goes out (to allow for P-Coms with no LED)
* Connection lost improvements:
  * When connection is lost, shows a specific error message on screen
  * Press B to reconnect after connection lost or WiFi/MQTT failed to connect; press A for menu as before
  * On screenless units, press the button to restart after crash or connection loss
* "i" version info command on serial
  * New file `version_info.py` with version info from build CI
### Changed
* Stop using data serial connection; use console serial connection for everything
* Stop rebooting between modes (except Drive Mode)
* Use SleepMemory instead of NVM for rebooting
* Request drive eject for fresh installs
* Drive Mode no longer remembered when unplugged
* Soft reboot instead of hard when running WiFi a second time - faster and doesn't drop serial
### Fixed
* Serial digiroms now work reliably with CR terminator as well as LF - fixes w0rld Android
* No longer crashes from character decoding errors on serial
* Don't send serial data when no app is connected - resolves serial data echo on Linux
### Removed
* `board_config` entry for Pi Pico WiFiCom with AirLift
### Tested with
- CircuitPython 8.2.2

## [1.0.0] - 2023-08-21
### Added
- More LED and audio feedback:
  - Beep once and blink LED 3 times when a new DigiROM or real-time battle setup request is received over WiFi or serial. (Previously just beeped on new DigiROM over WiFi.)
  - Blink LED briefly when reporting DigiROM results, like for the Arduino version. "Interesting" results give a slightly longer blink.
  - Play a sound when reaching main menu after completing startup.
  - Play a sound when WiFi/MQTT is ready to receive DigiROMs from the server.
  - Error beep on bad command via WiFi or serial.
  - Short LED blink every 2 seconds when failure is reported.
  - Beep on press-to-reboot after failure.
- Report "command" and "receive" errors to server via MQTT, visible on the website alongside DigiROM results.
- Catch unexpected exceptions and log the tracebacks to `wificom_log.txt` in CIRCUITPY. Rotate file to `wificom_log_old.txt` according to size. Can reboot with button press after a crash.
### Changed
- Updated dmcomm-python to v0.7.0:
  - Finalized Data Link - removed "!" - bytes are reversed from the "!" version.
  - Finalized Fusion Loader - removed "!!" with no changes.
  - Added calculation features in sequence DigiROMs.
- Real-time battle improvements:
  - Retry final connection.
  - LED blink for final connection.
  - Stale messages expire.
  - Players no longer need to press simultaneously for Legendz.
- Rebooting after failure waits for short A press instead of holding C.
- Screenless units can reboot by pressing the single button when failure is reported.
- Use failure alert feature for `secrets.py` errors.
- `boot.py` now reads button and LED pins from `board_config`.
- Various menu text updated.
- Removed "Drive" option from Dev Mode menu.
- Updated to CircuitPython 8.2.2.
- Increased `pystack` size.
- Updated README.md credits to reflect current project contributions.
### Fixed
- No longer crashes when `secrets.py` wireless network list has the wrong structure.
### Tested with
- CircuitPython 8.2.2

## [0.10.0] - 2023-04-24
- No changes from rc1.

## [0.10.0-rc1] - 2023-04-18
### Added
- Separate builds for Nina and PicoW microcontrollers, with the ability to use variants for the MiniMQTT dependency. Will show up as two archives, one ending in `_nina.zip` and other in `_picow.zip`, for both artifacts and release bundles.
### Changed
- Most code from `code.py` moved to `lib/wificom/main.py` with minor changes to accomodate this. This code can now be included in the release `mpy` builds for faster startup times.
- Updated `dmcomm-python` to v0.6.0 (basic Digimon Color support, DMOG fix).
- For messages which can appear in serial mode, changed ending of output lines from "\n" to "\r\n" to match Arduino.
- Disabled auto-reload on CIRCUITPY changes, except when in dev mode.
### Tested with
- CircuitPython 8.0.5

## [0.9.0] - 2023-02-27
### Added
- Sound on/off config option
- MQTT retries on connection failure (set to 3 times)
- New function connection_failure_alert() in code.py to handle shared wifi/mqtt failure alerts
- GitHub Action to compile libraries into mpy files
- Multiple WiFi network support, configured through secrets.py, see secrets.example.py for updates
- Retry each WiFi network up to 3 times each before moving on to the next
- New sound "beep_wifi_failure" for when WiFi fails to connect
- Audible beep for when a DigiROM is received via MQTT while on Wifi mode
### Changed
- Punchbag DigiROMs moved to `config.py` (`digiroms.py` removed)
- Changed recommended `prong_in` on "Pi Pico + AirLift" from GP26 to GP22
- Can now return to punchbag menu from a punchbag DigiROM
- Updated dmcomm-python to v0.5.0
- Default mqtt server in secrets.example.py is now "mqtt.wificom.dev", changed from "mqtt-production.wificom.dev
- Renamed secrets.py.example to secrets.example.py
### Removed
- In secrets.py the values "ssid" and "password" are no longer used, removed from example.  Users must now use wifi_networks array instead.  This is a breaking change, you will get errors connecting to WiFi until you update your secrets.py file to match secrets.example.py
- Combined merge-libs-from-remote.yml GitHub Action into single file with mpy compilation
### Tested with
- CircuitPython 8.0.2 (note: does not work with more recent)

## [0.8.0] - 2023-02-15
### Added
- Audio prompts for Pendulum X RTB
- GitHub Action for combining third party libs into one archive for easy installation on microcontrollers
### Changed
- Errors with secrets.py are caught, and displayed on the screen when attempting WiFi (other modes are able to run)
- Reboot when entering WiFi mode for a second time to avoid reinitialization errors
- Updated README.md to reflect new installation process
- Updated README.md to more accurately reflect current project status
### Tested with
- CircuitPython 8.0.0

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

[Unreleased]: https://github.com/mechawrench/wificom-lib/compare/v1.2.0...main
[1.2.0]: https://github.com/mechawrench/wificom-lib/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/mechawrench/wificom-lib/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/mechawrench/wificom-lib/compare/v0.10.0...v1.0.0
[0.10.0]: https://github.com/mechawrench/wificom-lib/compare/v0.10.0-rc1...v0.10.0
[0.10.0-rc1]: https://github.com/mechawrench/wificom-lib/compare/v0.9.0...v0.10.0-rc1
[0.9.0]: https://github.com/mechawrench/wificom-lib/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/mechawrench/wificom-lib/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/mechawrench/wificom-lib/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/mechawrench/wificom-lib/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/mechawrench/wificom-lib/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/mechawrench/wificom-lib/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/mechawrench/wificom-lib/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/mechawrench/wificom-lib/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/mechawrench/wificom-lib/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mechawrench/wificom-lib/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/mechawrench/wificom-lib/compare/v0.0.1
