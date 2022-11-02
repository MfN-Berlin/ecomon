import decimal
import xlsxwriter
import pytz
from sql.query import get_predictions_in_date_range
from sql.query import update_job_status, update_job_progress
from datetime import datetime, timedelta, timezone

from util.tools import species_row_to_name


def float_range(start, stop, step):
    while start < stop:
        yield float(start)
        start += decimal.Decimal(step)


def write_execl_file(filepath, rows, header):
    workbook = xlsxwriter.Workbook(filepath, options={"remove_timezone": True})
    # The workbook object is then used to add new
    # worksheet via the add_worksheet() method.
    worksheet = workbook.add_worksheet()
    # Iterate over the data and write it out row by row.
    date_format = workbook.add_format({"num_format": "d.mmm"})
    datetime_format = workbook.add_format({"num_format": "yy/mm/dd hh:mm:ss"})
    for index, value in enumerate(header):
        worksheet.write(0, index, value[0])
        worksheet.set_column(index, index, len(value[0]))
    for row_index, row in enumerate(rows):
        for col_index, header_val in enumerate(header):
            if header_val[1] is not None:
                if header_val[1] == "record_date":

                    worksheet.write_datetime(
                        row_index + 1, col_index, row[header_val[1]], date_format
                    )
                else:
                    if header_val[1] == "record_datetime":
                        worksheet.write_datetime(
                            row_index + 1,
                            col_index,
                            row[header_val[1]],
                            datetime_format,
                        )

                    else:
                        worksheet.write(row_index + 1, col_index, row[header_val[1]])
    workbook.close()


async def create_predictions(
    database,
    collection_name,
    start_datetime,
    end_datetime,
    species,
    result_filepath,
    job_id,
    request_timezone="UTC",
):
    print("REuested timezone: ", request_timezone)
    print("Start datetime: ", start_datetime)
    print("End datetime: ", end_datetime)
    species_list = (
        species if type(species) == list else [species] if species != None else []
    )
    request_timezone = pytz.timezone(request_timezone)
    result_list = []
    # Create headers for excel file
    header = [
        ("Record date", "record_date"),
        ("Record datetime", "record_datetime"),
    ]
    for species_id in species_list:
        name = species_row_to_name(species_id)
        header.append(("{} confidence".format(name), "{}".format(species_id)))
    print(datetime.fromisoformat(start_datetime[:-1]).replace(tzinfo=timezone.utc))
    print(datetime.fromisoformat(end_datetime[:-1]).replace(tzinfo=timezone.utc))
    query = get_predictions_in_date_range(
        collection_name,
        species_list,
        datetime.fromisoformat(start_datetime[:-1]).replace(tzinfo=timezone.utc),
        datetime.fromisoformat(end_datetime[:-1]).replace(tzinfo=timezone.utc),
    )
    predictions = await database.fetch_all(query)

    for prediction in predictions:
        row = {}
        # print(prediction[0])
        record_datetime = prediction[0].replace(tzinfo=timezone.utc)
        # print(prediction[0])
        row["record_date"] = record_datetime.astimezone(request_timezone)
        # print(row["record_date"])
        row["record_datetime"] = (
            record_datetime + timedelta(seconds=round(prediction[1]))
        ).astimezone(request_timezone)

        for index, species_id in enumerate(species_list, 2):
            row["{}".format(species_id)] = prediction[index]
        result_list.append(row)

    await database.execute(update_job_progress(job_id, 100))

    write_execl_file(
        result_filepath, result_list, header,
    )
    await database.execute(update_job_status(job_id, "done"))

