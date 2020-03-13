import os

import psycopg2 as psycopg2
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import urllib.request
import json
import cv2
from apscheduler.schedulers.blocking import BlockingScheduler
import re

conn = psycopg2.connect(user=os.environ["user"],
                    password=os.environ["passwd"],
                    host=os.environ["host"],
                    port=os.environ["port"],
                        database=os.environ["database"],)

f = open("demofile.txt", "r")
def newdb():
    cursor = conn.cursor()
    conn.autocommit = True
    for x in f:
        sp = x.split(",",1)
        game = sp[0]
        url = "https://store.playstation.com/store/api/chihiro/00_09_000/container/PL/pl/100/" + game
        with urllib.request.urlopen(url) as url:
            api = json.loads(url.read())
            try:
                price1 = api["default_sku"]["rewards"][0]["display_price"]
            except:
                price1 = api["default_sku"]["display_price"]
            price2 = str(float(price1[:-2].replace(',', '.')))
            try:
                name = str(api["default_sku"]["entitlements"][0]["name"])
            except:
                name = str(api["default_sku"]["eligibilities"][0]["name"])
            now = datetime.now()
            today = now.strftime("%d/%m/%Y %H:%M:%S")
            print(today)
            img = str(api["images"][0]["url"])
            string = "CREATE TABLE "  + re.sub(r'\W+', '', name) +"( cena FLOAT NOT NULL,data TIMESTAMP NOT NULL, url VARCHAR(2048) NOT NULL, img VARCHAR(2048) NOT NULL);"
            string2 = re.sub(r'\W+', '', name)   +  "(cena, data, url, img) VALUES ( "+ price2 +  ",'" + today + "'" + ",'https://store.playstation.com/pl-pl/product/"+ game +"','"+img+"')"
            try:
                cursor.execute(string + ''' INSERT INTO ''' + string2)
                conn.commit()
            except psycopg2.Error:
                cursor.execute('''INSERT INTO ''' + string2)
            conn.commit()

def graph():
    cursor = conn.cursor()
    for x in f:
        sp = x.split(",", 1)
        game = sp[0]
        url = "https://store.playstation.com/store/api/chihiro/00_09_000/container/PL/pl/100/" + game
        with urllib.request.urlopen(url) as url:
            api = json.loads(url.read())
            try:
                name = str(api["default_sku"]["entitlements"][0]["name"])
            except:
                name = str(api["default_sku"]["eligibilities"][0]["name"])
        cursor.execute('''Select * from ''' + re.sub(r'\W+', '', name)  + ";")
        rows = cursor.fetchall()

        df = pd.DataFrame([[ij for ij in i] for i in rows])
        df.rename(columns={0: 'cena', 1: 'data', 2: 'url', 3: 'img'}, inplace=True);
        df = df.sort_values(['data'], ascending=[1]);

        fig = px.line(df, x="data", y="cena", title=name)
        # fig.show()
        img = fig.to_image()
        nparr = np.fromstring(img, np.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cv2.imshow(name,img_np)
        cv2.waitKey(100)
    cv2.waitKey(0)


scheduler = BlockingScheduler()
scheduler.add_job(newdb, 'interval', hours=1)
scheduler.start()




