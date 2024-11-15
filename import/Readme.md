#Analyse Audio Data and import it into the Webinterface


## Audio Data Import Configuration Generator

This script is designed to generate YAML configuration files for importing audio data using Jinja2 templates. It allows you to specify a prefix, year, and model to customize the configuration files. The script can generate a single configuration file or multiple files based on subfolders within a specified directory.

### Script Parameters

- `--prefix`: The prefix to use in the configuration. This is required unless the `--folder` option is specified.
- `--year`: The year to use in the configuration. This is required unless the `--folder` option is specified.
- `--model`: The model to use in the configuration. This is a required parameter and must be either `birdid` or `birdnet`.
- `--folder`: Path to a folder. If specified, the script will generate configuration files for each subfolder, using the subfolder name as the prefix.
- `--output`: The output folder where the generated configuration files will be saved. This is a required parameter.

### Usage Example

To generate a single configuration file for importing audio data:
```bash
python generate_config.py --prefix AKWAMO0304A --year 2024 --model birdid --output ./config

# or to generate configuration files for all subfolders in a directory:
python generate_config.py --model birdid --output ./config/akwamo --year 2024 --folder /mnt/akwamodata/

```

# Create Reports Script

This script is designed to generate reports from a ecomon database, summarizing records  from specified prefiox. It supports both text and JSON output formats and can utilize multiple CPU cores for parallel processing.

## Features

- Generates reports for specified prefix records.
- Supports both text and JSON output formats.
- Utilizes multiple CPU cores for faster processing.
- Customizable through command-line arguments.

## Prerequisites

- Python 3.x
- PostgreSQL database
- Required Python packages (see below)

## Installation
1. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

   Ensure your `requirements.txt` includes:
   - `psycopg2`
   - `pandas`
   - `tqdm`
   - `python-dotenv`
   - `pytz`

2. Set up your environment variables in a `.env` file:

   ```plaintext
   POSTGRES_USER=your_db_user
   POSTGRES_PASSWORD=your_db_password
   POSTGRES_DATABASE=your_db_name
   POSTGRES_HOST=your_db_host
   POSTGRES_PORT=your_db_port
   DATA_DIRECTORY=your_data_directory
   REPORTS_DIRECTORY=your_reports_directory
   ```

## Usage

Run the script using the following command:

```bash
python import/create_reports.py [options]
```
### Options

- `--collection_prefix`: Specify the collection/prefix name (optional).
- `--prefix_includes`: Filter collections/prefixes that include this string (optional).
- `--output_format`: Choose the output format (`text` or `json`). Default is `json`.
- `--cores`: Number of CPU cores to use for processing. Default is 1.

### Example

Generate a JSON report for a specific collection prefix using 4 CPU cores:
```bash
python import/create_reports.py --collection_prefix AKWAMO0304A --output_format json --cores 4
```

# Create Species Events

This script is designed to generate reports for a collection of datasets by creating a maximum predictions table for each dataset. It utilizes PostgreSQL for database operations and supports parallel processing using multiple CPU cores.

## Features

- **Drop Existing Tables**: Drops existing predictions max tables if they exist.
- **Create Predictions Max Table**: Generates a new table with the maximum predictions for each species.
- **Add Index**: Adds an index on the `record_datetime` column for efficient querying.
- **Parallel Processing**: Supports parallel processing using multiple CPU cores to speed up the operation.

## Requirements

- Python 3.x
- PostgreSQL
- Required Python packages: `argparse`, `psycopg2`, `dotenv`, `tqdm`, `logging`, `multiprocessing`

## Setup

1. **Install Python Packages**: Ensure all required Python packages are installed. You can use `pip` to install them:
   ```bash
   pip install psycopg2-binary python-dotenv tqdm
   ```

2. **Environment Variables**: Create a `.env` file in the root directory with your PostgreSQL database credentials:
   ```
   POSTGRES_HOST=your_host
   POSTGRES_USER=your_user
   POSTGRES_PASSWORD=your_password
   POSTGRES_DATABASE=your_database
   POSTGRES_PORT=your_port
   ```

## Usage

Run the script using the following command:

```bash
python import/create_species_events.py [options]
```

- `partial_name`: (Optional) A part of the dataset name to filter which datasets to process.
- `--debug`: (Optional) Enable debug mode for more detailed logging.
- `--cores N`: (Optional) Specify the number of CPU cores to use for processing. Default is 1.

## Example

To process datasets with names containing "example" using 4 CPU cores and enable debug mode:
```bash
python import/create_species_events.py --partial_name akwamo --cores 4 --debug
```

# Species Histogram Generator

This script is designed to generate species histograms from prediction tables in a PostgreSQL database. It creates a histogram table for each dataset, with bins representing the frequency of species predictions within specified ranges.

## Prerequisites

- Python 3.x
- PostgreSQL database
- Required Python packages (listed in `requirements.txt`)

## Installation

1. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the root directory with your database credentials:

   ```plaintext
   POSTGRES_HOST=your_host
   POSTGRES_USER=your_user
   POSTGRES_PASSWORD=your_password
   POSTGRES_DATABASE=your_database
   POSTGRES_PORT=your_port
   ```

## Usage

Run the script using the following command:
```bash
python import/create_species_histograms.py [options]
```

- `partial_name` (optional): A part of the dataset name to filter which datasets to process.
- `--debug`: Enable debug mode for more detailed logging.
- `--cores N`: Specify the number of CPU cores to use for processing. Default is 1.

## How It Works

1. **Database Connection**: The script connects to the PostgreSQL database using credentials from the `.env` file.
2. **Dataset Identification**: It identifies datasets by looking for tables with names ending in `_records`.
3. **Histogram Creation**: For each dataset, it creates a histogram table with bins representing species prediction frequencies.
4. **Parallel Processing**: The script can utilize multiple CPU cores to process datasets in parallel, improving performance on large datasets.
