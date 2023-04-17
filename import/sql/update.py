def update_corrupted_file(prefix, filepath):
    return """
    UPDATE {}_records SET corrupted = 0 where filepath = '{}'
    """.format(
        prefix, filepath
    )

def update_record(
    prefix, filepath, duration, channels, corrupted
):
    query = """UPDATE {}_records
    SET duration = {}, channels = {}, corrupted = {}
    WHERE filepath = '{}';
    """.format(
        prefix, duration, channels, corrupted, filepath
    )
    return query