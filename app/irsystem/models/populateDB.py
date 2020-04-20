import json
import csv
import sys
import datetime
import psycopg2
from psycopg2 import connect, Error

update_podcasts = True
update_reviews = False

try:
    conn = connect(
        dbname="pea_podcast",
        user="postgres",
        host="localhost",
        password="1234",
        # attempt to connect for 3 seconds then raise exception
        connect_timeout=3
    )

    cur = conn.cursor()
    print("\ncreated cursor object:", cur)

except (Exception, Error) as err:
    print("\npsycopg2 connect error:", err)
    conn = None
    cur = None

# only attempt to execute SQL if cursor is valid
if cur != None:

    if update_podcasts:

        with open('data/merged_podcasts.json') as json_data:
            record_dict = json.load(json_data)
            table_name = "podcasts"

        # enumerate over the records' values
        records = record_dict.values()
        val_list = [[] for x in range(len(records))]
        # enumerate over the records' values
        for i, record in enumerate(records):

            # append each value to a new list of values
            for v, key in enumerate(record):
                val = record[key]
                if type(val) == list:
                    avg_ep_dur = 0
                    if type(val[0]) == float or type(val[0]) == int:
                        sum_ep_dur = sum(val)
                        avg_ep_dur = sum_ep_dur / len(val)
                        val = avg_ep_dur
                    else:
                        val = ';'.join(map(str, val))
                        val = str(val).replace('"', '')
                elif type(val) == str:
                    val = str((val)).replace('"', '')
                val_list[i].append(str(val))

        try:
            for i in range(len(list(records)[0])):
                cur.execute(
                    """INSERT INTO podcasts VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (i, datetime.datetime.now(), datetime.datetime.now(),
                     val_list[0][i], val_list[1][i], val_list[2][i],  val_list[3][i],  val_list[4][i],  val_list[5][i],  val_list[6][i],
                     val_list[7][i], val_list[8][i], val_list[9][i], val_list[10][i]))
            conn.commit()

            print('\nfinished INSERT INTO execution')

        except (Exception, Error) as error:
            print("\nexecute_sql() error:", error)
            conn.rollback()

    if update_reviews:
        with open('data/reviews.csv', newline='') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header row.

            try:
                for row in reader:
                    # each row is a list
                    cur.execute(
                        """INSERT INTO reviews VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (row[0], datetime.datetime.now(), datetime.datetime.now(), row[1], row[2], row[3], row[4]))

                conn.commit()

                print('\nfinished INSERT INTO execution')

            except (Exception, Error) as error:
                print("\nexecute_sql() error:", error)
                conn.rollback()

    # close the cursor and connection
    cur.close()
    conn.close()
