import argparse
from dotenv import load_dotenv
from db import connect_to_db


PREFIX = "INPEDIV"

# create index for column with index_name
def create_index_for_sql_table(table_name, column_name):
    return """
    CREATE INDEX {}_index ON {}({})
    """.format(
        column_name, table_name, column_name
    )


# drop index for column with index_name and table_name
def drop_index_for_sql_table(table_name, column_name):
    return """
    ALTER TABLE {} DROP INDEX {}_index 
    """.format(
        table_name, column_name
    )


def get_column_names_of_sql_table_query(table_name):
    return """
    SELECT column_name FROM information_schema.columns WHERE table_name = '{}'
    """.format(
        table_name
    )


def main(prefix=PREFIX, drop=False):

    table_name = "{}_predictions".format(prefix)
    load_dotenv()
    db_connection = connect_to_db()
    db_cursor = db_connection.cursor()

    non_species_columns = ["id", "record_id", "start_time", "end_time", "channel"]
    db_cursor.execute(get_column_names_of_sql_table_query(table_name))
    result = db_cursor.fetchall()
    for i in result:
        column = i[0]
        if column in non_species_columns:
            continue
        print("{} index for column: {}".format("Drop" if drop else "create", column))
        try:
            if drop:
                db_cursor.execute(drop_index_for_sql_table(table_name, column))
            else:
                db_cursor.execute(create_index_for_sql_table(table_name, column))
            db_connection.commit()
        except Exception as e:
            print(e)

    return


def parse_boolean(value):
    value = value.lower()

    if value in ["true", "yes", "y", "1", "t"]:
        return True
    elif value in ["false", "no", "n", "0", "f"]:
        return False

    return False


if __name__ == "__main__":
    # read commandline arguments is prefix and drop flag
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix")
    parser.add_argument(
        "--drop",
        type=parse_boolean,
        default=False,
        help="Flag for dropping not creating index.",
    )
    args = parser.parse_args()
    main(prefix=args.prefix, drop=args.drop)
