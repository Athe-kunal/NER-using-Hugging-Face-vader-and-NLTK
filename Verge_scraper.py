import selenium
from selenium import webdriver
import os
import json
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import re
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
from joblib import Parallel, delayed
from concurrent.futures import ProcessPoolExecutor
import time
import tqdm




def scrolling_func(wait,driver):
    SCROLL_PAUSE_TIME = 1.0

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.p-button')))
        load_button = driver.find_element_by_css_selector('.p-button')
        load_button.click()
        time.sleep(5)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def parse_dates(years,months):
    base_url = "https://www.theverge.com/archives" 
    urls = []
    zipped = zip(years,months)
    for year,month in zipped:
        url =  base_url+"/"+year+"/"+month
        urls.append(url)
    return urls

def link_extractor(titles):
    s = str(titles)[str(titles).find("href")+5:]
    return s[:s.find(">")]

def date_extractor(dates):
    return dates.text.strip()

def title_extractor(titles):
    return titles.text

def scraper(years,months):
    CHROME_PATH = r"C:\Users\astar\Stock market tutorials\chromedriver_win64\chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(CHROME_PATH,chrome_options=options)
    driver.maximize_window()
    
    urls = parse_dates(years,months)
    
    final_headlines = []
    final_dates = []
    final_links = []

    for url in urls:
        driver.get(url)
        done=True
     
        
        while done:
            try:
                wait = WebDriverWait(driver,10)
                scrolling_func(wait,driver)  
            except:
                done=False

        soup = BeautifulSoup(driver.page_source,'lxml')
        #https://stackoverflow.com/questions/5041008/how-to-find-elements-by-class
        #https://stackoverflow.com/questions/42732958/python-parallel-execution-with-selenium
        #https://stackoverflow.com/questions/44245451/how-to-scrape-multiple-html-page-in-parallel-with-beautifulsoup-in-python
        
        titles = soup.find_all("h2",class_="c-entry-box--compact__title")
        dates = soup.find_all("time",class_="c-byline__item")

        print(len(titles),len(dates))

        headlines_results = map(title_extractor,titles)
        dates_results = map(date_extractor,dates)
        links_results = map(link_extractor,titles)

        
        def list_process(gens):
            return [gen for gen in gens]
        
        headlines = list_process(headlines_results)
        dates = list_process(dates_results)
        links = list_process(links_results)

        final_headlines.extend(headlines) 
        final_dates.extend(dates) 
        final_links.extend(links)

        time.sleep(15)


    print(len(final_headlines),len(final_dates),len(final_links))    

    assert len(final_headlines)==len(final_dates)==len(final_links), f'Different lengths of headlines {len(headlines)} and date {len(dates)}'
    data = {"Headlines":final_headlines,"Dates":final_dates,"Links":final_links}
    df = pd.DataFrame(data) 
    print(len(df))
    df.to_csv('file1.csv') 
    return df 

if __name__ == "__main__":
    scraper(["2020"],["1"])