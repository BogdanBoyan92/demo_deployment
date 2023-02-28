from flask import Flask, request, jsonify
import os
import pickle
from sklearn.model_selection import cross_val_score
import pandas as pd
import sqlite3
from flask_sqlalchemy import SQLAlchemy


os.chdir(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True
ruta_bd = '/data/advertising.db'
conexion = sqlite3.connect(ruta_bd)



@app.route("/", methods=['GET'])
def hello():
    return "Bienvenido a mi API del modelo advertising"

# 1. Endpoint que devuelva la predicción de los nuevos datos enviados mediante argumentos en la llamada
@app.route('/v2/predict', methods=['GET'])
def predict():
    model = pickle.load(open('data/advertising_model','rb'))

    tv = request.args.get('tv', None)
    radio = request.args.get('radio', None)
    newspaper = request.args.get('newspaper', None)

    if tv is None or radio is None or newspaper is None:
        return "Missing args, the input values are needed to predict"
    else:
        prediction = model.predict([[tv,radio,newspaper]])
        return "The prediction of sales investing that amount of money in TV, radio and newspaper is: " + str(round(prediction[0],2))

# 2. Endpoint que almacena los datos en una base de datos, creacion de la base de datos



@app.route('/v2/ingest_data', methods=['POST'])
def ingest_data():
        tv = request.json['tv']
        radio = request.json['radio']
        newspaper = request.json['newspaper']
        conexion = sqlite3.connect('data/advertising.db')
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO campaña (tv, radio, newspaper) VALUES (?, ?, ?)", (tv, radio, newspaper))
        conexion.commit()
        conexion.close()




# 3. Posibilidad de entrenar el modelo con los nuevos datos añadidos a la base de datos

@app.route('/v2/retrain', methods=['POST'])
def retrain():
    
    modelo_entrenado = pickle.load(open('data/advertising_model','rb'))

    data = request.get_json()
    tv = [d['tv'] for d in data]
    radio = [d['radio'] for d in data]
    newspaper = [d['newspaper'] for d in data]

    nuevo_modelo = modelo_entrenado.fit(X=[tv, radio, newspaper], y=None)

    with open('modelo_entrenado.pkl', 'wb') as file:
        pickle.dump(nuevo_modelo, file)

    return jsonify({'Mensaje': 'Modelo entrenado correctamente'})





app.run()