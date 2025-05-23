# Salesforce to HubSpot Metadata Sync (sf2hs)

A Python-based CLI tool for managing Salesforce metadata. It allows you to list and save Salesforce object fields, validate configurations, and synchronize field metadata to HubSpot properties. This tool is designed to assist with migrating or integrating Salesforce data with HubSpot by providing insights into Salesforce object structures and facilitating the setup of corresponding HubSpot properties.

## Features

- Synchronize Salesforce fields to HubSpot properties
- Configuration-based field mapping
- Support for multiple Salesforce objects
- CLI interface for easy operation
- Configurable sync settings

## Setup

### Prerequisites

*   Python 3.8 or higher.
*   (Recommended) A Python virtual environment.
    *   Create one using: `python -m venv .venv`
    *   Activate it:
        *   macOS/Linux: `source .venv/bin/activate`
        *   Windows: `.\.venv\Scripts\activate`

### Installation

1.  **Ensure you have cloned the repository and navigated to its root directory.**
2.  **Install dependencies:**
    ```bash
    pip install .
    ```

### Configuration

The tool requires two main types of configuration: environment variables for credentials and a YAML file for application settings.

1.  **Environment Variables (Credentials):**

    Salesforce and HubSpot credentials should be securely stored as environment variables. This tool supports loading these from a `.env` file.

    *   **Create a `.env` file:** Copy the example file:
        ```bash
        cp .env.example .env
        ```
    *   **Edit the `.env` file** to include your actual credentials:
        ```env
        SF_USERNAME="your_salesforce_username"
        SF_PASSWORD="your_salesforce_password"
        SF_SECURITY_TOKEN="your_salesforce_security_token"
        HUBSPOT_API_KEY="your_hubspot_api_key"
        # SF_INSTANCE_URL="https://your-domain.my.salesforce.com" # Optional: if not using default login.salesforce.com
        ```
    *   The tool will automatically load variables from a `.env` file in the current working directory. Alternatively, you can specify a path to a `.env` file using the `--env-file` option with any command (e.g., `sf2hs list-fields --env-file /path/to/your/.env ...`).

2.  **Application Configuration (YAML):**

    This file defines Salesforce instance details (if not using the default login URL), object mappings for synchronization, and other operational settings.

    *   **Copy the default configuration template:**
        ```bash
        cp config/default_config.yaml config/my_config.yaml
        ```
    *   **Modify `my_config.yaml`** according to your needs. This includes specifying which Salesforce objects to work with, how their fields map to HubSpot properties, and any custom settings for the synchronization process.
    *   This configuration file is passed to most commands using the `--config` option (e.g., `sf2hs sync --config config/my_config.yaml ...`).

## Usage / Commands

The general pattern for using the tool is:
```bash
sf2hs <command> [options]
```

All commands accept an `--env-file` option to specify the path to a `.env` file for loading credentials (e.g., `--env-file .env`). If not provided, the tool looks for a `.env` file in the current directory.

### `list-fields`

Lists available fields for a specified Salesforce object, showing details like field name, label, type, and migratability. This helps in understanding the data structure of an object before configuring synchronization.

*   **Usage Example:**
    ```bash
    sf2hs list-fields --object Account --env-file .env --config config/my_config.yaml --hide-non-migratable
    ```
*   If `--config` is not provided, the command attempts to use default Salesforce connection parameters (e.g., instance URL from environment variables if set). By default, it shows all fields. Use `--hide-non-migratable` to view only fields typically suitable for migration.

### `save-fields`

Retrieves and saves fields for one or more Salesforce objects to a file. This is useful for documentation, offline analysis, or as a basis for creating field mappings. Supports output in Excel (default) or JSON formats.

*   **Usage Examples:**
    *   Save fields for a specific object (`Account`) to a JSON file (showing all fields by default):
        ```bash
        sf2hs save-fields --object Account --output account_fields.json --format json --env-file .env
        ```
    *   Save fields for all objects defined in `my_config.yaml` to an Excel file (showing all fields by default):
        ```bash
        sf2hs save-fields --config config/my_config.yaml --output all_object_fields.xlsx --env-file .env
        ```
*   By default, all fields are included (`--show-all`). Use `--hide-non-migratable` to filter out fields not typically suitable for migration.

### `validate`

Validates the syntax of the YAML configuration file (`--config`) and checks connectivity and authentication with Salesforce. If HubSpot integration details are configured, it may also check HubSpot connectivity. This command is crucial for ensuring your setup is correct before attempting a synchronization.

*   **Usage Example:**
    ```bash
    sf2hs validate --config config/my_config.yaml --env-file .env
    ```

### `sync`

Synchronizes Salesforce fields to HubSpot properties based on the mappings and settings defined in the specified configuration file. This is the core command for performing the metadata transfer.

*   **Usage Example (syncing a specific object):**
    ```bash
    sf2hs sync --config config/my_config.yaml --object Account --env-file .env
    ```
*   The `--object` option specifies which Salesforce object's configured mappings should be processed for synchronization.

## Development

This section is for anyone looking to contribute to `sf2hs` or modify the tool for their own purposes. We welcome your contributions!

### Setting up a Development Environment

1.  **Create and activate a virtual environment:** (Recommended)
    *   `python -m venv .venv`
    *   `source .venv/bin/activate` (macOS/Linux) or `.\.venv\Scripts\activate` (Windows)
2.  **Ensure you have cloned the repository and navigated to its root directory.**
3.  **Install development dependencies:**
    ```bash
    pip install -e ".[dev]"
    ```
    This will install the tool in editable mode along with all dependencies needed for development and testing.

### Running Tests

We use `pytest` for testing and `pytest-cov` for coverage.

*   **Run all tests:**
    ```bash
    pytest
    ```
*   **Run tests with coverage report:**
    ```bash
    pytest --cov=src/sf2hs tests/
    ```
    (Adjust the path to `src/sf2hs` if your source layout is different. The `tests/` argument specifies where to find the tests.)

### Code Quality & Formatting

To maintain code quality and consistency, we use the following tools. Please run these before committing your changes:

*   **Black (Formatter):**
    ```bash
    black .
    ```
*   **isort (Import Sorter):**
    ```bash
    isort .
    ```
*   **Ruff (Linter):**
    ```bash
    ruff check .
    ```
*   **MyPy (Static Type Checker):**
    ```bash
    mypy src
    ```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
