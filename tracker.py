from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup as Soup
from email.mime.text import MIMEText
from dotenv import load_dotenv
import requests
import smtplib
import json
import ssl
import os


def calc_discount(price, coupon):
    if "%" in coupon:
        index = coupon.find("%")
        coupon_val = "0." + coupon[0:index]
        discount = price * float(coupon_val)
        price_discount = round(price - discount, 2)
        return {
            "Amazon_Price": price,
            "Discounted_Price": price_discount
        }
    elif "$" in coupon:
        index = coupon.find("$")
        coupon_val = coupon[index + 1:]
        price_discount = round(price - float(coupon_val), 2)
        return {
            "Amazon_Price": price,
            "Discounted_Price": price_discount
        }


class Amazon_item:
    coupon = None

    def __init__(self, prod_search, prod_url):
        self.item = prod_search
        request = requests.get("http://192.168.100.227:8050/render.html", params={"url": prod_url, "wait": 3})
        self.scraper = Soup(request.text, "lxml")

    @property
    def name(self):
        head_element = self.scraper.find("h1", id="title")
        prod_name = head_element.find("span", id="productTitle").text.split()
        return " ".join(prod_name)

    @property
    def pricing(self):
        price_element = self.scraper.find("div", id="price")
        if price_element is None:
            print("No price element found")
        else:
            amz_price = float(price_element.find("span", id="priceblock_ourprice").text[1:])
            coupon_element = self.scraper.find('tr', class_="couponFeature")
            if coupon_element is None:
                return {"Amazon_Price": amz_price, "Discounted_Price": None}
            else:
                self.coupon = coupon_element.find('span', class_="a-color-success").text.split()[3]
                return calc_discount(price=amz_price, coupon=self.coupon)

    @property
    def image_url(self):
        img_container = self.scraper.find('div', id="imgTagWrapperId")
        img_tag = img_container.find('img')
        return img_tag.get("src")


class Bot_tracker:
    def __init__(self):
        load_dotenv()
        self.email = os.environ.get("email")
        self.password = os.environ.get("password")
        self.products = []
        with open('Track.json', 'r') as prod_list:
            track_products = json.load(prod_list).get("Products_Tracking")
            for item in track_products:
                what_product = item.get("name")
                product_url = item.get("url")
                desired_price = item.get("desired_price")
                product_dict = {
                    what_product: {
                        "url": product_url,
                        "desired_price": desired_price
                    }
                }
                self.products.append(product_dict)


# product = Amazon_item(what_product, product_url)
# print(product.name)
# print(product.pricing)
# print(product.image_url)
# print(product.coupon)

bot = Bot_tracker()


