import csv
import sqlite3

"""
This function imports a CSV (comma delimited) into a SQLite3 DB
Creates a table named: <document_name>
Fills it with the CSV content

args:
    csv_root: Path of the CSV file (example: C:/Documents/example.csv)
    db_root: Path of the database file (example: C:/Documents/my_database.db)
    
"""

def importCSV_inDB(csv_root, db_root):
    csv_file_name = ((csv_root.split('/'))[-1]).split('.')[0]
    if not db_table_exists(csv_file_name):
        # If it does not exist, we create a
        with open(csv_root, "r") as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            headers_db = ''
            db_connection = sqlite3.connect(db_root)
            db_cursor = db_connection.cursor()
            for i, csv_line in enumerate(reader):
                if i == 0:
                    header = csv_line[0].split(',')
                    for head in header:
                        if head == header[-1]:
                            head = "`" + head + "`"
                            head += ' text'
                        else:
                            head = "`" + head + "`"
                            head += ' text, '
                        headers_db += head
                    db_cursor.execute('CREATE TABLE ' + csv_file_name + '\n' + '(' + headers_db + ')')
                else:
                    rows_db = ''
                    row = csv_line[0].split(',')
                    for j, element in enumerate(row):
                        if j == len(row) - 1:
                            element = "'" + element + "'"
                        else:
                            element = "'" + element + "', "
                        rows_db += element
                    db_cursor.execute('INSERT INTO ' + csv_file_name + ' VALUES (' + rows_db + ")")

            db_connection.commit()
            db_connection.close()








def exportCSV_fromDB(csv_root, db_root):
    csv_file_name = ((csv_root.split('/'))[-1]).split('.')[0]
    csv_content = []
    # If it does not exist, we create a
    db_connection = sqlite3.connect(db_root)
    db_cursor = db_connection.cursor()
    for headers in db_cursor.execute('SELECT * FROM ' + csv_file_name + ' WHERE 1=2'):
        print(headers)
        print('ww')
    for row in db_cursor.execute('SELECT * FROM ' + csv_file_name):
        row=','.join(row)
        csv_content.append(row)
        print(row)
    #    print("inside")
    return csv_content


"""

This function returns True if database exists in our current Django project

args:
    table: String containing table name.
    cursor: *Not necessary to introduce*
"""
def db_table_exists(table, cursor=None):
    try:
        if not cursor:
            from django.db import connection
            cursor = connection.cursor()
        if not cursor:
            raise Exception
        table_names = connection.introspection.get_table_list(cursor)
    except:
        raise Exception("unable to determine if the table '%s' exists" % table)
    else:
        return table in table_names
