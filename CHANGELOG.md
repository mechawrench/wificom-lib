# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2022-08-22
### Added
- Added board detection to boot.py
- Realtime battles for Digimon Pendulum X
- Initial groundwork laid for Realtime battles (Legendz)
- Shared topics added for Realtime battles
- Realtime battles now has it's own callback
- Realtime battles output now goes to a separate function
- Added function get_is_rtb_active to PlatformIO that allows us to determine if a RTB is active or not
- Added serial only mode (toggled by pressing the button on the board until LED goes out then releasing)
- Added WiFiCom mode w/ drive access (toggled by holding the button on the board until you see a orange led, then releasing)
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

[Unreleased]: https://github.com/mechawrench/wificom-lib/compare/v0.4.0...develop
[0.4.0]: https://github.com/mechawrench/wificom-lib/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/mechawrench/wificom-lib/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/mechawrench/wificom-lib/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/mechawrench/wificom-lib/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mechawrench/wificom-lib/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/mechawrench/wificom-lib/compare/v0.0.1