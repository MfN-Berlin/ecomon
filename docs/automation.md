# Automation

Automation is controlled through Airflow. The Airflow UI can be accessed at: http://localhost/ecomon_next/airflow

## PostgreSQL Backup DAG

### Overview
The `postgres_weekly_backup` DAG performs automated weekly backups of the PostgreSQL database with compression and rotation management.

### Schedule
- **Frequency**: Weekly (every Sunday at 03:00 AM)
- **Max Active Runs**: 1 (prevents overlapping backup operations)

### Tasks

#### 1. Create Backup (`create_backup`)
- **Type**: BashOperator (NoTemplateBashOperator)
- **Script**: `/opt/airflow/dags/scripts/backup_pg.sh`
- **Function**:
  - Executes `pg_basebackup` to create a physical backup of the PostgreSQL database
  - Creates a timestamped backup directory: `basebackup_YYYY-MM-DD_HH-MM-SS`
  - Stores the timestamp in `$PGBACKUP_PATH/current_timestamp.txt` for subsequent tasks
  - Logs output to `$PGBACKUP_PATH/backup_YYYY-MM-DD_HH-MM-SS.log`
- **Configuration**:
  - Uses environment variables: `PGBACKUP_PATH`, `PG_USER`, `PG_PASSWORD`, `PG_HOST`, `PG_PORT`, `PG_DATABASE`
  - Backup location: `$PGBACKUP_PATH` directory on the host (mounted on `/backup` in the container)
  - Format: Plain format with streaming WAL

#### 2. Compress Backup (`compress_backup`)
- **Type**: BashOperator (NoTemplateBashOperator)
- **Function**:
  - Reads the timestamp from the previous task
  - Compresses the backup directory into a `.tar.gz` archive
  - Removes the original uncompressed backup directory to save space
- **Output**: `$PGBACKUP_PATH/basebackup_YYYY-MM-DD_HH-MM-SS.tar.gz`

#### 3. Rotate Backups (`rotate_backups`)
- **Type**: BashOperator (NoTemplateBashOperator)
- **Function**:
  - Lists all existing backup archives sorted by date (newest first)
  - Keeps only the `MAX_BACKUPS` most recent backups
  - Deletes older backups to manage disk space
  - Cleans up the temporary timestamp file
- **Configuration**: Uses `MAX_BACKUPS` environment variable (default: 2)

### Task Dependencies
After the backup is terminated, the file should be downloaded from the server and stored in a safe location ("Z"). To manually copy the backup, do `rsync -P denbi-gpu:source-path destination-path-on-Z` where denbi-gpu is your SSH configuration to connect to the server. Make sure there is enough space on destination-path-on-Z.

## Create Report DAG

### Overview
The `create_report` DAG generates a comprehensive workflow status report that tracks the data processing pipeline from raw WAV files through database import to BirdNET model inference. This report provides visibility into data flow, processing status, and potential bottlenecks across all monitoring sites.

### Schedule
- **Frequency**: Daily at 03:00 AM
- **Catchup**: Disabled (only runs for current date)

### Purpose
The DAG creates a daily snapshot of the system's data processing status by:
1. Scanning file system for WAV files
2. Comparing file counts with database records
3. Tracking BirdNET model inference progress
4. Identifying processing bottlenecks and data discrepancies
5. Storing historical reports for trend analysis

### Tasks

#### 1. Get Sites from Database (`get_sites_from_db`)
- **Type**: Python task
- **Function**: Fetches all site IDs and prefixes from the `sites` table
- **Output**: List of dictionaries with `site_id` and `prefix`

#### 2. Create Report Table (`create_report_table`)
- **Type**: Python task
- **Function**:
  - Creates the `workflow_reports` table if it doesn't exist
  - Defines schema with columns for all workflow metrics
  - Creates indexes on `report_date`, `site_id`, and `prefix` for query performance
