import pyodbc
import pandas as pd
import plotly.express as px
from datetime import date
import urllib.request
import json

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-H4AEIGK;'
                      'Database=PSN;')

f = open("demofile.txt", "r")
def newdb():
    cursor = conn.cursor()
    for x in f:
        sp = x.split(",",1)
        game = sp[0]
        price = sp[1]
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
            name2 = name.replace("-", '').replace("’", '').replace("®",'').replace("'",'')
            today = date.today().strftime('%Y-%m-%d')
            img = str(api["images"][0]["url"])
            string = "CREATE TABLE " +"[" + name2 +"] " +"( cena FLOAT NOT NULL,data DATE NOT NULL, url VARCHAR(2048) NOT NULL, img VARCHAR(2048) NOT NULL, )"
            string2 ="[" + name2 +"] " +  "VALUES ("+ price2 +  ",'" + today + "'" + ",'https://store.playstation.com/pl-pl/product/"+ game +"','"+img+"')"
            try:
                cursor.execute(string + '''INSERT INTO ''' + string2)
            except:
                cursor.execute('''INSERT INTO ''' + string2)
            conn.commit()

def graph():
    cursor = conn.cursor()
    for x in f:
        sp = x.split(",", 1)
        game = sp[0]
        price = sp[1]
        url = "https://store.playstation.com/store/api/chihiro/00_09_000/container/PL/pl/100/" + game
        with urllib.request.urlopen(url) as url:
            api = json.loads(url.read())
            try:
                name = str(api["default_sku"]["entitlements"][0]["name"])
            except:
                name = str(api["default_sku"]["eligibilities"][0]["name"])
            name2 = name.replace("-", '').replace("’", '').replace("®", '').replace("'",'')
        cursor.execute('''
                            Select * from 
                            '''+ " [" +name2+ "]")
        rows = cursor.fetchall()

        df = pd.DataFrame([[ij for ij in i] for i in rows])
        df.rename(columns={0: 'cena', 1: 'data', 2: 'url', 3: 'img'}, inplace=True);
        df = df.sort_values(['data'], ascending=[1]);

        fig = px.line(df, x="data", y="cena", title=name2)
        fig.show()

graph()




