# Batch Audiofile Inferencing
Use script to analyze big collections auf recordings

## Packages needed:
```bash
pip3 install tqdm
pip3 install python-dotenv
# if you have problems with mariadb try to install first
# sudo apt-get install libmariadbclient-dev
pip3 install mariadb

```


## HOW TO USE
1. clone repository
2. copy .env-default to .env
3. change enviroment variables in .env as you like
4. start database with `docker-compose up`
   
# MARIABDB - MYSQLWORCKBENCH
If you have problems to connect to MARIADB because of SSL required 
got to Advanced Tab in the connection dialog and add
```
useSSL=0
```