from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup as Soup
from email.mime.text import MIMEText
from dotenv import load_dotenv
from time import sleep
import schedule
import requests
import smtplib
import json
import ssl
import os


def job():
    bot = Price_tracker()
    bot.send_mail()


class Amazon_item:
    coupon = None

    def __init__(self, prod_url):
        request = requests.get(
            "http://splash-renderer:8050/render.html", params={"url": prod_url, "wait": 3})
        self.scraper = Soup(request.text, "lxml")

    @property
    def name(self):
        head_element = self.scraper.find("h1", id="title")
        prod_name = head_element.find("span", id="productTitle").text.split()
        return " ".join(prod_name)

    @property
    def pricing(self):
        price_element = self.scraper.find("div", id="price")
        if price_element is not None:
            amz_price = float(price_element.find(
                "span", id="priceblock_ourprice").text[1:])
            coupon_element = self.scraper.find('tr', class_="couponFeature")
            if coupon_element is None:
                return {"Amazon_Price": amz_price, "Discounted_Price": None}
            else:
                self.coupon = coupon_element.find(
                    'span', class_="a-color-success").text.split()[3]
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
        self.email = os.environ.get("sender_email")
        self.password = os.environ.get("sender_pswd")
        self.receiver = os.environ.get("receiver_email")
        self.products = []
        with open('./app/Track.json', 'r') as prod_list:
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

                _product = Amazon_item(_url)

                if _product.pricing is None:
                    print(f"No Price for {_name}")
                    break

                elif _product.pricing.get("Discounted_Price") is None and _product.pricing.get(
                        "Amazon_Price") <= desired_price:
                    kwargs = {"arg1": _product.name, "arg2": _product.image_url,
                              "arg3": _product.pricing.get("Amazon_Price"),
                              "arg4": "None", "arg5": _product.pricing.get("Amazon_Price"), "arg6": _url}
                    mail_content = email_content.format(**kwargs)

                elif _product.pricing.get("Discounted_Price") is None and _product.pricing.get(
                        "Amazon_Price") > desired_price:
                    break

                elif _product.pricing.get("Amazon_Price") <= desired_price or _product.pricing.get(
                        "Discounted_Price") <= desired_price and _product.pricing.get("Discounted_Price") is not None:
                    kwargs = {"arg1": _product.name, "arg2": _product.image_url,
                              "arg3": _product.pricing.get("Amazon_Price"),
                              "arg4": _product.coupon, "arg5": _product.pricing.get("Discounted_Price"), "arg6": _url}
                    mail_content = email_content.format(**kwargs)

                elif _product.pricing.get("Amazon_Price") > desired_price or _product.pricing.get(
                        "Discounted_Price") > desired_price:
                    break
                content = MIMEText(mail_content, 'html')
                message.attach(content)
                context = ssl.create_default_context()

                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as mail_server:
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
        print("working")
        sched = schedule.every().day.at("00:00").do(job)

    elif cmd_main == "dly" and cmd_param is not None:
        interval = cmd_param[1:]
        sched = schedule.every().day.at(interval).do(job)

    elif cmd_main == "d" and cmd_param is None:
        sched = schedule.every().day.do(job)

    elif cmd_main == "d" and cmd_param is not None:
        interval = int(cmd_param[1:])
        sched = schedule.every(interval).days.do(job)

    elif cmd_main == "h" and cmd_param is None:
        sched = schedule.every().hour.do(job)

    elif cmd_main == "h" and cmd_param is not None:
        interval = int(cmd_param[1:])
        sched = schedule.every(interval).hours.do(job)

    elif cmd_main == "m" and cmd_param is None:
        sched = schedule.every().minute.do(job)

    elif cmd_main == "m" and cmd_param is not None:
        interval = int(cmd_param[1:])
        sched = schedule.every(interval).minutes.do(job)
    print(sched)
    return sched


bot_sched = tracker_init()
print("Amazon Price tracker is now active")

while True:
    schedule.run_pending()
    sleep(1)
