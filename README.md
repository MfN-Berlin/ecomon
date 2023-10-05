# Batch Audio 'File Inferencing

Use script to analyze big collections auf recordings

# Setup

## Setup Web Service with docker-compose

1. clone repository
2. copy .env-default to .env ans set following variables
   ```bash
   MDAS_MARIADB_PORT=3306                 # port of database
   MDAS_MARIADB_DATABASE=DATABASE_NAME    # database name of the service, It will be created in the docker container
   MDAS_MARIADB_USER=DB_USER              # database user
   MDAS_MARIADB_PASSWORD=dev_password     # password of database user
   MDAS_MARIADB_ROOT_PASSWORD=root_password # root password of the database
   MDAS_DATA_DIRECTORY=/net/              # root directory of monitoring recordings
   MDAS_TMP_DIRECTORY=./runtime-data/backend/tmp # directory for temporary files used for packaging result zip files
   MDAS_SAMPLE_FILES_DIRECTORY=./runtime-data/backend/files # files created from the service
   ```
3. change environment variables in .env
4. start service with `docker-compose up -d`

## How to start dev environment

1. copy .env to backend folder
2. create development python environment
3. install requirements

```bash
pip install --no-cache-dir --upgrade -r /code/requirements.txt
pip install pytz
pip install pyyaml
```

3. start development database with
   `docker-compose -f docker-compose.dev.yaml up -d`
4. change to your python environment and start dev server
   `./run.dev.sh'

## import a collection

A collection should not be to big, One Collection is one station one year.

1. Add following variables to .env file

```bash
MDAS_RESULT_DIRECTORY=/folder/results #folder where result pickle files of the classifier container will be stored
```

2. Adapt the docker-compose file to your needs and to the hardware of the computer. Start the containers with `docker-compose -f filename.yaml up -d`

3. Create a yaml config file with following schema

```yaml
# Folder Path to be relative to MDAS_DATA_DIRECTORY environment variable
recordFolder: # List of directories containing the recordings
   - folder1
   - folder2
fileEnding: # List of file extensions to be analyzed
   - wav
   - WAV
resultFolder: folder # Subdirectory in result folder
indexToNameFile: ./classifier_index_to_name.json # Index to name File of your used classifier
filenameParsing: "ammod" # | "inpediv" # Choose method to parse recording time from file name
prefix: Classifier_Station_Year # Prefix of the created tables in database. Also shows up in frontend. Name is parsed for Classifier, station name and year.
testRun: False # If True no results are save to the database
timezone: CET #Timezone of the datetime information in the filename of the recordings
speciesIndexList: # list of species for which columns a index will be created
   - grus_grus
   - ardea_cinerea
basePort: 9000 # lowest port of classifier containers
analyzeThreads: 6 # how many analyze threads will be instantiated
transformModelOutput: False # Transform output if dimension of classifier output and speciesIndexList miss match
allThreadsUseSamePort: False # if False port number is created else Same port in all threads is used
repeats: 10 # how often the all files are tried to be analyzed
modelOutputStyle: resultDict # if not none this will be added to the classifier request
```

4. Run import script
   import_records.py parameters:
   -  filepath to config yaml file
   -  --create_index if you want to create database species column index
5. If you wan to run more then one import use batch_import.py

# MARIABDB - MYSQLWORCKBENCH

If you have problems to connect to MARIADB because of SSL required
got to Advanced Tab in the connection dialog and add

```
useSSL=0
```
