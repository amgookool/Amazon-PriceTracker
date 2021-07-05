from bs4 import BeautifulStoneSoup as soup
import json
import requests
import smtplib
import time


class Amazon_item:
    def __init__(self, prod_search, prod_url, desired_price):
        self.product = prod_search
        self.url = prod_url
        self.desired_price = desired_price
    def track_products(self):
        pass


products_tracking=[]
with open('Track.json', 'r') as prod_list:
    track_products = json.load(prod_list).get("Products_Tracking")
    for item in track_products:
        what_product = item.get("name")
        product_url = item.get("url")
        product_desired_price = item.get("desired_price")
        prod_dict = {
            what_product: {
                "URL": product_url,
                "Desired Price": product_desired_price
            }}
        products_tracking.append(prod_dict)



with open("Config.json", 'r') as config:
    tracker_configs = json.load(config)
    bot_email = tracker_configs.get("from_email")
    b_email_passwd = tracker_configs.get("password")
    send_to = tracker_configs.get("to_email")
    checking_period = tracker_configs.get("check_period")
