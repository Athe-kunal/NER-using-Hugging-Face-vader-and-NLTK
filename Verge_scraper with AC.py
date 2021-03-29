from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import logging
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download("wordnet")
from nltk.tokenize import PunktSentenceTokenizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords
import json
import urllib

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")

file_handler = logging.FileHandler('scraper.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def scrolling_func(wait,driver):
    SCROLL_PAUSE_TIME = 0.5

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('END').key_up(Keys.CONTROL).perform()
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
    time.sleep(SCROLL_PAUSE_TIME)
    ActionChains(driver).key_down(Keys.CONTROL).send_keys('HOME').key_up(Keys.CONTROL).perform()

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

def NER(sentence,query): #Named Entity recognizer
    text= " ".join([word for word in list(sentence.split(" ")) if word not in stopwords.words("english")])
    custom_sent_tokenizer = PunktSentenceTokenizer()
    tokenized = custom_sent_tokenizer.tokenize(text)

    NERS = []
    for token in tokenized:
        words = nltk.word_tokenize(token)
        tagged = nltk.pos_tag(words)
    # named_ent = nltk.ne_chunk()
    for tags in tagged:
        if tags[1] in ['NNP']:
            NERS.append(query+" "+tags[0])
    return NERS

def GKG(query): #Google knowledge graph
    api_key = 'AIzaSyCICUBPcSLJKKywmJuwIUFaumLqNrXrOlU'
    service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
    params = {
        'query': query,
        'limit': 5,
        'indent': True,
        'key': api_key,
}
    url = service_url + '?' + urllib.parse.urlencode(params)
    response = json.loads(urllib.request.urlopen(url).read())
    for element in response['itemListElement']:
        if query.split(" ")[-1] in element['result']['name'] and element['resultScore']>=1000.0:
            return True
            break

def scraper(years,months):
    CHROME_PATH = r"C:\Users\astar\Stock market tutorials\chromedriver_win64\chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(CHROME_PATH,options=options)
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
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('HOME').key_up(Keys.CONTROL).perform()
        soup = BeautifulSoup(driver.page_source,'lxml')
        #https://stackoverflow.com/questions/5041008/how-to-find-elements-by-class
        #https://stackoverflow.com/questions/42732958/python-parallel-execution-with-selenium
        #https://stackoverflow.com/questions/44245451/how-to-scrape-multiple-html-page-in-parallel-with-beautifulsoup-in-python
        #https://stackoverflow.com/questions/45816619/selenium-firefox-webdriver-for-python-keyerror-value
        num_articles = soup.find("h1",class_="p-page-title").text
        current = num_articles[num_articles.find("for")+4:num_articles.find("(")]
        articles_num = num_articles[num_articles.find("(")+1:-1]
        titles = soup.find_all("h2",class_="c-entry-box--compact__title")
        dates = soup.find_all("time",class_="c-byline__item")

        if articles_num != len(titles):
            logger.warning("Actual #articles {} and #scraped articles {} for {}".format(articles_num,len(titles),current))
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
    df.to_csv('file1.csv') 
    return df 

def main(years,months,query):
    df = scraper(years,months)
    final_df = pd.DataFrame(columns=["Headlines","Dates","Links"])
    for index, row in df.iterrows():   
        if query in row[0]:
            final_df.loc[index] = df.loc[index]
        else:
            NERS = NER(row[0],query)
            try:
                for ner in NERS:
                    if GKG(ner):
                        final_df.loc[index] = df.loc[index]
            except Exception as e:
                print(e)
    return final_df.reset_index(inplace=True)

if __name__ == "__main__":
    final_df = main(["2021"],["2"],"Google")
    print(final_df)
