import codecs
import json
import logging as log
import random
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep

import requests
import schedule
from bs4 import BeautifulSoup as Soup

logs_format = "%(asctime)s|%(levelname)s|%(message)s"

log.basicConfig(level=log.INFO, encoding="utf-8",
                format=logs_format, datefmt="%d-%b-%y %H:%M:%S")

json_path = "./app/Settings.json"

config_content = """ Amazon Tracker is initialized with the following configuration:
---> Sender Email: {arg0}
---> Receiver Email: {arg1}
---> Tracking Schedule : {arg2}"""


class Amazon_Product:
    def __init__(self, amz_req):
        try:
            self.scraper = Soup(amz_req.text, "lxml")
            self.url = amz_req.url
        except Exception as err:
            print(err)

    coupon = None

    @property
    def name(self):
        _name = self.scrpe_name()
        return _name

    @property
    def image(self):
        _image = self.scrpe_img_url()
        return _image

    @property
    def pricing(self):
        _pricing = self.scrpe_pricing()
        return _pricing

    def scrpe_name(self):
        try:
            name_element = self.scraper.find("h1", id="title")
            product_name = name_element.find(
                "span", id="productTitle").text.split()
            return " ".join(product_name)
        except Exception as err:
            log.error("Could not find a HTML name element for product name")
            print(err)
            return None

    def scrpe_img_url(self):
        try:
            img_element = self.scraper.find('div', id="imgTagWrapperId")
            img_tag = img_element.find("img")
            return img_tag.get("src")
        except Exception as err:
            log.error("Could not find a HTML element for product image")
            print(err)
            return None

    def scrpe_pricing(self):
        amz_price = None

        price_element = self.scraper.find("div", id="price")

        if price_element is not None:
            try:
                amz_price = float(price_element.find(
                    "span", id="priceblock_saleprice").text[1:])  # amzn retail price
            except AttributeError:
                pass  # move on to next html id for price

            try:
                amz_price = float(price_element.find(
                    "span", id="priceblock_ourprice").text[1:])
            except AttributeError:
                pass  # move on to next html id for price

            try:
                amz_price = float(price_element.find(
                    "span", id="priceblock_dealprice").text[1:])
            except AttributeError:
                pass  # move on to next html id for price

            coupon_elem = self.scraper.find('tr', class_="couponFeature")

            if coupon_elem is None:
                return {"Amazon_Price": amz_price, "Discounted_Price": None}
            else:
                self.coupon = coupon_elem.find(
                    "span", class_="a-color-success").text.split()[3]
                return calc_discount(price=amz_price, coupon=self.coupon)
        else:
            return None  # indicates that amazon product is out of stock


