import mariadb
import sys
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Read database credentials from environment variables
DB_HOST = os.getenv("MARIADB_HOST")
DB_PORT = int(os.getenv("MARIADB_PORT"))
DB_NAME = os.getenv("MARIADB_DATABASE")
DB_USER = os.getenv("MARIADB_USER")
DB_PASSWORD = os.getenv("MARIADB_PASSWORD")

columns = [
    "grus_grus",
    "ardea_cinerea",
    "strix_aluco",
    # "dendrocoptes_medius",
    "dendrocopos_major",
    "lophophanes_cristatus",
    "phylloscopus_sibilatrix",
    "phylloscopus_trochilus",
    "phylloscopus_collybita",
    "locustella_luscinioides",
    "sylvia_atricapilla",
    "regulus_ignicapilla",
    "troglodytes_troglodytes",
    "turdus_merula",
    "turdus_philomelos",
    "turdus_viscivorus",
    "erithacus_rubecula",
    "luscinia_luscinia",
    "phoenicurus_ochruros",
    "phoenicurus_phoenicurus",
    "fringilla_coelebs",
]

# Connect to MariaDB database
print("Start Add Indices Script")
try:
    conn = mariadb.connect(
        user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME
    )
    cur = conn.cursor()

    # Get a list of tables ending with '_predictions'
    cur.execute("SHOW TABLES LIKE '%_predictions'")
    tables = [row[0] for row in cur.fetchall()]
    print(f"Found {len(tables)} tables")
    # Loop through tables and columns to add indexes
    for table in tables:
        print(f"Adding indices to table {table}")
        for column in columns:
            # Check if column already has an index
            cur.execute(f"SHOW INDEX FROM `{table}` WHERE Column_name = '{column}'")
            index = cur.fetchone()
            if not index:
                print(f"Adding indices to column {column}")
                # Add index to column with a specified index name
                index_name = f"{column}_index"
                cur.execute(
                    f"ALTER TABLE `{table}` ADD INDEX `{index_name}` (`{column}`)"
                )
                conn.commit()
                print(f"Added index to column {column} in table {table}")
            else:
                print(f"Column {column} in table {table} already has an index")

    # Close database connection
    conn.close()
except mariadb.Error as e:
    print(f"Error connecting to MariaDB: {e}")
    sys.exit(1)

