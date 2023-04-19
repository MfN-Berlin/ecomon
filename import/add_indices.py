import mariadb
import sys
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Read database credentials from environment variables


DB_HOST = os.getenv("MDAS_MARIADB_HOST")
DB_PORT = int(os.getenv("MDAS_MARIADB_PORT"))
DB_NAME = os.getenv("MDAS_MARIADB_DATABASE")
DB_USER = os.getenv("MDAS_MARIADB_USER")
DB_PASSWORD = os.getenv("MDAS_MARIADB_PASSWORD")

columns = [
    "grus_grus",
    "ardea_cinerea",
    "strix_aluco",
    "dendrocoptes_medius",
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
try:
    conn = mariadb.connect(
        user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME
    )
    cur = conn.cursor()
except mariadb.Error as e:
    print(f"Error connecting to MariaDB: {e}")
    sys.exit(1)

# Get a list of tables ending with '_predictions'
cur.execute("SHOW TABLES LIKE '%_predictions'")
tables = [row[0] for row in cur.fetchall()]

# Define the list of columns to check and add indexes to

# Loop through tables and columns to add indexes
for table in tables:
    for column in columns:
        # Check if column already has an index
        cur.execute(f"SHOW INDEX FROM {table} WHERE Column_name = '{column}'")
        index = cur.fetchone()
        if not index:
            # Add index to column
            cur.execute(f"ALTER TABLE {table} ADD INDEX ({column})")
            print(f"Added index to column {column} in table {table}")
        else:
            print(f"Column {column} in table {table} already has an index")
# Close database connection
conn.close()