- **Table Schema**:
  - `id`: Primary key
  - `report_date`: Timestamp of report generation
  - `prefix`: Site prefix (e.g., "TEST")
  - `site_id`: Foreign key to sites table
  - `wav_size_bytes`: Total size of WAV files in bytes
  - `wav_count`: Number of WAV files
  - `record_count`: Number of database records
  - `db_import`: Import status ("ready", "ready with losses", "pending", or empty)
  - `birdid_medium_processed`: Count of records processed by BirdNET
  - `birdid_medium`: BirdNET processing status
  - `birdid_medium_visible`: Count of records with max confidence scores (visible in UI)
  - `visible_in_ui`: Boolean flag for UI visibility
  - `created_at`: Record creation timestamp

#### 3. Get Record Counts (`get_record_counts_from_db`)
- **Type**: Python task
- **Function**: Queries the `records` table to count imported records per site
- **Output**: Dictionary mapping `site_id` to record count

#### 4. Get BirdNET Processed Counts (`get_birdid_medium_processed_counts`)
- **Type**: Python task
- **Function**:
  - Counts unique records that have been processed by BirdNET (model_id=3)
  - Queries `model_inference_logs` table
- **Output**: Dictionary mapping `site_id` to processed record count

#### 5. Get BirdNET Visible Counts (`get_birdid_medium_visible_counts`)
- **Type**: Python task
- **Function**:
  - Counts records with max confidence scores (visible in UI)
  - Queries `model_inference_results_max_confidence` table for model_id=3
- **Output**: Dictionary mapping `site_id` to visible record count

#### 6. Get Running Inference Jobs (`get_running_inference_jobs`)
- **Type**: Python task
- **Function**:
  - Identifies sites with currently running BirdNET inference jobs
  - Queries `jobs` table for status='running' and topic='model_inference_site'
  - Extracts site_id from job metadata JSON
- **Output**: Set of site IDs with active inference jobs

#### 7. Create Report (`create_report`)
- **Type**: Python task
- **Function**:
  - Walks the `/data` directory tree
  - Identifies first-level subdirectories (site prefixes)
  - Lists files in each directory
- **Output**: List of dictionaries with directory path, files, and root path

#### 8. List WAV Files (`list_wavs`)
- **Type**: Python task
- **Function**: Counts WAV files (`.wav` extension) in each directory
- **Output**: List with directory, WAV count, and root path

#### 9. Calculate WAV Sizes (`calculate_wav_sizes`)
- **Type**: Python task
- **Function**:
  - Calculates total size of all WAV files per directory
  - Handles file access errors gracefully with warnings
- **Output**: List with directory, WAV count, and total size in bytes

#### 10. Aggregate by Prefix (`aggregate_wav_data_by_prefix`)
- **Type**: Python task
- **Function**:
  - Groups WAV counts and sizes by site prefix
  - Matches prefixes to site IDs using the sites lookup
  - Aggregates multiple subdirectories under the same prefix
- **Output**: List of aggregated data per prefix with site_id

#### 11. Calculate Import Statuses (`calculate_import_statuses`)
- **Type**: Python task
- **Function**:
  - Calculates `db_import` status by comparing WAV count to record count
  - Calculates `birdid_medium` status by comparing record count to processed count
  - Status logic:
    - **Empty**: No records in database
    - **"ready"**: Counts match exactly (difference = 0)
    - **"ready with losses"**: Difference ≤ 10 files
    - **"pending"**: Difference > 10 files
    - **"running"**: Active inference job detected
- **Configuration**: `MAX_DIFF = 10` (acceptable difference threshold)
- **Output**: Enriched data with status fields

#### 12. Transform Data (`transform_data`)
- **Type**: Python task
- **Function**:
  - Converts list to pandas DataFrame
  - Orders columns for consistent output
  - Sorts by prefix alphabetically
- **Output**: Sorted DataFrame

#### 13. Print Report (`print_report`)
- **Type**: Python task
- **Function**:
  - Logs detailed report to Airflow logs
  - Formats file sizes in MB
  - Shows all metrics per site
- **Output**: Log entries (no return value)

#### 14. Save Report to Database (`save_report_to_db`)
- **Type**: Python task
- **Function**:
  - Deletes today's existing report (prevents duplicates on re-runs)
  - Cleans up reports older than 30 days
  - Inserts new report rows into `workflow_reports` table
  - One row per site/prefix
- **Output**: Count of rows inserted
