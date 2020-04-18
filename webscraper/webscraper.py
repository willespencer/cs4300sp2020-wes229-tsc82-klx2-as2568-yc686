import time
from selenium.webdriver import Chrome
import pandas as pd

# Selenium version of the old webscraper

# get list of podcast names and their review urls
def get_podcasts(url):
    driver.get(url)
    items = driver.find_elements_by_class_name("sl-showName")

    podcasts = []
    for i in range(len(items)):
        a_tag = items[i].find_element_by_tag_name("a")
        link = a_tag.get_attribute("href")
        name = a_tag.text
        podcasts.append((name, link))
    return podcasts

# get list of podcast names, review scores, and review texts
def get_reviews(podcasts):
    reviews = []
    for i in range(len(podcasts)):
        podcast = podcasts[i]

        podcast_name = podcast[0]
        driver.get(podcast[1])

        # wait for reviews to load
        time.sleep(5)

        # prevents the inclusion of the highlighted 2 incomplete reviews
        fullReviews = driver.find_element_by_class_name("bv-content-list-Reviews")

        ratings =  fullReviews.find_elements_by_xpath("//meta[@itemprop='ratingValue']")
        descriptions = fullReviews.find_elements_by_class_name("bv-content-summary-body-text")

        for i in range(len(descriptions)):
            score = ratings[i].get_attribute("content")

            # combine paragraphs into one string with line breaks
            paragraphs = descriptions[i].find_elements_by_tag_name("p")
            review_text = ""
            for j in range(len(paragraphs)):
                review_text += paragraphs[j].text + "\n"

            reviews.append((podcast_name, score, review_text))

    return reviews

def output_reviews_to_csv(reviews):
    df = pd.DataFrame(reviews,columns=['podcast name','review score','review text'])
    df.to_csv('reviews.csv')

webdriver = "./chromedriver"
driver = Chrome(webdriver)
url = "https://www.stitcher.com/stitcher-list/"

podcasts = get_podcasts(url)
print("Got list of podcasts")

reviews = get_reviews(podcasts)
print("Got list of all reviews")

output_reviews_to_csv(reviews)
print("Outputted reviews to csv")

driver.close()
