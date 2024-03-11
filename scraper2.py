import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pyvirtualdisplay import Display
from selenium.webdriver.chrome.options import Options

# Set up the Chrome driver
chrome_driver_path = '/Users/wepukhulu/Downloads/chromedriver'
chrome_options = Options()
chrome_options.add_argument(f"exec_path={chrome_driver_path}")

# Initialize the Chrome driver with the correct options
driver = webdriver.Chrome(options=chrome_options)

def ScrapePropertyData():
    all_data = []  # Create a list to store data

    for i in range(1, 6):
        url = f'https://www.buyrentkenya.com/houses-for-sale/nairobi/{i}_p/'
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

            all_data.append({'Title': title, 'Category': category, 'Location': location,
                             'Beds': bedrooms, 'Baths': bathrooms, 'Price': price})

    # Create DataFrame outside the loop
    real_estate_new = pd.DataFrame(all_data)
    print(real_estate_new)

    driver.quit()  # Close the browser when done
    return real_estate_new

ScrapePropertyData()