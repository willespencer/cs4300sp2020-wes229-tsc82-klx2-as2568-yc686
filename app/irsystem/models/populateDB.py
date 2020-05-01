import json
import csv
import sys
import datetime
import psycopg2
from psycopg2 import connect, Error

update_podcasts_and_reviews = False

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

    if update_podcasts_and_reviews:

        combinedData = {}

        with open('data/merged_podcasts.csv', newline='') as podcast_data:
            podcast_reader = csv.reader(podcast_data)
            next(podcast_reader)
            numPodcast = 0

            for row in podcast_reader:
                # each row is a list
                name = str(row[1]).replace('"', '')

                genres = row[6].replace('\'', '').split(", ")
                genres = [x.strip("]").strip("[") for x in genres]
                genres = ';'.join(genres)

                row[8] = row[8].split(", ")
                sum_ep_dur = 0
                for i in row[8]:
                    val = float(i.strip("]").strip("["))
                    sum_ep_dur += val
                avg_ep_dur = sum_ep_dur * 1.0 / len(row[8])

                podcastData = [row[0], float(row[2]), float(row[3]), row[4], row[5],
                               genres, int(row[7]), avg_ep_dur, row[9], row[11]]
                combinedData[name] = podcastData
                numPodcast += 1

        # print("num podcasts:" + str(numPodcast)) = 6657
        # print(len(combinedData)) =  6598
        # print(combinedData["The Moth"])

        with open('data/combindedReviews.csv', newline='') as f:
            review_reader = csv.reader(f)
            next(review_reader)  # Skip the header row.

            numReviews = 0
            for row in review_reader:
                name = str(row[1]).replace('"', '')
                reviewData = [row[2], row[3], row[4], row[5],
                              row[6], row[7], row[8], row[9], row[10], row[11]]
                if name in combinedData.keys():
                    newData = combinedData[name] + reviewData
                    combinedData[name] = newData
                numReviews += 1

        # print("num Reviews: " + str(numReviews))  # = 5889
        # print(combinedData["The Moth"])
        # print(len(combinedData["The Moth"]))

        try:
            for key in combinedData.keys():
                podcast = combinedData[key]
                podcast = [x if x != '' else None for x in podcast]
                if (len(podcast) == 20):
                    cur.execute(
                        """INSERT INTO podcasts VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (podcast[0], datetime.datetime.now(), datetime.datetime.now(),
                         key, podcast[1], podcast[2], podcast[3], podcast[4], podcast[5], podcast[6], podcast[7],
                         podcast[8], podcast[9], podcast[10], podcast[11], podcast[12], podcast[13], podcast[14],
                         podcast[15], podcast[16], podcast[17], podcast[18], podcast[19]))
                else:
                    cur.execute(
                        """INSERT INTO podcasts VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (podcast[0], datetime.datetime.now(), datetime.datetime.now(),
                         key, podcast[1], podcast[2], podcast[3], podcast[4], podcast[5], podcast[6], podcast[7],
                         podcast[8], podcast[9]))
            conn.commit()

            print('\nfinished INSERT INTO execution')

        except (Exception, Error) as error:
            print("\nexecute_sql() error:", error)
            conn.rollback()

    # close the cursor and connection
    cur.close()
    conn.close()
