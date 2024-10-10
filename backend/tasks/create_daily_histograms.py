import decimal
import xlsxwriter
import pytz
from sql.query import get_predictions_in_date_range
from sql.query import update_job_status, update_job_progress
from datetime import datetime, timedelta, timezone

from util.tools import species_row_to_name
from logging  import getLogger
logger = getLogger(__name__)

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


async def create_daily_histograms(
    database,
    collection_name,
    start_datetime,
    end_datetime,
    species,
    bin_width,
    result_filepath,
    job_id,
    request_timezone="UTC",
    min_threshold=None,
    max_threshold=None,
):
    request_start_datetime = datetime.fromisoformat(start_datetime[:-1]).replace(
        tzinfo=timezone.utc
    )
    request_end_datetime = datetime.fromisoformat(end_datetime[:-1]).replace(
        tzinfo=timezone.utc
    )
    request_timezone = pytz.timezone(request_timezone)
    steps = list(float_range(0, 1, bin_width))
    steps_count = len(steps)
    # Create headers for excel file
    header = [("Record date", "record_date")]
    # calc decimal places of bin width
    bin_width_str = str(bin_width)
    if "." in bin_width_str:
        decimal_places = len(str(bin_width).split(".")[1])
    else:
        decimal_places = 0

    name = species_row_to_name(species)
    for index, step in enumerate(steps):
        header.append(
            (
                f"{round(step, decimal_places)} <= x < {round(step + bin_width, decimal_places)}",
                f"bin_{index}",
            )
        )
    # Get predictions from database

    query = get_predictions_in_date_range(
        collection_name,
        species,
        request_start_datetime,
        request_end_datetime,
        min_threshold=min_threshold,
        max_threshold=max_threshold,
    )
    predictions = await database.fetch_all(query)
    days = {}
    for prediction in predictions:
        record_datetime = (
            prediction[0].replace(tzinfo=timezone.utc).astimezone(request_timezone)
        )
        date = record_datetime.date()
        if date not in days:
            # create list of bin counts
            days[date] = [0] * steps_count
        days[date][int(prediction[2] / bin_width)] += 1

    # make days to list and sort by keys
    await database.execute(update_job_progress(job_id, 50))
    rows = []
    for record_date, bins in sorted(days.items(), key=lambda x: x[0]):
        row = {}
        row["record_date"] = record_date
        for index, bin_count in enumerate(bins):
            row[f"bin_{index}"] = bin_count
        rows.append(row)
    logger.debug(f"Rows: {rows}")
    await database.execute(update_job_progress(job_id, 80))
    write_execl_file(result_filepath, rows, header)
    await database.execute(update_job_progress(job_id, 100))
    await database.execute(update_job_status(job_id, "done"))

