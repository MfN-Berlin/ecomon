# Backup data and schemas

current estimate:

    Backup: 6h
    Compress: 12h
    Check 0:30
    Transfer to Z: 3 h

The backup tar is currently 290GB
There are currently 8TB (out of 30TB in total) available on the Z backup drive.

Steps 1,2,3, are automated 1 x week usiong Airflow. The Airflow DAG is in ecomon/airflow/dags/backup_postgres.py.
Step 4 is manual. To manually copy the backup, do rsync -P denbi-gpu:source-path destination-path-on-Z where denbi-gpu is your SSH configuration to connect to the server.