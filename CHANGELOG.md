# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Initial groundwork laid for Realtime battles (Digimon/Legendz)
- Shared topics added for Realtime battles
- Usernames are now lowercase, if put into the file as mixed case it will correct itself
- Usernames are now the "name" you picked when siging up, i.e. brassbolt (in lowercase)
- Realtime battles now has it's own callback
- Realtime battles output now goes to a separate function, this is for future work
- Added function get_is_rtb_active to PlatformIO that allows us to determine if a RTB is active or not

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

[Unreleased]: https://github.com/mechawrench/wificom-lib/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/mechawrench/wificom-libreleases/tag/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mechawrench/wificom-libreleases/tag/v0.0.1...v0.1.0
[0.0.1]: https://github.com/mechawrench/wificom-libreleases/tag/v0.0.1