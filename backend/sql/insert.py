from sympy import periodic_argument


def insert_record(prefix, filepath, filename, record_datetime, duration, channels):
    return """INSERT INTO {}_records
VALUES (null, '{}', '{}', '{}', {}, {});""".format(
        prefix, filepath, filename, record_datetime, duration, channels
    )


def insert_prediction(prefix, record_id, start_time, end_time, channel, predictions):
    prediction_list = ",".join([str(x) for x in predictions])
    return """INSERT INTO {}_predictions VALUES (null,{}, {}, {}, {}, {})
    """.format(
        prefix, record_id, start_time, end_time, channel, prediction_list
    )

