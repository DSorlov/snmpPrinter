# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-10-14

### Added
- Cached values feature: Integration now remembers last known sensor values when printer is offline
- Offline status indication in sensor attributes with timestamp of last successful data fetch
- Status sensor now shows "offline" state when using cached data

## [1.0.0] - 2025-10-01

### Added
- Initial release
- SNMP v1, v2c, and v3 support
- Automatic printer discovery via Zeroconf/mDNS (a bit slow due to pulling snmp values but works)
- Manual printer configuration
- Support for major printer brands (Brother, Canon, HP, Konica Minolta, Kyocera, Lexmark, OKI, Panasonic, Ricoh, Samsung, Sharp, Xerox)
- Support for MIB and MIBII
- Wide sensor coverage:
  - Printer status sensor with attributes
  - Cover status sensor
  - Total pages sensor with color/BW breakdown
  - Toner/ink level sensors
  - Paper tray sensors
  - Waste container sensor
  - Drum unit sensors
  - Other consumable sensors
- Device information display (manufacturer, serial number, MAC address)
- Automatic web interface link detection (check if web gui reachable)
- Display text service for printer displays (make amazing automations!)
- Localization support