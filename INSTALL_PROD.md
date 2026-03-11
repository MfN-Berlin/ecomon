# Installing an Ecomon instance for development
Instructions for installing Ecomon on a Linux server.

System requirements for production:
* 250GB+ RAM
* 25+ CPU cores
* 2+ GPU
* 8TB on a fast disk to hold the database
* 70TB+ to store audio data and for backups, e.g. on a 3fs storage
* Sudo access

Required software
* CUDA Version: 12.4
* Git
* Docker and Docker-Compose

Clone the repository and checkout the desired branch
```
sudo GIT_SSH_COMMAND='ssh -i path-to-your-id_rsa' git clone git@github.com:MfN-Berlin/ecomon.git ecomon_validate
sudo chown -R "$USER":akwamo ecomon_validate
cd ecomon_validate
git checkout ecomon_validate
```

Make a copy of the environment variables file for development
```
cp env-default .env
```

Open the `.env` file in an editor and set at least:
* DB_NAME=ecomon
* DB_PASSWORD=secure-password
* DB_ROOT_PASSWORD=secure-password
* BASE_DATA_DIRECTORY=path-to-audio-dir  # needs 50TB+, e.g. on 3fs storage
* PGBACKUP_PATH=path-to-backup-dir  # needs 20TB+, e.g. on 3fs storage
* SUB_PATH=/ecomon_validate
* PGDATA_PATH=path-to-custom-place-for-database-data  # important: db needs 8TB+ on fast disk
* AIRFLOW_ADMIN_PASSWORD=secure-password
* HASURA_ADMIN_SECRET=secure-password
* HASURA_URL=pdefault-docker-compose-gateway (typically 172.17.0.1:10080/v1/graphql, used by Dashboard)
* USE_GPU=1  # 1, 2, or all

You might need to set in .env and/or docker-compose.production.yaml:
* Port to dashboard service in docker-compose.production.yaml

Start Docker containers
```
docker compose -f docker-compose.production.yaml up -d
```
This should start these containers:
* ecomon_validate-dashboard-1
* ecomon_validate-airflow-1
* ecomon_validate-db-migrate-1
* ecomon_validate-api-1
* ecomon_validate-traefik-1
* ecomon_validate-worker-1
* ecomon_validate-frontend-1
* redis-validate
* ecomon_validate-graphql-engine-1
* ecomon_validate-db-1

And these networks:
* ecomon_validate_ecomon
* ecomon_validate_traefik-ingress
