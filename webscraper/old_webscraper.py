from bs4 import BeautifulSoup
import urllib.request as url_test
import time
import mechanize
import requests

# This webscraper only works with html files downloaded, not with URLs
# Uses beuaitful soup and either mechanize, urllib, or requests

def get_soup_from_file(file):
    with open(file, encoding='utf8') as fp:
        soup = BeautifulSoup(fp, features="lxml")
        return soup

def get_soup_from_url(url):
    br = mechanize.Browser()
    br.open(url)
    time.sleep(10)
    response = br.response()
    time.sleep(10)
    soup = BeautifulSoup(response.read(), features="lxml")
    return soup

# def get_soup_from_url(url):
#     html = requests.get(url).content
#     soup = BeautifulSoup(html, features="lxml")
#     return soup


def get_podcasts():
    # soup = get_soup("https://www.stitcher.com/stitcher-list/")
    soup = get_soup_from_file("stitchertop100.html")

    body = soup.body
    wrapper = body.select(".wrapper")[0]

    content = wrapper.select("#content")[0]
    wrapper2 = content.select(".wrapper")[0]
    left_col = wrapper2.div.div
    sl_container = left_col.select("#sl-container")[0]
    # print(sl_container), has no tbody from url

    items = sl_container.table.tbody.select(".sl-item")

    podcasts = []
    for i in range(len(items)):
        a_tag = items[i].select(".sl-show-details")[0].span.a
        link = a_tag['href']
        name = a_tag.string
        podcasts.append((name, link))
    # print(podcasts)
    return podcasts


def get_reviews(soup):
    body = podcast_soup.body
    #print(body)
    wrapper = body.select(".wrapper")[1]
    # print(wrapper)
    content = wrapper.select("#showpage")[0]
    container = content.select("#BVRRContainer")[0]
    innerDiv = container.div.div.div.div
    review_list = innerDiv.ol.select(".bv-content-item")

    reviews = []
    for i in range(len(review_list)):
        item = review_list[i].div.div.div

        header =  item.select(".bv-content-header")[0]
        meta = header.div.div.span.meta
        score = meta["content"]

        details = item.select(".bv-content-details-offset-off")[0]
        review_body = details.div.div.div
        paragraphs = review_body.select("p")
        review_text = ""
        for j in range(len(paragraphs)):
            review_text += paragraphs[j].string + "\n"
        reviews.append((review_text, score))
    print(reviews)

podcasts = get_podcasts()
# podcast_soup = get_soup_from_url(podcasts[0][1])
podcast_soup = get_soup_from_file("joeroganex.html")
get_reviews(podcast_soup)
