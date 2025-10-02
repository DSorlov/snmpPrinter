# Contributing to SNMP Printer Integration

Thank you for your interest in contributing to the SNMP Printer integration!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/dsorlov/snmpPrinter.git
cd snmpPrinter
```

2. Install Home Assistant development environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate
pip install homeassistant
```

3. Link the integration to your Home Assistant config directory:
```bash
ln -s $(pwd)/custom_components/snmpPrinter ~/.homeassistant/custom_components/snmpPrinter
```

## Testing

Test your changes with a real printer:

1. Enable SNMP on your printer (consult printer manual)
2. Restart Home Assistant
3. Add the integration through the UI
4. Verify all sensors are working correctly

## Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to all functions and classes
- Keep functions focused and small

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Reporting Bugs

Use the GitHub issue tracker to report bugs. Include:

- Home Assistant version
- Integration version
- Printer model and manufacturer
- SNMP version used
- Detailed description of the issue
- Relevant log entries

## Feature Requests

Feature requests are welcome! Please provide:

- Clear description of the feature
- Use case and benefits
- Any relevant examples from other integrations

## Code of Conduct

Be respectful and constructive in all interactions.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
