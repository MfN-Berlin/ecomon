import argparse
from dotenv import load_dotenv
from util.db import connect_to_db
from sql.query import (
    create_index_for_sql_table,
    drop_index_for_sql_table,
    get_column_names_of_sql_table_query,
)
from util.tools import parse_boolean

PREFIX = "INPEDIV"

# create index for column with index_name


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
