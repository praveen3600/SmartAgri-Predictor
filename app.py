from flask import Flask, render_template, url_for, request, redirect, session
import sqlite3
import os
import time
import base64
import numpy as np
import pandas as pd
import requests
import config
import pickle
import io
from PIL import Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import base64
# pip install scikit-learn==1.2.2

forest = pickle.load(open('models/yield_rf.pkl', 'rb'))  # yield

model = pickle.load(open('models/classifier.pkl','rb'))
ferti = pickle.load(open('models/fertilizer.pkl','rb'))

cr = pickle.load(open('models/RandomForest.pkl', 'rb'))

def weather_fetch(city_name):
    """
    Fetch and returns the temperature and humidity of a city
    :params: city_name
    :return: temperature, humidity
    """
    api_key = config.weather_api_key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()
    print('vgj,hDS|m n')
    print(response)

    if x["cod"] != "404":
        y = x["main"]

        temperature = round((y["temp"] - 273.15), 2)
        humidity = y["humidity"]
        return temperature, humidity
    else:
        return None

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

command = """CREATE TABLE IF NOT EXISTS user(name TEXT, password TEXT, mobile TEXT, email TEXT)"""
cursor.execute(command)

command = """CREATE TABLE IF NOT EXISTS seller(Id INTEGER PRIMARY KEY AUTOINCREMENT, crop TEXT, cost TEXT, district TEXT, image BLOB)"""
cursor.execute(command)

command = """CREATE TABLE IF NOT EXISTS buyer(Id INTEGER PRIMARY KEY AUTOINCREMENT, crop TEXT, cost TEXT, district TEXT, image BLOB)"""
cursor.execute(command)

command = """CREATE TABLE IF NOT EXISTS community_query(Id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, image BLOB, query TEXT)"""
cursor.execute(command)

command = """CREATE TABLE IF NOT EXISTS community_answer(query_id TEXT, username TEXT, answer TEXT)"""
cursor.execute(command)

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/userlog', methods=['GET', 'POST'])
def userlog():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']

        query = "SELECT * FROM user WHERE name = '"+name+"' AND password= '"+password+"'"
        cursor.execute(query)

        result = cursor.fetchone()

        if result:
            session['username'] = result[0]
            return redirect(url_for('market'))
        else:
            return render_template('index.html', msg='Sorry, Incorrect Credentials Provided,  Try Again')

    return render_template('index.html')


@app.route('/userreg', methods=['GET', 'POST'])
def userreg():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']
        mobile = request.form['phone']
        email = request.form['email']

        command = """CREATE TABLE IF NOT EXISTS user(name TEXT, password TEXT, mobile TEXT, email TEXT)"""
        cursor.execute(command)

        cursor.execute("INSERT INTO user VALUES ('"+name+"', '"+password+"', '"+mobile+"', '"+email+"')")
        connection.commit()

        return render_template('index.html', msg='Successfully Registered')
    
    return render_template('index.html')

@app.route('/fertilizer', methods=['GET', 'POST'])
def fertilizer():
    if request.method == 'POST':

        temp = request.form.get('temp')
        humi = request.form.get('humid')
        mois = request.form.get('mois')
        soil = request.form.get('soil')
        crop = request.form.get('crop')
        nitro = request.form.get('nitro')
        pota = request.form.get('pota')
        phosp = request.form.get('phos')
        input = [int(temp),int(humi),int(mois),int(soil),int(crop),int(nitro),int(pota),int(phosp)]

        res = ferti.classes_[model.predict([input])]
        print(f"RES   {res}")

        return render_template('fertilizer.html', prediction=res[0])
    else:
        return render_template('fertilizer.html', prediction="Something try again")

##    return render_template('fertilizer.html')

@app.route('/Yield', methods=['GET', 'POST'])
def Yield():
    if request.method == 'POST':
        state = request.form['stt']
        district = request.form['city']
        year = request.form['year']
        season = request.form['season']
        crop = request.form['crop']
        Temperature = request.form['Temperature']
        humidity = request.form['humidity']
        soilmoisture = request.form['soilmoisture']
        area = request.form['area']

        out_1 = forest.predict([[float(state),
                                 float(district),
                                 float(year),
                                 float(season),
                                 float(crop),
                                 float(Temperature),
                                 float(humidity),
                                 float(soilmoisture),
                                 float(area)]])
        out_yield="{:.2f}".format(out_1[0])
        print(out_yield)
        if float(area)== 0.0:
            out_yield=0
            ty=""
        elif 1 <= float(area) < 10:
            ty="Quintal"
        elif float(area) > 10:
            ty="Tons"
        return render_template('yield.html', prediction=out_yield, ty=ty)

    return render_template('yield.html')

@app.route('/crop', methods=['GET', 'POST'])
def crop():
    if request.method == 'POST':
        N = request.form['nitrogen']
        P = request.form['phosphorous']
        K = request.form['pottasium']
        ph = request.form['ph']
        rainfall = request.form['rainfall']
        temp = request.form['temperature']
        hum = request.form['humidity']
##        state = request.form['stt']
##        city = request.form['city']

##        if weather_fetch(city) != None:
##            temperature, humidity = weather_fetch(city)
        data = np.array([[N, P, K, temp, hum, ph, rainfall]])
        probabilities = cr.predict_proba(data)[0]
        print(probabilities)
        top_3_indices = np.argsort(probabilities)[::-1][:3]
        crop3 = cr.classes_[top_3_indices]
        prob3 = probabilities[top_3_indices]
        print(f"\n\n\n{crop3}\n\n\n")
        print(f"\n\n\n{prob3}\n\n\n")
        

        return render_template('crop.html', crop31=crop3[0],crop32=crop3[1],crop33=crop3[2],
                               prob31=prob3[0],prob32=prob3[1],prob33=prob3[2])
##        else:
##            return render_template('crop.html', msg="Some thing went wrong, try again")
    # prediciton=False
    return render_template('crop.html') 

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        try:
            city = request.form['city']
            # Fetch weather data using OpenWeatherMap API
            weather_data = weather_fetch(city)
            
            if weather_data:
                temp, humidity = weather_data
                rem = f"Temperature is {temp}°C, Humidity is {humidity}%"
                print(rem)
                return render_template('weather.html', city=city, temp=temp, humidity=humidity)
            else:
                return render_template('weather.html', msg="City not found. Try again.")
        except Exception as e:
            print(f"Error: {e}")
            return render_template('weather.html', msg="An error occurred. Try again.")
    return render_template('weather.html')


@app.route('/market')
def market():
    url = "https://www.napanta.com/market-price/karnataka/bangalore/bangalore"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the table with class "table table-bordered table-striped"
    table = soup.find("table")
    if table:
        result = [['Commodity', 'Place', 'Variety', 'Maximum Price',	'Average Price', 'Minimum Price', 'Last Updated On']]
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if cells:
                d = [cell.get_text(strip=True) for cell in cells]
                result.append(d[:-1])
    return render_template('market.html', result=result)

@app.route('/logout')
def logout():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
