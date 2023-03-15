import mariadb
from tqdm import tqdm
from os import getenv, path
from dotenv import load_dotenv
from util.files import check_audio_file

# create a connection to the MySQL database
load_dotenv()  # load environment variables from .env

root_dir = getenv("MDAS_DATA_DIRECTORY")

cnx = mariadb.connect(
    user=getenv("MDAS_MARIADB_USER"),
    password=getenv("MDAS_MARIADB_PASSWORD"),
    database=getenv("MDAS_MARIADB_DATABASE"),
    host=getenv("MDAS_MARIADB_HOST"),
    port=int(getenv("MDAS_MARIADB_PORT")),
)

# create a cursor object
cursor = cnx.cursor()

# get all tables with the suffix _records
cursor.execute("SHOW TABLES LIKE '%\_records'")
tables = cursor.fetchall()

# iterate over all tables and update them
for table in tables:
    table_name = table[0]

    # add a corrupted column with a boolean flag
    # check if the corrupted column already exists in the table
    cursor.execute("SHOW COLUMNS FROM {} LIKE 'corrupted'".format(table_name))
    column = cursor.fetchone()
    if column is None:
        print("Table {} does not have a column corrupted".format(table_name))
        cursor.execute(
            "ALTER TABLE {} ADD COLUMN corrupted BOOLEAN DEFAULT FALSE".format(
                table_name
            )
        )

    else:
        print("Table {} already has a column corrupted".format(table_name))

    # select all entries in the table
    cursor.execute("SELECT * FROM {}".format(table_name))
    entries = cursor.fetchall()

    # iterate over all entries and check for the wave file in column filepath first 10 entries
    # with tqdm(
    #     total=len(entries), initial=0, desc="Analyzed", unit="files", smoothing=0.1,
    # ) as progress:
    #     for entry in entries:
    #         filepath = entry[1]
    #         # perform the wave file check and write the boolean value in the column corrupted
    #         # join root_dir with filepath
    #         abs_filepath = path.join(root_dir, filepath)
    #         is_corrupted = check_audio_file(abs_filepath)
    #         if is_corrupted:
    #             print("File {} is corrupted".format(abs_filepath))
    #         # else:
    #         #     print("File {} is not corrupted".format(abs_filepath))
    #         cursor.execute(
    #             "UPDATE {} SET corrupted = {} WHERE id = {}".format(
    #                 table_name, is_corrupted, entry[0]
    #             )
    #         )
    #         progress.update(1)

    # commit the changes for the table
    cnx.commit()
    print("Table {} has been updated".format(table_name))

# close the cursor and connection objects
cursor.close()
cnx.close()
