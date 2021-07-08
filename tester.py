import requests
from bs4 import BeautifulSoup as Soup

url = "https://www.amazon.com/Govee-Brighter-Million-Controlled-Kitchen/dp/B07WHP2V77/ref=sr_1_2_sspa?dchild=1&keywords=32%2Bft%2Bled%2Bstrip&qid=1624900069&sr=8-2-spons&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUEzNzdDOURDMkgzMTFSJmVuY3J5cHRlZElkPUEwMDU4NDAwRkNDTk1JWFhISjlXJmVuY3J5cHRlZEFkSWQ9QTA5ODc1MTQzMEJJU0Y2T1I1MTUmd2lkZ2V0TmFtZT1zcF9hdGYmYWN0aW9uPWNsaWNrUmVkaXJlY3QmZG9Ob3RMb2dDbGljaz10cnVl&th=1"

amazon_request = requests.get("http://192.168.100.227:8050/render.html", params={'url': url, 'wait': 5})

scraper = Soup(amazon_request.text, 'lxml')

div_data = scraper.find('div', id='price')
