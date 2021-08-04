- [**Amazon-PriceTracker**](#amazon-pricetracker)
- [**Settings.json File**](#settingsjson-file)
  - [**_Tracker_Configuration_ Property**](#tracker_configuration-property)
    - [**SMTP Mailing Sub-Properties**](#smtp-mailing-sub-properties)
    - [**Schedule Sub-Property**](#schedule-sub-property)
  - [**_Products_Tracking_ Property**](#products_tracking-property)
  - [**_Browser_User_Agents_ Property**](#browser_user_agents-property)
- [**Installation and Usage**](#installation-and-usage)
  - [**Installation**](#installation)
  - [**Usage**](#usage)
    - [**Changes in the _Tracker_Configuration_ Property**](#changes-in-the-tracker_configuration-property)
    - [**Changes in the _Products_Tracking_ and Browser_User_Agents Properties**](#changes-in-the-products_tracking-and-browser_user_agents-properties)
    - [__Useful Commands__](#useful-commands)
---
# **Amazon-PriceTracker**
**A containerized Python application that web-scrapes an amazon product webpage for its price and notifies the user if the web-scrapped price is less than or equal to the user's desired price.**

**The application uses a Simple Mail Transfer Protocol (SMTP) server defined by the user to notify the user of the price changes.**

**The application features a scheduling property the user defines that executes the web-scraping job of the application. The scheduling values are shown in the scheduling sub-property section.**

**The addition of products and application configurations are done in the _Settings.json_ file.**


***

# **[Settings.json File](./app/Settings.json)**
**The Settings.json file is used to configure and add the products the user wants to scrape.There are 3 properties associated in this file for its operation:**
* **Tracker_Configuration**
* **Products_Tracking**
* **Browser_User_Agents**

## **_Tracker_Configuration_ Property**
**This property consists of sub-properties for configuring the SMTP mailing requirements (SMTP Mailing Sub-properties) and scheduling web scrapes (Scheduling Sub-Properties).**
***

### **SMTP Mailing Sub-Properties**

* > **_"smtp_server" : "smtp.server.here"_**
  **--> Specifies SMTP server address which the tracker (SENDER) email belongs too.**

* > **_"smtp_port" : integer_**
  **--> Specifies the port which the SMTP server uses to send and receive emails.**
  
* > **_"bot_email" : "Sender Email address"_**
  **--> Refers to the Tracker (Sender) email address**
  
* > **_"bot_passwd" : "Sender Email Password"_**
  **--> Refers to the password for the Tracker Email address**
  
* > **_"receiver_email" : "Receiver Email address"_**
  **--> Refers to the password for the Tracker Email address**

eg. Google (Gmail) Server is given as : 
```json
  "smtp_server"     : "smtp.gmail.com",
  "smtp_port"       : 465,
  "bot_email"       : "myemail@gmail.com",
  "bot_passwd"      : "email_password",
  "receiver_email"  : "receiver@whatever.com" 
```
**Note: Most SMTP servers require you to allow less secure apps to be turned on.**
**A list of smtp server providers can be found [here](https://www.arclab.com/en/kb/email/list-of-smtp-and-pop3-servers-mailserver-list.html).**

***
### **Schedule Sub-Property**
Refers to how often the price scraping feature occurs. The following configurations are used for settings the schedule.

* #### **Daily Scrape at a certain time (24 hour clock)**
    * Description: Allows scrape feature to occur everyday at that particular time.
    * Main Character --> "**dly**"
    * Optional Character --> "**-xx:xx**"
      * Default is set to "**-00:00**"
    * Examples :
      * > ```"schedule":"dly" ``` --> Run every day at 12:00AM
      * > ```"schedule":"dly -14:20"``` --> Run every day at 2:20 PM

* #### **Scrape by Day(s)**
  * Description --> Allows scrape feature to occur every (-x) day(s).
  * Main Character --> "**d**"
  * Optional Character --> "**-int**"
    * Default is set to scrape every day at the time the container is active.
  * Examples: 
    * > ```"schedule":"d"``` --> Run every day
    * > ```"schedule":"d -4"``` --> Run every 4 days

* #### **Scrape by Hour(s)**
  * Description --> Allows scrape feature to occur every (-x) hour(s).
  * Main Character --> "**h**"
  * Optional Character --> "**-int**"
    * Default is set to scrape every hour at the time the container is active.
  * Examples: 
    * > ```"schedule":"h"``` --> Run every hour
    * > ```"schedule":"h -6"``` --> Run every 6 hours

* #### **Scrape by Minute(s)**
  * Description --> Allows scrape feature to occcur every (-x) minute(s) .
  * Main Character --> "**m**"
  * Optional Character --> "**-int**"
    * Default is set to scrape every minute at the time the container is active.
  * Examples: 
    * > ```"schedule":"m"``` --> Run every minute
    * > ```"schedule":"m -27"``` --> Run every 27 minutes
***        

## **_Products_Tracking_ Property**
**The products tracking property in the Settings.json file is where the user adds the amazon products they want to keep track of.**
 
Each product requires three fields to be filled out for the proper operation of the application. These are: 
* ["name"](./app/Settings.json)
* ["url"](./app/Settings.json)
* ["desired_price"](./app/Settings.json)

Example format of a single product in the [_Products_Tracking_](./app/Settings.json) section in [Settings.json](./app/Settings.json) file

```json
{
    "name": "Custom Product Tracking Name",
    "url" : "Amazon Product Webpage URL",
    "desired_price" : 120.34
}
```

Example format of multiple products in the [_Products_Tracking_](./app/Settings.json) section in [Settings.json](./app/Settings.json) file

```json
{
  "name":"Product 1 Name",
  "url" :"Product 1 URL",
  "desired_price" : 20.00
},
{
  "name": "Product 2 Name",
  "url": "Product 2 URL",
  "desired_price": 39.34
}
```
**Note: In the [_Products_Tracking_](./app/Settings.json) section, the last product entry (shown by ' ] ') should not have a comma (,) at the end. Additionally, each product enrty is seperated by a comma (,)**

---
## **_Browser_User_Agents_ Property**
**This property is a list containing different device user-agents for a web browser header.** 

This list randomly selects browser headers when executing a scraping job to avoid blocks from the Amazon website.

**Additional Browser User-Agents can be found [here](https://deviceatlas.com/blog/list-of-user-agent-strings)**


# **Installation and Usage**
## **Installation**
**This application requires both Docker and Docker-Compose to be installed on the host machine.**

1. Refer to **[Docker](https://docs.docker.com/docker-for-windows/install/)** webpage for install instructions for your Operating System.

1. Once Docker and Docker Compose are installed, clone the **[Amazon-PriceTracker](https://github.com/amgookool/Amazon-PriceTracker)** repository or download the zip file. 

1. Setup your Configurations in the [Settings.json](./app/Settings.json) file.

1. Navigate to the root location of the repository directory using a Command Line Interface (CLI).

1. Type following command to build and start the Amazon-PriceTracker on CLI 
```bash
docker-compose up -d --build
```
## **Usage**
### **Changes in the [_Tracker_Configuration_](./app/Settings.json) Property**

The container insatance should be stopped if making changes in the **_Tracker_Configuration_** Section. If container was not stopped, changes made would occur on the application.


### **Changes in the [_Products_Tracking_ and Browser_User_Agents](./app/Settings.json) Properties**

The container instance can be active if making changes to the **_Products_Tracking_** or **_Browser_User_Agents_** sections of the application 

### __Useful Commands__
To check status of the containerized application... type the following command on CLI

```bash
docker-compose ps
```
To stop the container... type the following command on CLI
```bash
docker-compose stop app
```
To start the container... type the following command on CLI
```bash
docker-compose start app
```
To delete the container... type the following command on CLI
```bash
docker-compose rm app
```
To delete the image that the container is based on... type the following command on CLI
```bash
docker rmi amazon-pricetracker_app
```