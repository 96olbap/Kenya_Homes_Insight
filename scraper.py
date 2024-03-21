import pandas as pd
import bs4 as bs
import time
import re

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller

# from pyvirtualdisplay import Display
# display = Display(visible = 0, size =(800, 800))
# display.start()

"""Set up the Chrome driver"""
chrome_driver_path = '/Users/wepukhulu/Downloads/chromedriver'
chrome_options = Options()
chrome_options.add_argument(f"exec_path={chrome_driver_path}")

"""Initialize the Chrome driver with the correct options"""
driver = webdriver.Chrome(options=chrome_options)

# Data cleaning functions
def clean_category(category):
    categories = ['villa', 'bungalow', 'apartment', 'townhouse']
    for cat in categories:
        if cat in category.lower():
            return cat.capitalize()
    return 'Other'

def clean_price(price):
    match = re.search(r'KSh\s*([\d,]+)', price)
    if match:
        return int(match.group(1).replace(',', ''))
    return None

def ScrapePropertyData(): #Function to scrape property data

    columns = ['Title', 'Category', 'Location', 'Beds', 'Baths', 'Price']
    real_estate = []

    """To scrape data from the first 80 pages of the website"""
    for i in range(1, 81):
        url = f'https://www.buyrentkenya.com/houses-for-sale/nairobi' + str(i) + '_p/'
        driver.get(url)

        try:
            elem = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//body"))
            )
        except:
            print(f"Failed to load {url}")
            continue

        print(f'Loaded: {url}')
    
        result_elements = driver.find_elements(By.CSS_SELECTOR, 'div.listing-card')
            
        for result in result_elements:
            try:
                title = result.find_element(By.CSS_SELECTOR, 'a[data-cy="listing-title-link"]').text
            except:
                title = 'n/a'
            try:
                category = result.find_element(By.CSS_SELECTOR, 'div[data-bi-listing-category]').text
            except:
                category = 'n/a'
            try:
                location = result.find_element(By.CSS_SELECTOR, 'p.ml-1').text
            except:
                location = 'n/a'
            try:
                bedrooms = result.find_element(By.CSS_SELECTOR, 'span[data-cy="card-beds"]').text
            except:
                bedrooms = 'n/a'
            try:
                bathrooms = result.find_element(By.CSS_SELECTOR, 'span[data-cy="card-bathrooms"]').text
            except:
                bathrooms = 'n/a'
            try:
                price = result.find_element(By.CSS_SELECTOR, 'div[data-bi-listing-price]').text
            except:
                price = 'n/a'

            real_estate.append({'Title': title, 'Category': category, 'Location': location,
                             'Beds': bedrooms, 'Baths': bathrooms, 'Price': price})


    real_estate_df = pd.DataFrame(real_estate, columns=columns)
    print(real_estate_df)

    """Clean the dataframe"""
    real_estate_df['Category'] = real_estate_df['Category'].apply(clean_category)
    real_estate_df['Price'] = real_estate_df['Price'].apply(clean_price)

    """Drop rows with None in 'Price'"""
    real_estate_df.dropna(subset=['Price'], inplace=True)

    """Save the data to a csv file"""
    real_estate_df.to_csv('real_estate_nrb_cleaned.csv', index=False, sep=';')
    return real_estate_df

ScrapePropertyData()