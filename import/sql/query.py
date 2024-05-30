
def get_record_id_by_filepath(prefix, filepath):
    return """
    SELECT id from {}_records where filepath = '{}'
    """.format(
        prefix, filepath
    )

def create_index_for_sql_table(table_name: str, column_name: str):
    return f"CREATE INDEX {table_name}_{column_name}_index ON {table_name}({column_name})"

# drop index for column with index_name and table_name
def drop_index_for_sql_table(table_name, column_name):
    return f"DROP INDEX {table_name}_{column_name}_index"
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

def get_all_filepaths(prefix):
    return """
    SELECT filepath from {}_records
    """.format(prefix)


