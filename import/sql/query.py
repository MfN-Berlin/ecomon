
def get_record_id_by_filepath(prefix, filepath):
    return """
    SELECT id from {}_records where filepath = '{}'
    """.format(
        prefix, filepath
    )

def create_index_for_sql_table(table_name: str, column_name: str):
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
def get_corrupted_files(prefix):
    return """
    SELECT filepath from {}_records where corrupted = 1
    """.format(
        prefix)

def get_record_id(prefix, filepath):
    return """
    SELECT id from {}_records where filepath = '{}'
    """.format(
        prefix, filepath
    )