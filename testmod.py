from bs4 import BeautifulStoneSoup as soup
from selenium import webdriver
import requests
import time

url = "https://www.amazon.com/Govee-Brighter-Million-Controlled-Kitchen/dp/B07WHP2V77/ref=sr_1_2_sspa?dchild=1&keywords=32%2Bft%2Bled%2Bstrip&qid=1624900069&sr=8-2-spons&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUEzNzdDOURDMkgzMTFSJmVuY3J5cHRlZElkPUEwMDU4NDAwRkNDTk1JWFhISjlXJmVuY3J5cHRlZEFkSWQ9QTA5ODc1MTQzMEJJU0Y2T1I1MTUmd2lkZ2V0TmFtZT1zcF9hdGYmYWN0aW9uPWNsaWNrUmVkaXJlY3QmZG9Ob3RMb2dDbGljaz10cnVl&th=1"

desired_price = 33.00

driver = "C:/Program Files (x86)/chromedriver.exe"

class Browser:
  def __init__(self,webdriver_path,url):
    self.driver_path = webdriver_path
    self.prod_url = url
    self.chrome = webdriver.Chrome(executable_path=self.driver_path,chrome_options=self.browser_options())
    self.chrome.get(self.prod_url)
    
  def browser_options(self):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    #options.add_argument('--headless')
    #options.add_argument('--disable-gpu')
    return options
  
  
  def scrape_price(self):
    time.sleep(2)
    scraper = soup(self.chrome.page_source,features='xml')
    main_tag = scraper.find_all('div',id="dp")
    print(scraper)



a = Browser(driver,url)
a.scrape_price()
print("loaded page")
