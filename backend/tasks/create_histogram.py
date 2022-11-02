import decimal
import xlsxwriter
from sql.query import count_species_over_threshold_in_date_range
from sql.query import update_job_status, update_job_progress
from datetime import datetime, timezone

from util.tools import species_row_to_name


def float_range(start, stop, step):
    while start < stop:
        yield float(start)
        start += decimal.Decimal(step)


def write_execl_file(filepath, rows, header):

    workbook = xlsxwriter.Workbook(filepath)

    # The workbook object is then used to add new
    # worksheet via the add_worksheet() method.
    worksheet = workbook.add_worksheet()
    # Iterate over the data and write it out row by row.
    for index, value in enumerate(header):
        worksheet.write(0, index, value[0])
        worksheet.set_column(index, index, len(value[0]))
    for row_index, row in enumerate(rows):
        for col_index, header_val in enumerate(header):
            if header_val[1] is not None:
                worksheet.write(row_index + 1, col_index, row[header_val[1]])
    workbook.close()


async def create_histogram(
    database,
    collection_name,
    start_datetime,
    end_datetime,
    species,
    bin_width,
    result_filepath,
    job_id,
):
    species_list = [species] if species != None else []
    steps = list(float_range(0, 1, bin_width))
    print(steps)
    steps.reverse()
    print(steps)
    total_steps = len(steps) * len(species_list)
    counter = 0
    result_list = []
    # Create headers for excel file
    header = [
        (">= Threshold", "threshold_min"),
        ("< Threshold", "threshold_max"),
    ]
    for species_id in species_list:
        name = species_row_to_name(species_id)
        header.append(
            ("{} Accumulative".format(name), "{}_predictions_acc".format(species_id),)
        )
        header.append(
            ("{} Count".format(name), "{}_predictions_count".format(species_id))
        )
    # Create rows for excel file
    for idx, threshold_min in enumerate(steps):
        # print("Get prediction count for ", threshold_min)
        row = {
            "threshold_min": threshold_min,
            "threshold_max": threshold_min + bin_width,
        }
        for species_id in species_list:
            query = count_species_over_threshold_in_date_range(
                collection_name,
                species_id,
                threshold_min,
                1,
                datetime.fromisoformat(start_datetime[:-1]).replace(
                    tzinfo=timezone.utc
                ),
                datetime.fromisoformat(end_datetime[:-1]).replace(tzinfo=timezone.utc),
            )
            prediction_count = (await database.fetch_one(query))[0]
            row["{}_predictions_acc".format(species_id)] = prediction_count
            row["{}_predictions_count".format(species_id)] = (
                prediction_count
                - result_list[idx - 1]["{}_predictions_acc".format(species_id)]
                if idx > 0
                else prediction_count
            )

            counter = counter + 1
            result_list.append(row)
            await database.execute(
                update_job_progress(job_id, round(counter / total_steps * 100))
            )

    write_execl_file(
        result_filepath, result_list, header,
    )
    await database.execute(update_job_status(job_id, "done"))

