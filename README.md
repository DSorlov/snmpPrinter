![maintained](https://img.shields.io/maintenance/yes/2025.svg)
[![hacs_badge](https://img.shields.io/badge/hacs-default-green.svg)](https://github.com/custom-components/hacs)
[![ha_version](https://img.shields.io/badge/home%20assistant-2025.08%2B-green.svg)](https://www.home-assistant.io)
![version](https://img.shields.io/badge/version-1.0.0-green.svg)
![stability-alpha](https://img.shields.io/badge/stability-stable-green.svg)
[![maintainer](https://img.shields.io/badge/maintainer-dsorlov-blue.svg)](https://github.com/DSorlov)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# SNMP Printer Integration for Home Assistant

Are you tired of different printers and different integrations? I was, this is a one-to-rule-them-all integration for getting status about your printers. This integration supports automatic discovery and manual configuration of printers, providing detailed status information, supply levels, and automation capabilities.

## Features

- :mag: **Automatic Discovery**: Automatically discovers SNMP-enabled printers via Zeroconf/mDNS
- :printer: **Wide Printer Support**: Compatible with Brother, Canon, HP, Konica Minolta, Kyocera, Lexmark, OKI, Panasonic, Ricoh, Samsung, Sharp, and Xerox printers
- :bar_chart: **Monitoring**: Track printer status, toner levels, paper trays, drums, and more
- :wrench: **SNMP Version Configuration**: Support for SNMP v1, v2c, and v3
- :robot: **Automation Ready**: Trigger automations based on printer events

## Supported Sensors

For each configured printer, the integration creates:

- **Status Sensor**: Current printer status (ready, jammed, etc.) with uptime, memory, page count, and other attributes
- **Cover Status Sensor**: Current cover/door status
- **Total Pages Sensor**: Total pages printed (with color and B&W breakdown)
- **Toner/Ink Sensors**: Individual sensors for each toner cartridge showing remaining level
- **Paper Tray Sensors**: Status and capacity for each paper tray
- **Waste Container Sensor**: Waste toner box fill level
- **Drum Unit Sensors**: Remaining life for drum units
- **Other Consumables**: Belt units, finishers, etc.

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the "+" button
4. Search for "SNMP Printer"
5. Install the integration
6. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub](https://github.com/dsorlov/snmpPrinter/releases)
2. Extract the `custom_components/snmp_printer` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

### Via UI (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "SNMP Printer"
4. Follow the configuration steps:
   - **Automatic Discovery**: If Home Assistant discovered a printer, you'll see a notification - click Configure to set it up
   - **Manual Configuration**: Enter printer details manually if not discovered

#### Configuration Options

- **IP Address**: Printer's IP address
- **Port**: SNMP port (default: 161)
- **SNMP Version**: v1, v2c, or v3
- **Community String**: SNMP community name (default: public)
- **Update Interval**: How often to poll the printer (default: 60 seconds)

### SNMP v3 Configuration

For SNMP v3, additional security parameters are required:

- **Username**: SNMP v3 username
- **Auth Protocol**: Authentication protocol (MD5 or SHA)
- **Auth Key**: Authentication password
- **Privacy Protocol**: Privacy protocol (DES or AES)
- **Privacy Key**: Privacy password

## Usage

### Monitoring

Once configured, the integration will create a device for your printer with all available sensors. View the device page to see:

- Manufacturer and model information
- Serial number
- Hardware (MAC) address
- Link to printer's web interface (if available)
- All sensor readings

### Automations

Create automations based on printer events:

```yaml
automation:
  - alias: "Low Toner Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.office_printer_black_toner
        below: 20
    action:
      - service: notify.mobile_app
        data:
          message: "Office printer black toner is low!"

  - alias: "Paper Jam Notification"
    trigger:
      - platform: state
        entity_id: sensor.office_printer_status
        to: "jammed"
    action:
      - service: notify.mobile_app
        data:
          message: "Office printer has a paper jam!"
```

## Troubleshooting

### Printer Not Discovered

If your printer is not discovered automatically:

1. Ensure the printer is powered on and connected to the network
2. Verify SNMP is enabled on the printer
3. Check that your printer advertises itself via mDNS/Zeroconf (most network printers do)
4. Try manual configuration instead with the printer's IP address

### No Data or Sensors Unavailable

- Verify the SNMP community string is correct
- Ensure SNMP version matches printer configuration
- Check printer supports standard Printer MIB (RFC 3805)
- Some printers may not support all sensors

### SNMP v3 Issues

- Verify username and passwords are correct
- Ensure auth and privacy protocols match printer configuration
- Some older printers may not fully support SNMP v3

## Localization

I have tried to use machine translation to create a few useable translations. Please correct me if there are any major wrongs or you are missing some languages:

- :uk: English (en.json) - English
- :sweden: Swedish (sv.json) - Svenska
- :denmark: Danish (da.json) - Dansk
- :norway: Norwegian (no.json) - Norsk
- :finland: Finnish (fi.json) - Suomi
- :de: German (de.json) - Deutsch
- :netherlands: Dutch (nl.json) - Nederlands
- :es: Spanish (es.json) - Español
- :fr: French (fr.json) - Français

## Supported Printers

This integration uses standard Printer MIB (RFC 3805) and should work with most network printers from:

- Brother
- Canon
- HP
- Konica Minolta
- Kyocera
- Lexmark
- OKI
- Panasonic
- Ricoh
- Samsung
- Sharp
- Xerox

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- :bug: [Report a Bug](https://github.com/dsorlov/snmpPrinter/issues)
- :bulb: [Request a Feature](https://github.com/dsorlov/snmpPrinter/issues)
- :book: [Documentation](https://github.com/dsorlov/snmpPrinter)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
