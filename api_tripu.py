import flask
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import nltk
import re
import string
import utilities as ut


app = Flask(__name__)
app.config["DEBUG"] = True

df=pd.read_csv("database.csv",encoding='UTF-8')

"""
La petición sería:
http://127.0.0.1:5000/expertos?ID=115 method: GET
"""
@app.route('/expertos', methods = ['GET'])
def expertos():
    args = request.args

    if 'ID' in args:
        user = args.get('ID', None, type=int)
                   
        if user is None:
            return "Error. Args empty"
        else:

            def RecomendacionExperto(Top, ID_usuario):
                df_salida = ut.automatizacion(user, df).copy()
    
                RecomendacionUsuario = ut.carga_datos_expertos(df_salida)[ID_usuario].sort_values(ascending=False)[1:Top]
    
                filtrado_expertos = pd.DataFrame()
                for id in RecomendacionUsuario.index:
                    filtrado_expertos = filtrado_expertos.append(df[df["user_id"]== id])
    
                return filtrado_expertos
            
            df_filtrado = RecomendacionExperto(10,user)
            recomendaciones = df_filtrado.to_dict('records')

            return jsonify(recomendaciones)

    else:
        return "Error in args"


"""
La petición sería:
http://127.0.0.1:5000/comunidad?ID=115 method: GET
"""
@app.route('/comunidad', methods = ['GET'])
def comunidad():
    args = request.args

    if 'ID' in args:
        user = args.get('ID', None, type=int)
                  
        if user is None:
            return "Error. Args empty"
        else:
            def RecomendacionUsuario(Top, ID_usuario):
                ID_usuario = ID_usuario - 1
                #database = df.copy()
                RecomendacionUsuario = ut.carga_datos(df).iloc[(-ut.carga_datos(df).iloc[:, ID_usuario]).argsort()[1:(Top+1)].values, ID_usuario]
                
                filtrado = pd.DataFrame()
                for id in RecomendacionUsuario.index:
                    filtrado = filtrado.append(df[df["user_id"]== id])
                
                return filtrado

            df_filtrado = RecomendacionUsuario(10,user)
            recomendaciones = df_filtrado.to_dict('records')
            
            return jsonify(recomendaciones)

    else:
        return "Error in args"




app.run()