import time
from selenium.webdriver import Chrome
import pandas as pd

def combineFiles():
    files = []
    files.append(pd.read_csv("first1000reviews.csv", usecols = ['podcast name', 'review name', 'review score', 'review text']))
    files.append(pd.read_csv("reviewspt2.csv", usecols = ['podcast name', 'review name', 'review score', 'review text']))
    files.append(pd.read_csv("reviewspt3.csv", usecols = ['podcast name', 'review name', 'review score', 'review text']))
    files.append(pd.read_csv("reviewspt4.csv", usecols = ['podcast name', 'review name', 'review score', 'review text']))
    files.append(pd.read_csv("reviewspt5.csv", usecols = ['podcast name', 'review name', 'review score', 'review text']))
    files.append(pd.read_csv("reviewspt6.csv", usecols = ['podcast name', 'review name', 'review score', 'review text']))

    finalData = []
    for file in files:
        currPodcastName = ""
        reviewsForName = []
        for index, row in file.iterrows():
            # ignoring review name for now
            name = row['podcast name']
            if(name == currPodcastName):
                reviewsForName.append((str(row['review score']), str(row['review text'])))
            else :
                # sort list by longest review and add to dict
                reviewsForName.sort(key=lambda t: len(t[1]), reverse=True)
                shortenedList = reviewsForName[:5]
                lineToOutput = [currPodcastName]
                for i in range(len(shortenedList)):
                    lineToOutput.append(shortenedList[i][0])
                    lineToOutput.append(shortenedList[i][1])
                finalData.append(lineToOutput)

                # clear and prep for next iteration
                currPodcastName = name
                reviewsForName = []
                reviewsForName.append((row['review score'], row['review text']))
    return finalData[1:]

def output_data_to_csv(data):
    df = pd.DataFrame(data,columns=['name', 'score1', 'text1', 'score2', 'text2', 'score3', 'text3', 'score4', 'text4', 'score5', 'text5'])
    df.to_csv('combindedReviews.csv', encoding="utf-8")

finalData = combineFiles()
print("Got data")
output_data_to_csv(finalData)
print("Done")