class Amazon_Tracker:
    def __init__(self):
        self.configs = get_configs()
        self.email_content = get_mail_template()
        self.smtp_server = self.configs.get("smtp_server")
        self.smtp_port = self.configs.get("smtp_port")
        self.sender_email = self.configs.get("bot_email")
        self.sender_pswd = self.configs.get("bot_passwd")
        self.receiver_email = self.configs.get("receiver_email")
        self.cmd_schedule = self.configs.get("schedule").split()

    # Define a function that gets the products to track
    @property
    def track_products(self):
        prods = get_prod_list()
        return prods

    # Function that defines the runtime of the tracker bot
    def run(self):
        sched = self.read_schedule()
        kwargs = {
            "arg0": self.sender_email,
            "arg1": self.receiver_email,
            "arg2": sched.get("Description")
        }
        log.info(config_content.format(**kwargs))
        # returns the appropiate schedule module object
        return sched.get("Sched-Variable")

    # Generator that calls the Scraper Amazon class
    def amz_generator(self):
        for prod in self.track_products:
            browser_header = get_request_header()
            prod_url = prod.get("url")
            request = requests.get(
                prod_url, headers=browser_header, params={"wait": 10})
            yield Amazon_Product(request)

    # Configuring SMTP protocol and message to send email notification
    def sendmail(self):
        log.info(f"Tracking {len(self.track_products)} products")
        products = self.amz_generator()
        econtent = None
        for index, product in enumerate(products):
            usr_prod_name = self.track_products[index].get("name")
            desired_price = self.track_products[index].get("desired_price")
            message = MIMEMultipart("alternative")
            message["From"] = self.sender_email
            message["To"] = self.receiver_email
            message["Subject"] = "Price Alert: " + usr_prod_name

            if product.pricing is None:
                log.info(f"{usr_prod_name} is currently out of stock")
                continue

            elif product.pricing.get("Discounted_Price") is None and product.pricing.get(
                    "Amazon_Price") <= desired_price:
                econtent = self.fill_content(product)

            elif product.pricing.get("Discounted_Price") is None and product.pricing.get(
                    "Amazon_Price") > desired_price:
                log.info(
                    f"There are no coupons and the Amazon price is > desired price for {usr_prod_name}")
                continue

            elif product.pricing.get("Amazon_Price") <= desired_price or product.pricing.get(
                    "Discounted_Price") <= desired_price and product.pricing.get("Discounted_Price") is not None:
                econtent = self.fill_content(product)

            elif product.pricing.get("Amazon_Price") > desired_price or product.pricing.get(
                    "Discounted_Price") > desired_price:
                log.info(
                    f"Both Amazon price and Coupon Discounted price is > desired price for {usr_prod_name}")
                continue

            mail_content = MIMEText(econtent, 'html')
            message.attach(mail_content)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as mail_driver:
                log.info(f"Sending mail for {usr_prod_name}")
                mail_driver.login(self.sender_email, self.sender_pswd)
                mail_driver.sendmail(
                    self.sender_email,
                    self.receiver_email,
                    message.as_string())
        return

    # Function to populate html template with appropiate data
    def fill_content(self, product: Amazon_Product) -> str:
        if product.coupon is None:
            kwargs = {
                "arg1": product.name,
                "arg2": product.image,
                "arg3": product.pricing.get("Amazon_Price"),
                "arg4": "None",
                "arg5": product.pricing.get("Amazon_Price"),
                "arg6": product.url
            }
        else:
            kwargs = {
                "arg1": product.name,
                "arg2": product.image,
                "arg3": product.pricing.get("Amazon_Price"),
                "arg4": product.coupon,
                "arg5": product.pricing.get("Discounted_Price"),
                "arg6": product.url
            }
        return self.email_content.format(**kwargs)

    # reading the user config to determine how often bot runs
    def read_schedule(self):
        cmd_main = None  # represents m in "m -10"
        cmd_param = None  # represents -10 in "m -10"
        descr = None  # Describes the schedule set in settings.json
        sched = None  # Returns a python schedule object to run job
        for chars in self.cmd_schedule:
            if '-' in chars:
                cmd_param = chars
            else:
                cmd_main = chars

        if cmd_main == "dly" and cmd_param is None:
            descr = "Run everyday at 12:00 AM"
            sched = schedule.every().day.at("00:00").do(self.sendmail)

        elif cmd_main == "dly" and cmd_param is not None:
            interval = cmd_param[1:]
            descr = f"Run everyday at {interval}"
            sched = schedule.every().day.at(interval).do(self.sendmail)

        elif cmd_main == "d" and cmd_param is None:
            descr = "Run everyday at the time the container is started"
            sched = schedule.every().day.do(self.sendmail)

        elif cmd_main == "d" and cmd_param is not None:
            interval = int(cmd_param[1:])
            descr = f"Run every {interval} days"
            sched = schedule.every(interval).days.do(self.sendmail)

        elif cmd_main == "h" and cmd_param is None:
            descr = "Runs every hour"
            sched = schedule.every().hour.do(self.sendmail)

        elif cmd_main == "h" and cmd_param is not None:
            interval = int(cmd_param[1:])
            descr = f"Run every {interval} hours"
            sched = schedule.every(interval).hours.do(self.sendmail)

        elif cmd_main == "m" and cmd_param is None:
            descr = "Runs every minute"
            sched = schedule.every().minute.do(self.sendmail)

        elif cmd_main == "m" and cmd_param is not None:
            interval = int(cmd_param[1:])
            descr = f"Run every {interval} minutes"
            sched = schedule.every(interval).minutes.do(self.sendmail)
        return {"Description": descr, "Sched-Variable": sched}


# Function to calulate the discounted price if coupon was detected on Amazon
def calc_discount(price: float, coupon: str):
    if "%" in coupon:
        index = coupon.find("%")
        coupon_val = float(coupon[0:index]) / 100
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


# Function that reads the html templaet for email fucntion
def get_mail_template():
    template = codecs.open("./app/mail_template.html", 'r')
    return template.read()


# Defining a function that get the configuration from json file
def get_configs():
    with open(json_path, "r") as json_file:
        configs = json.load(json_file).get("Tracker_Configuration")
        configs["bot_passwd"] = "Kooltron2004!"
        json_file.close()
        return configs


# Defining a function that gets the product list from json file
def get_prod_list():
    with open(json_path, "r") as json_file:
        listings = json.load(json_file).get("Products_Tracking")
        json_file.close()
    return listings


# Defining the browser header to bypass bot verification
def get_request_header():
    with open(json_path, "r") as json_file:
        user_agents = json.load(json_file).get("Browser_User_Agents")
        user_agent = random.choice(user_agents)
        header = {
            'authority': 'www.amazon.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': user_agent,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }
        json_file.close()
    return header


if __name__ == '__main__':
    amazon_scraper = Amazon_Tracker()
    amazon_scraper.run()
    while True:
        schedule.run_pending()
        sleep(1)
