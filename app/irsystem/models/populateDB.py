import json
import sys
import datetime
from psycopg2 import connect, Error


with open('merged_podcasts.json') as json_data:

    record_dict = json.load(json_data)

    # columns = list(["name", "rating_volume", "rating", "genre",
    #                 "description_x", "artwork",
    #                 "genres", "ep_count",
    #                 "ep_durations",
    #                 "itunes_URL",
    #                 "deed_URL",
    #                 "podcast_URL", "description_y"])

    table_name = "podcasts"

# nval_list = [[x] for x in range(len(list(records)[0]))]
# for i, record in enumerate(records):

#     for v, key in enumerate(record):
#         val = record[key]
#         if type(val) == list:
#             val = ';'.join(map(str, val))
#             val = str(val).replace('"', '')
#         if type(val) == str:
#             if ("http:" not in str(val)):
#                 val = str(val).replace('"', '\'')
#                 val = str(val).replace('\'', '')
#             val = str(val)
#         nval_list[v].append(val)

# print(str(tuple(nval_list[0])))
# # print("val_list: " + str(len(val_list)))


# enumerate over the records' values
records = record_dict.values()
val_list = [[] for x in range(len(records))]
# enumerate over the records' values
for i, record in enumerate(records):

    # append each value to a new list of values
    for v, key in enumerate(record):
        val = record[key]
        if type(val) == list:
            val = ';'.join(map(str, val))
            val = str(val).replace('"', '')
        elif type(val) == str:
            val = str((val)).replace('"', '')
        val_list[i].append(str(val))

    # print("val_list: " + str(len(val_list[i])))
# print(str(val_list[1]))
# for i, val in enumerate(val_list):
#     val_list[i] = tuple(val_list[i])

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

    try:

        for i in range(len(list(records)[0])):
            cur.execute(
                """INSERT INTO podcasts VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (i, datetime.datetime.now(), datetime.datetime.now(),
                 val_list[5][i], val_list[4][i], val_list[12][i],  val_list[7][i],  val_list[8][i],  val_list[3][i],  val_list[6][i],
                 val_list[9][i], val_list[0][i], val_list[11][i], val_list[2][i], val_list[1][i], val_list[10][i]))
        conn.commit()

        print('\nfinished INSERT INTO execution')

    except (Exception, Error) as error:
        print("\nexecute_sql() error:", error)
        conn.rollback()

    # close the cursor and connection
    cur.close()
    conn.close()
