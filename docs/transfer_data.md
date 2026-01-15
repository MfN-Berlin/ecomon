# Transfer data from another instance of Ecomon

Once a new instance of Ecomon has been setup (see: INSTALL_DEV.md, INSTALL_PRID.md), you might want to transfer existing data into it.

1. Make a binary backup of the original database
```
pg_basebackup -Uecomon -D /path/to/backup/directory -P
```

2. If in a production environment, point the environment variable PGDATA_PATH in .env to the binary backup.

3. Start the containers for the new Ecomon instance. The database container should start and keep running, with the data from the backup. Other containers might not start at this point, ignore them for now.

4. Exec into the container where the database is running, open the databse in psql, change the password of the ecomon user to what is set in .env.
```
docker exec -ti database-container bash
psql -Umy_user -decomon
\du
ALTER USER my_user WITH PASSWORD 'new_password';
```
* 'my_user' shuld correspond with DB_USERNAME as set in .env.
* 'new_password' should correspond to DB_PASSWORD as set in .env.

5. Restart the containers. Now all containers should run.


# Transfer inference data from another instance of ecomon

**export_model_inference_results.sh**

The script scripts/export_model_inference_results.sh exports inference results of a given location and model(s) to CSV. Then use psql to import the CSV into the new database. See inline documentation in the script for examples.

**export_model_inference_logs.sh**

The script scripts/export_model_inference_logs.sh exports model inference logs from a PostgreSQL database to a CSV file for a specific site. It accepts command-line arguments to connect to either a local PostgreSQL database or one running in a Docker container, specifying credentials, database name, and the target site ID. The script then queries the database and exports the results to a CSV file.

**export_mir_max_confidence.sh**

This script exports the maximum confidence values from model inference results max confidence table for a specific site to a CSV file. It allows users to specify connection details for a PostgreSQL database, either locally or within a Docker container, using command-line arguments. The script processes these arguments, connects to the database, and generates a CSV file containing the desired data.
