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
    EC.presence_of_element_located((By.ID, "mainContent")) #the id encompassing the content on the target page
    )
    finally:
        print('loaded')
        soup = BeautifulSoup(driver.page_source, 'html.parser')

    """Scraper to fetch each row and column"""
    