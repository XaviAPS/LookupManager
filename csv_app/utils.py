import csv
import sqlite3
import json
"""
This function imports a CSV (comma delimited) into a SQLite3 DB
Creates a table named: <document_name>
Fills it with the CSV content

args:
    csv_root: Path of the CSV file (example: C:/Documents/example.csv)
    db_root: Path of the database file (example: C:/Documents/my_database.db)
    
"""

def importCSV_inDB(csv_root, db_root):
    csv_file_name = ((((csv_root.split('/'))[-1]).split('.')[0]).replace(" ", "_")).replace("-","_")

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




def exportLog_fromDB(filename, db_root):
    filename = (filename.replace(" ", "_")).replace("-","_")
    db_connection = sqlite3.connect(db_root)
    db_cursor = db_connection.cursor()
    content = []
    for i, row in enumerate(db_cursor.execute('SELECT * ' + 'FROM csv_app_log;')):
        print('row: ', row)
        if(i==2):
            next(db_cursor.execute('SELECT * ' + 'FROM csv_app_log;'))
        if filename in row:
            row = row[1:]
            row = [x for i, x in enumerate(row) if i != 2 and x != filename]
            print('end_row: ', row)
            content.append(row)
    return content


def exportCSV_fromDB(csv_root, db_root):
    csv_file_name = ((((csv_root.split('/'))[-1]).split('.')[0]).replace(" ", "_")).replace("-","_")
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
    csv_file_name = ((((csv_root.split('/'))[-1]).split('.')[0]).replace(" ", "_")).replace("-","_")
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



# Get The Current Date Or Time
# def getdatetime(timedateformat='complete'):
#     from datetime import datetime
#     timedateformat = timedateformat.lower()
#     if timedateformat == 'day':
#         return ((str(datetime.now())).split(' ')[0]).split('-')[2]
#     elif timedateformat == 'month':
#         return ((str(datetime.now())).split(' ')[0]).split('-')[1]
#     elif timedateformat == 'year':
#         return ((str(datetime.now())).split(' ')[0]).split('-')[0]
#     elif timedateformat == 'hour':
#         return (((str(datetime.now())).split(' ')[1]).split('.')[0]).split(':')[0]
#     elif timedateformat == 'minute':
#         return (((str(datetime.now())).split(' ')[1]).split('.')[0]).split(':')[1]
#     elif timedateformat == 'second':
#         return (((str(datetime.now())).split(' ')[1]).split('.')[0]).split(':')[2]
#     elif timedateformat == 'millisecond':
#         return (str(datetime.now())).split('.')[1]
#     elif timedateformat == 'yearmonthday':
#         return (str(datetime.now())).split(' ')[0]
#     elif timedateformat == 'daymonthyear':
#         return ((str(datetime.now())).split(' ')[0]).split('-')[2] + '-' + ((str(datetime.now())).split(' ')[0]).split('-')[1] + '-' + ((str(datetime.now())).split(' ')[0]).split('-')[0]
#     elif timedateformat == 'hourminutesecond':
#         return ((str(datetime.now())).split(' ')[1]).split('.')[0]
#     elif timedateformat == 'secondminutehour':
#         return (((str(datetime.now())).split(' ')[1]).split('.')[0]).split(':')[2] + ':' + (((str(datetime.now())).split(' ')[1]).split('.')[0]).split(':')[1] + ':' + (((str(datetime.now())).split(' ')[1]).split('.')[0]).split(':')[0]
#     elif timedateformat == 'complete':
#         return str(datetime.now())
#     elif timedateformat == 'datetime':
#         return (str(datetime.now())).split('.')[0]
#     elif timedateformat == 'timedate':
#         return ((str(datetime.now())).split('.')[0]).split(' ')[1] + ' ' + ((str(datetime.now())).split('.')[0]).split(' ')[0]

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)

def csv_to_JSON(file, json_file):

    csvfile = open(file, 'r')
    reader = csv.DictReader(csvfile)
    headers = reader.fieldnames
    jsonfile = open(json_file, 'w')

    reader = csv.DictReader(csvfile, headers)
    # next(reader, None)  # skip the headers
    all_lines = list(reader)
    for row in all_lines:

        if 'LATITUDE' in row and 'LONGITUDE' in row:
            row['coords'] = '{ asdtypeasd: asdPointasd,asdcoordinatesasd: [' + row['LATITUDE'] +', ' + row['LONGITUDE']+'] }'

        if row == all_lines[-1]:
            jsonfile.write(
                json.dumps(row, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False) + '\n')

        else:
            jsonfile.write(
                json.dumps(row, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False) + ',\n')
    jsonfile.close()




    with open(json_file, "rt") as json_r:
        with open('./media/tmp/converted.json', "wt") as json_w:
            for line in json_r:
                if 'coords' in line:
                    json_w.write(((line.replace('asd', '"')).replace('"{','{')).replace('}"', "}").replace('"Point",','"Point",\n\t\t'))
                    print(line)
                else:
                    json_w.write(line)