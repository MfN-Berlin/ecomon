import xlsxwriter
import json


def write_execl_file(filepath, rows, header):
    # load olaf_id.json file into dictionary
    olaf_id_list = json.load(open("./assets/olaf8_id.json"))
    olaf_id_dict = {}
    for entry in olaf_id_list:
        olaf_id_dict[entry["latin_name"].lower().replace(" ", "_")] = entry["olaf8_id"]
    # which is the filename that we want to create.
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
                if header_val[1] == "filename":
                    worksheet.write_url(
                        row_index + 1,
                        col_index,
                        "./{}".format(row[header_val[1]]),
                        string=row[header_val[1]],
                    )
                    continue
                if header_val[0] == "SpeciesCode":
                    worksheet.write(
                        row_index + 1,
                        col_index,
                        olaf_id_dict[row[header_val[1]].lower().replace(" ", "_")],
                    )
                    continue
                worksheet.write(row_index + 1, col_index, row[header_val[1]])
    workbook.close()

