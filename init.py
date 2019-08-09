import xlrd
import json
import db_interactor
import re
import traceback


def main(file, config_file):
    try:
        wb = xlrd.open_workbook(file)
        sheet = wb.sheet_by_index(0)
        begin_parse(sheet, config_file)

    except Exception as e:
        traceback.print_exc()
        raise e


"""
method to parse through the an excel sheet and add data to the database
"""
def begin_parse(sheet, config_file):
    db = db_interactor.DBInteractor()
    form_response = {}
    for row in range(1, sheet.nrows):
        for col in range(0, sheet.ncols, 3):
            value = sheet.cell_value(row, col + 2)
            if type(value) is float:
                value = int(value)
            form_response[sheet.cell_value(row, col)] = value
        config = fill_config(form_response, config_file)
        db.update(config)


"""
helper method to fill the config with data from excel sheet
"""
def fill_config(form_response, config_file):
    with open(config_file) as config_data:
        # loads config.JSON to map questions to cols
        config = json.load(config_data)
        # enter entry into map
        for key in config:
            entry = config[key]
            # for each identifier check for derived identifiers
            for identifier in entry["identifiers"]:
                if not identifier["derived"]:
                    identifier["value"] = str(format_val(identifier, form_response))
                else:
                    for question in identifier['questions']:
                        question['value'] = str(format_val(question, form_response))

            for col in entry["cols"]:
                col["value"] = format_val(col, form_response)
        return config


"""
helper method to format any values to specified regexes
"""
def format_val(col, form_response):
    val = form_response[col["question"]]
    # if necessary set up commas to be escaped
    if col['escape_commas']:
        val = re.sub(r",", "\,", val)
    # splits question if necessary
    if "cut_commas" in col.keys():
        sections = re.split(r"(?<!\\),", val)
        val = ""
        # recreates answer
        for section in range(len(sections)):
            if section not in col["cut_commas"]:
                val += sections[section] + ', '
        val = val[0:len(val) - 2]
    if type(val) == str:
        # remove apostrophes
        val = re.sub(r'\'', "''", val)
        val = re.sub(r'\s*-\s*', " ", val)
    return val
