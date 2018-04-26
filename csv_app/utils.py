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
            reader = csv.reader(csvfile, quotechar='|')
            headers_db = ''
            db_connection = sqlite3.connect(db_root)
            db_cursor = db_connection.cursor()
            for i, csv_line in enumerate(reader):
                print('csv_line: ',csv_line)
                if i == 0:
                    header = csv_line
                    print('header: ', header)
                    for head in header:
                        print('head: ', head)
                        if head == header[-1]:
                            head = "`" + head + "`"
                            head += ' text'
                        else:
                            head = "`" + head + "`"
                            head += ' text, '
                        headers_db += head
                        print('headers: ', headers_db)

                    db_cursor.execute('CREATE TABLE ' + csv_file_name + '\n' + '(' + headers_db + ')')
                else:
                    rows_db = ''
                    row = csv_line
                    for j, element in enumerate(row):
                        if j == len(row) - 1:
                            element = "'" + element + "'"
                        else:
                            element = "'" + element + "', "
                        rows_db += element
                        print('rows: ', rows_db)
                    db_cursor.execute('INSERT INTO ' + csv_file_name + ' VALUES (' + rows_db + ")")

            db_connection.commit()
            db_connection.close()








def exportCSV_fromDB(csv_root, db_root):
    csv_file_name = ((csv_root.split('/'))[-1]).split('.')[0]
    csv_content = []
    header_list = []
    # If it does not exist, we create a
    db_connection = sqlite3.connect(db_root)
    db_cursor = db_connection.cursor()
    for headers in db_cursor.execute('PRAGMA table_info(' + csv_file_name + ');'):
        header_list.append(headers[1])
    header_list=','.join(header_list).split(',')
    for row in db_cursor.execute('SELECT * FROM ' + csv_file_name):
        row=','.join(row).split(',')
        csv_content.append(row)

    return csv_content, header_list



def deleteCSV_fromDB(csv_root, db_root):
    csv_file_name = ((csv_root.split('/'))[-1]).split('.')[0]
    db_connection = sqlite3.connect(db_root)
    db_cursor = db_connection.cursor()
    db_cursor.execute('DROP TABLE ' + csv_file_name + ';')

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
