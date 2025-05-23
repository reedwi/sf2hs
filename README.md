# Salesforce to HubSpot Metadata Sync (sf2hs)

A Python-based CLI tool for automating the synchronization of Salesforce metadata to HubSpot properties.

## Features

- Synchronize Salesforce fields to HubSpot properties
- Configuration-based field mapping
- Support for multiple Salesforce objects
- CLI interface for easy operation
- Configurable sync settings

## Installation

```bash
pip install sf2hs
```

## Configuration

1. Copy the default configuration template:
```bash
cp config/default_config.yaml config/my_config.yaml
```

2. Update the configuration with your Salesforce and HubSpot credentials:
   - Set Salesforce credentials via environment variables:
     - `SF_USERNAME`
     - `SF_PASSWORD`
     - `SF_SECURITY_TOKEN`
   - Set HubSpot API key via environment variable:
     - `HUBSPOT_API_KEY`

3. Configure your object mappings in the YAML file

## Usage

### List Available Fields

```bash
sf2hs list-fields --object Account
```

### Validate Configuration

```bash
sf2hs validate --config config/my_config.yaml
```

### Sync Fields

```bash
sf2hs sync --config config/my_config.yaml --object Account
```

## Development

1. Clone the repository
2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

3. Run tests:
```bash
pytest
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
