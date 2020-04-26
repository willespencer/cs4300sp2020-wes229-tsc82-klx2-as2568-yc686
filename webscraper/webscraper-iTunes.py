import time
from selenium.webdriver import Chrome
import pandas as pd

# iTunes webscraper using Selenium and our dataset of links

# get list of podcast names, review scores, and review texts

def get_reviews(podcasts):
    reviews = []
    for i in range(len(podcasts)):
        try:
            podcast = podcasts[i]

            podcast_name = podcast[0]
            url = podcast[1] + "#see-all/reviews"
            driver.get(url)

            # wait for reviews to load
            time.sleep(3)

            ratings =  driver.find_elements_by_class_name("we-star-rating") # TODO
            titles = driver.find_elements_by_class_name("we-customer-review__title")
            descriptions = driver.find_elements_by_class_name("we-clamp")

            for j in range(len(descriptions)):
                # aria-label will be "# out of 5" where number is 1, 2, 3, 4, or 5
                score_string = ratings[j].get_attribute("aria-label")
                score = int(score_string[0])

                title = titles[j].text

                # combine paragraphs into one string
                paragraphs = descriptions[j].find_elements_by_tag_name("p")
                review_text = ""
                for k in range(len(paragraphs)):
                    paragraph = paragraphs[k]

                    #innerText works, .text does not, unclear why
                    review_text += paragraph.get_attribute("innerText")
                    if(k != len(paragraphs) - 1):
                        review_text += "\n"

                reviews.append((podcast_name, title, score, review_text))
        except:
            # handle potential failure without program stopping
            print("failed at podcast", podcasts[i][0])
            continue
    return reviews

def get_podcasts_from_csv():
    df = pd.read_csv("merged_podcasts.csv", usecols = ['Name','iTunes_URL'])
    df1000 = pd.read_csv("first1000reviews.csv", usecols = ['podcast name'])
    df5000 = pd.read_csv("reviewspt2.csv", usecols = ['podcast name'])
    df3 = pd.read_csv("reviewspt3.csv", usecols = ['podcast name'])
    df4 = pd.read_csv("reviewspt4.csv", usecols = ['podcast name'])
    df5 = pd.read_csv("reviewspt5.csv", usecols = ['podcast name'])
    df6 = pd.read_csv("reviewspt6.csv", usecols = ['podcast name'])

    previouslyScraped = set(df1000["podcast name"].tolist() + df5000["podcast name"].tolist() + df3["podcast name"].tolist() + df4["podcast name"].tolist() + df5["podcast name"].tolist() + df6["podcast name"].tolist())

    tuples = [tuple(x) for x in df.to_numpy()]

    # remove ones with no iTunes links (check if nan)
    filtered = [t for t in tuples if t[1] == t[1] and t[0] not in previouslyScraped]
    # print(len(filtered))
    return filtered

def output_reviews_to_csv(reviews):
    df = pd.DataFrame(reviews,columns=['podcast name', 'review name', 'review score','review text'])
    df.to_csv('reviews.csv', encoding="utf-8")

podcasts = get_podcasts_from_csv()
print("Got list of podcasts")
#
webdriver = "./chromedriver"
driver = Chrome(webdriver)
print("Started Selenium")

reviews = get_reviews(podcasts)
print("Got list of all reviews")

output_reviews_to_csv(reviews)
print("Outputted reviews to csv")

driver.close()
