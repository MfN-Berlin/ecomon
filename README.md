# Batch Audiofile Inferencing
Use script to analyze big collections auf recordings

## Packages needed:
```bash
pip3 install tqdm
pip3 install pyyaml
pip3 install python-dotenv
# if you have problems with mariadb try to install first
# sudo apt-get install libmariadbclient-dev
pip3 install mariadb

```


## HOW TO USE
1. clone repository
2. copy .env-default to .env
3. change enviroment variables in .env as you like
4. start database with `docker-compose up -d`
5. run main.py

   
# MARIABDB - MYSQLWORCKBENCH
If you have problems to connect to MARIADB because of SSL required 
got to Advanced Tab in the connection dialog and add
```
useSSL=0
```

## Setup
1. Load image from tar file 
2. 

# How to use Docker Container
## Load docker image
docker load -i birdid-europe254-2103-flask-v03.tar

## Set environment variable of directory with local audio files
DATADIR=/path/to/audio

## Run docker with GPU (use only GPU 0)
docker run -it -p 4001:80 --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=0 -v $DATADIR:/mnt --ipc=host --name birdid --rm birdid-europe254-2103-flask-v03


## Predict birds in file /path/to/audio/file.wav and save results to /path/to/audio/Results
curl "http://localhost:4001/identify?path=/mnt/file.wav&outputDir=/mnt/Results&outputStyle=resultDict"

## Results are saved as dictionary in pkl format
## Open pkl and read dict in python
with open('file.pkl', 'rb') as f:
    resultDict = pickle.load(f)
    
## resultDict format:
resultDict['fileId']
resultDict['modelId']
resultDict['segmentDuration']
resultDict['classIds']
resultDict['classNamesScientific']
resultDict['startTimes']
resultDict['probs']     # Prediction Matrix: nChannels x nSegments x nClasses
