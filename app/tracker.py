from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup as Soup
from email.mime.text import MIMEText
from dotenv import load_dotenv
from time import sleep
import requests
import schedule
import smtplib
import logging
import json
import ssl
import os

logs_format = "%(asctime)s | %(levelname)s | %(message)s"

logging.basicConfig(level=logging.DEBUG, encoding="utf-8",
                    format=logs_format, datefmt="%d-%b-%y %H:%M:%S")


def job():
    logging.info("Starting Scraping Job")
    bot = Price_tracker()
    bot.send_mail()


class Amazon_item:
    coupon = None
    headers = {
        'authority': 'www.amazon.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    def __init__(self, prod_url):
        logging.info(
            "Sending request to Splash javaascript rendering container")
        request = requests.get(
            "http://splash-renderer:8050/render.html",headers=self.headers, params={"url": prod_url, "wait": 3})
        self.scraper = Soup(request.text, "lxml")

    @property
    def name(self):
        head_element = self.scraper.find("h1", id="title")
        prod_name = head_element.find("span", id="productTitle").text.split()
        return " ".join(prod_name)

    @property
    def pricing(self):
        amz_price = None
        price_element = self.scraper.find("div", id="price")
        if price_element is not None:
            try:
                amz_price = float(price_element.find("span", id="priceblock_saleprice").text[1:])
            except Exception:
                pass
            try:
                amz_price = float(price_element.find("span", id="priceblock_ourprice").text[1:])
            except Exception:
                pass
            try:
                amz_price = float(price_element.find("span",id= "priceblock_dealprice").text[1:])
            except Exception as e:
                pass
            coupon_element = self.scraper.find('tr', class_="couponFeature")
            if coupon_element is None:
                return {"Amazon_Price": amz_price, "Discounted_Price": None}
            else:
                self.coupon = coupon_element.find('span', class_="a-color-success").text.split()[3]
                return calc_discount(price=amz_price, coupon=self.coupon)
        else:
            return None

    @property
    def image_url(self):
        img_container = self.scraper.find('div', id="imgTagWrapperId")
        img_tag = img_container.find('img')
        return img_tag.get("src")


email_content = """\
        <html>
        <body>
            <h2 style="color:red;font-weight:bold;">{arg1}</h2>
            <img src="{arg2}" alt="Failed to load product image">
            <h4>Amazon Price: <span style="color:red;">${arg3}</span></h4>
            <h4>Coupon Detected: <span style="color:red;">{arg4}</span></h4>
            <h4>Discounted Price: <span style="color:red;">${arg5}</span></h4>
            <br><br>
            <a style="background-color:red; color:white; padding: 20px; text-decoration:None;" href="{arg6}"> View Product</a>
        </body>
        </html>   
        """


class Price_tracker:

    def __init__(self):
        load_dotenv()
        logging.info("Reading Configuration from .env file")
        self.email = os.environ.get("sender_email")
        self.password = os.environ.get("sender_pswd")
        self.receiver = os.environ.get("receiver_email")
        self.products = []
        with open('./app/Track.json', 'r') as prod_list:
            logging.info("Reading the Track.json file")
            track_products = json.load(prod_list).get("Products_Tracking")
            for index, item in enumerate(track_products):
                what_product = item.get("name")
                product_url = item.get("url")
                desired_price = item.get("desired_price")
                product_dict = {
                    "product" + str(index): {
                        "Name": what_product,
                        "URL": product_url,
                        "Desired_price": desired_price
                    }
                }
                self.products.append(product_dict)
        prod_list.close()

    def send_mail(self):
        for product in self.products:
            message = MIMEMultipart("alternative")
            message["From"] = str(self.email)
            message["To"] = self.receiver
            mail_content = ""
            item = product.values()
            for info in item:
                _name = info.get("Name")
                message["Subject"] = "Price Alert: " + _name
                _url = info.get("URL")
                desired_price = info.get("Desired_price")
                logging.info(f"Starting Scrape for {_name}")

                _product = Amazon_item(_url)

                if _product.pricing is None:
                    logging.info(f"{_name} product is currently out of stock")
                    break

                elif _product.pricing.get("Discounted_Price") is None and _product.pricing.get(
                        "Amazon_Price") <= desired_price:
                    kwargs = {"arg1": _product.name, "arg2": _product.image_url,
                              "arg3": _product.pricing.get("Amazon_Price"),
                              "arg4": "None", "arg5": _product.pricing.get("Amazon_Price"), "arg6": _url}
                    mail_content = email_content.format(**kwargs)

                elif _product.pricing.get("Discounted_Price") is None and _product.pricing.get(
                        "Amazon_Price") > desired_price:
                    logging.info(
                        f"There are no coupons and the Amazon price is > desired price for {_name}")
                    break

                elif _product.pricing.get("Amazon_Price") <= desired_price or _product.pricing.get(
                        "Discounted_Price") <= desired_price and _product.pricing.get("Discounted_Price") is not None:
                    kwargs = {"arg1": _product.name, "arg2": _product.image_url,
                              "arg3": _product.pricing.get("Amazon_Price"),
                              "arg4": _product.coupon, "arg5": _product.pricing.get("Discounted_Price"), "arg6": _url}
                    mail_content = email_content.format(**kwargs)

                elif _product.pricing.get("Amazon_Price") > desired_price or _product.pricing.get(
                        "Discounted_Price") > desired_price:
                    logging.info(
                        f"Both Amazon price and Coupon Discounted price is > desired price for {_name}")
                    break
                content = MIMEText(mail_content, 'html')
                message.attach(content)
                context = ssl.create_default_context()

                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as mail_server:
                    logging.info(f"Sending email for {_name} product")
                    mail_server.login(self.email, self.password)
                    mail_server.sendmail(
                        self.email, self.receiver, message.as_string())
        return


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


def tracker_init():
    load_dotenv()
    logging.info("Initializing Amazon Price Tracker")
    cmd_param = None
    cmd_main = None
    sched = None
    usr_time = os.environ.get("sched_time").split()
    for item in usr_time:
        if "-" in item:
            cmd_param = item
        else:
            cmd_main = item

    if cmd_main == "dly" and cmd_param is None:
        logging.info("Schedule: Run everyday at 12:00 AM")
        sched = schedule.every().day.at("00:00").do(job)

    elif cmd_main == "dly" and cmd_param is not None:
        interval = cmd_param[1:]
        logging.info(f"Schedule: Run everyday at {interval}")
        sched = schedule.every().day.at(interval).do(job)

    elif cmd_main == "d" and cmd_param is None:
        logging.info(
            "Schedule: Run everyday at the time the container is started")
        sched = schedule.every().day.do(job)

    elif cmd_main == "d" and cmd_param is not None:
        interval = int(cmd_param[1:])
        logging.info(f"Schedule: Run every {interval} days")
        sched = schedule.every(interval).days.do(job)

    elif cmd_main == "h" and cmd_param is None:
        logging.info("Schedule: Runs every hour")
        sched = schedule.every().hour.do(job)

    elif cmd_main == "h" and cmd_param is not None:
        interval = int(cmd_param[1:])
        logging.info(f"Schedule: Run every {interval} hours")
        sched = schedule.every(interval).hours.do(job)

    elif cmd_main == "m" and cmd_param is None:
        logging.info("Schedule: Runs every minute")
        sched = schedule.every().minute.do(job)

    elif cmd_main == "m" and cmd_param is not None:
        interval = int(cmd_param[1:])
        logging.info(f"Schedule: Run every {interval} minutes")
        sched = schedule.every(interval).minutes.do(job)
    return sched



bot_sched = tracker_init()
logging.info("Amazon Price tracker is now active")

while True:
    schedule.run_pending()
    sleep(1)
