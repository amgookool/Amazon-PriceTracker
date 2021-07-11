This program uses Track.json and .env files for its operation. The Track.json file is responsible for setting up the products you wish to track. The required keys for the Track.json file are:
  *"name": str(description)
  
  *"url": str(url) 
  
  *"desired_price": float

The .env file is used to setup the program's sender's email and password and receiver's email address. Additionally, it also includes a scheduling feature to set how often you want the program to check the products. These are the following keys available in the .env file 
  * sender_email - email address bot uses to send notification
  * sender_pswd - password for the sender email account
  * receiver_email - email the notification is being sent too
  * scheduling - the timing that the scraping feature is executed

Note: The sender's email address should be using gmail and should allow less secure apps feature to access its smtp services

Note: str arguments for options are given in ["*"]
-------------------------------------------------------------------------------------------
Daily execution at a certain time (24 hour clock) ["dly"]
      -- Allows scrape feature to occur everyday at that particular time
      -- Default parameter is set to ["-00:00"] or 12:00 AM
      -> [-xx:xx] Optional Parameter: 24-hour clock format
      -- examples : 
            ["dly"] run every day at 12:00 AM 
            ["dly -13:20"] run every day at 1:20 PM
--------------------------------------------------------------------------------------------            
    * By day[d]
      -> [-int] Optional Parameter: integer
      -- Allows scrape feature to occur every -x days
      -- Default parameter is set to scrape every day at the time the container is run
      -- examples : 
            ["d"] run every day
            ["d -2"] run every 2 days
---------------------------------------------------------------------------------------------              
    * By hour[h]
      -> [str] Optional Parameter: integer
      -- Allows scrape feature to occur every x hours 
      -- Default parameter is set to scrape every hour at the time the container is run
      -- examples : 
            ["h"] run every hour
            ["h -5"] run every 5 hours 
-----------------------------------------------------------------------------------------------                    
    * By minute[m]
      -> [str] Optional Parameter: integer
      -- Allows scrape feature to occcur every x minutes 
      -- Default parameter is set to scrape every minute at the time the container is run
      -- examples : 
            ["m"] run on every minute
            ["m -3"] run every 3 minutes