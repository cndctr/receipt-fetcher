# GEMINI.md

## Project Overview

This project is a Python command-line tool named `receipt-fetcher`. Its primary purpose is to download e-receipts from various stores, parse the contents of the downloaded PDF, and then export the itemized list into an Excel spreadsheet.

The project is structured into several modules:
- `fetcher.py`: Handles downloading the receipt PDF from a given URL or GUID. It uses a `stores.json` file for configuration and can handle insecure TLS connections for certain hosts.
- `parser.py`: Parses the downloaded PDF file to extract individual items, prices, quantities, and totals. It uses `pdfplumber` for PDF processing.
- `exporter.py`: Takes the parsed receipt data and exports it into an Excel (`.xlsx`) file using `openpyxl`.
- `main.py`: The main entry point for the CLI tool, orchestrating the fetching, parsing, and exporting process.

## Building and Running

This project uses `uv` for dependency management and build processes.

### Installation

To install the necessary dependencies, run:
```bash
uv pip install -r requirements.txt 
# Or based on pyproject.toml
uv pip install -e .
```

### Running the tool

The tool is executed via the `receipt-fetcher` command, which is defined as a project script in `pyproject.toml`.

**Usage:**
```bash
receipt-fetcher <receipt-link-or-guid> [output.xlsx]
```

- `<receipt-link-or-guid>`: The full URL of the e-receipt or just the GUID.
- `[output.xlsx]`: (Optional) The name of the output Excel file. If not provided, it defaults to `<guid>_receipt.xlsx`.

**Example:**
```bash
receipt-fetcher "https://e-check.by/check/1234567890ABCDEF"
```

## Development Conventions

- **Configuration**: Store-specific information (API endpoints, service numbers) is managed in the `stores.json` file.
- **Error Handling**: The `fetcher.py` module includes a custom `UnsafeAdapter` to handle stores with outdated or broken TLS configurations.
- **Modularity**: The application is divided into clear modules for fetching, parsing, and exporting, making it easy to extend or maintain.
- **Dependencies**: Project dependencies are listed in `pyproject.toml` and managed with `uv`.
- **Testing**: TODO: No testing framework is currently set up. Adding tests with a framework like `pytest` would be a valuable improvement.
