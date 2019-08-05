import json

with open('config.JSON') as config_data:
    config = json.load(config_data)

def add_table():
    pass


def edit_table():
    pass


def add_column():
    pass


def get_existing_tables():

    return config.keys()


def get_table(table):
    pass
