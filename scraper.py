import requests
import json
import pandas as pd
import bs4 as BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller

from pyvirtualdisplay import Display
display = Display(visible = 0, size =(800, 800))
display.start()

chromedriver_autoinstaller.install() #To check if the current version of chromedriver exists, if not download automatically

chrome_options = webdriver.ChromeOptions()
options = [
    #Define window size
    "--window-size=1200,1200",
    "--ignore-certificate-errors"
]

for option in options:
    chrome_options.add_argument(option)

driver = webdriver.Chrome(options=chrome_options)

def ScrapePropertyData(): #Function to scrape property data
    driver.get('https://www.buyrentkenya.com/houses-for-sale/nairobi') #website to fetch data from
    try: #exception to wait for 30 seconds for the content on the target page to be loaded
        elem = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.ID, "mainContent")) #the class encompassing the content on the target page
    )
    finally:
        print('loaded')
        soup = BeautifulSoup(driver.page_source, 'html.parser')

    """Scraper to fetch each row and column"""

    result = soup.find_all('div', {'class' : 'listing-card'})
    len(result)

    result_update = [i for i in result if i.has_attr('data-bi')]
    len(result_update)

    """To get the specific attributes"""
    category = [result.find('div', {'data-bi-listing-category'}).get_text() for result in result_update]
    price = [result.find('div', {'data-bi-listing-price'}).get_text() for result in result_update]
    title = [result.find('a', {'data-cy' : 'listing-title-link'}).get_text() for result in result_update]
    location = [result.find('p', {'class' : 'ml-1'}).get_text() for result in result_update]
    bedrooms = [result.find('span', {'data-cy' : 'card-beds'}).get_text() for result in result_update]
    bathrooms = [result.find('span', {'data-cy' : 'card-bathrooms'}).get_text() for result in result_update]

    """To create a dataframe"""
    real_estate = pd.DataFrame(columns = ['Title', 'Category', 'Location', 'Beds', 'Baths', 'Price'])

    for i in range (len(location)):
        real_estate = real_estate.append({'Title':title[i], 'Category':category[i], 'Location':location[i], 'Beds':bedrooms[i], 'Baths':bathrooms[i], 'Price':price[i]})
    real_estate

