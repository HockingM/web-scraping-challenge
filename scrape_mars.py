# import dependencies
from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from webdriver_manager.chrome import ChromeDriverManager


def init_browser():
    executable_path = {"executable_path": ChromeDriverManager().install()}
    return Browser('chrome', **executable_path, headless=False)


def scrape_news():
    # create data dictionary
    news_data = {}

    # create webdriver object
    browser = init_browser()

    # visit mars.nasa.gov/news/
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    # look for the element on the page - accounting for latency between Aus and US
    browser.is_element_present_by_css("ul.item_list li.slide")
    time.sleep(2)

    # scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    # find first item in unordered list
    results = soup.select_one("ul.item_list li.slide")

    # get title and assign variable
    news_title = results.find("h3").text

    # get article teaser and assign variable
    news_p = results.find("div", class_="article_teaser_body").text

    # store data in a dictionary
    news_data = {
        "news_title": news_title,
        "news_p": news_p
    }

    # close the browser after scraping
    browser.quit()

    # create new webdriver object
    browser = init_browser()

    # https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)

    # navigate to featured image
    browser.click_link_by_id("full_image")
    browser.click_link_by_partial_text("more info")
    time.sleep(2)

   # scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    # locate image and browser urls
    content = soup.select_one("figure.lede img")["src"]

    # slice browser url and concatenate with image url
    link = browser.url[:24]
    featured_image_url = f"{link}{content}"

    # store data in a dictionary
    news_data["featured_image_url"] = featured_image_url  

    # close the browser after scraping
    browser.quit()
    
    # return results
    return news_data

def scrape_hemispheres():
    # create data dictionary
    hemisphere_image_urls = []

    # create new webdriver object
    browser = init_browser()

    # get webpage
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)
    time.sleep(2)

   # scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    # locate image and browser urls
    results = soup.find_all("div", class_="item")
    
    for i in range(len(results)):
        link = results[i].a["href"]
        browser.find_by_css("img.thumb")[i].click()
        title = browser.find_by_css("h2.title").text
        src = browser.find_by_css("img.wide-image")["src"]
        hemisphere_image_urls.append({"title_"+str(i):title, "url_"+str(i):src})
        time.sleep(2)

    # close the browser after scraping
    browser.quit()
    
    # return results
    return hemisphere_image_urls


def scrape_facts():
    # scrape table
    url = "https://space-facts.com/mars/"
    mars_data = pd.read_html(url)

    # create dataframe
    mars_df = mars_data[0]
    mars_df.columns = ["Facts", "Mars"] 
    mars_df.set_index("Facts", inplace = True)

    # export dataframe to html table
    mars_df.to_html("table.html")

    # return results
    return mars_df.to_html (classes="table table-striped table-bordered")

