import pandas as pd
import numpy as np
import nltk
import re
import string
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer


# FUNCIONES PARA EL ENDPOINT DE COMUNIDAD

def removeStopwords(text):
	"""Se eliminan palabras que carecen de significado
    
    Args: 
        text: Texto del que se desea eliminar las palabras sin significado.
        
    """
	
	stopw = nltk.corpus.stopwords.words('spanish')
	x = [w.strip() for w in text if w not in stopw]
	return x


def removePunctuation(text):
	"""Se eliminan signos de puntuación
    
    Args: 
        text: Texto del que se desea eliminar los signos de puntuación.
        
    """
	stopp = list(string.punctuation)
	stopp.append("''")
	stopp.append("")
	x = [w.strip() for w in text if w not in stopp]
	return x


def arrayToString(text):
	"""Se pasa de varias columnas a una sola
    
    Args: 
        text: 
        
    """
	x = ' '.join(text)
	return x

# Carga de datos

def carga_datos(database):

    df = database.copy()

    # Limpieza de datos

    # Modificar año de nacimiento a rangos de edad
    labels=['De55a65', 'De45a55', 'De35a45', 'De25a35', 'De18a25']
    df['year_birth'] = pd.cut(df['year_birth'], bins=[1957, 1967, 1977, 1987, 1997, 2005], labels=labels)
    df['year_birth'] = df['year_birth'].astype(str)

    # Elimino espacios en blanco de datos que me interesan para que sean una sola palabra
    df['area'] = df['area'].apply(lambda x: re.sub(' ', '', x))
    df['studies'] = df['studies'].apply(lambda x: re.sub(' ', '', x))

    # Unir varias columnas en una sola nueva con las palabras que me interesan para el modelo
    df['all_about_me'] = df['about_me'] + ', ' + df['mother_tongue'] + ', ' + df['area'] + ', ' + df['studies'] + ', ' + df['year_birth']

    # Tokenizar las palabras de la columna all_about_me para el modelo y eliminar stopwords y signos de puntuación 
    df['all_about_me'] = df['all_about_me'].apply(lambda x: nltk.word_tokenize(x))
    df['all_about_me'] = df['all_about_me'].apply(lambda x: removeStopwords(x))
    df['all_about_me'] = df['all_about_me'].apply(lambda x: removePunctuation(x))
    df['all_about_me'] = df['all_about_me'].apply(lambda x: arrayToString(x))

    # Defino el listado de opciones(usuarios) para elegir en el modelo
    listado = df['user_id']

    # Cálculo de la matriz de frecuencias de palabras
    vectorizer = CountVectorizer()
    MatrizFrecuencias = vectorizer.fit_transform(df['all_about_me'])

    # Cálculo término frecuencia inversa de documento (TfidfTransformer())
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(MatrizFrecuencias)

    # Cálculo matriz similitudes
    tdm = tfidf.transpose()
    dtm = tfidf
    Simil = dtm.dot(tdm)

    # Visualización de la matriz de similitudes
    SimilDF = pd.DataFrame(data = Simil.toarray(), index=listado.values,columns=listado.values)

    return SimilDF

# FUNCIONES PARA EL ENDPOINT DE EXPERTOS

# Funcion que utiliza el id recibido para crear una lista con los datos del usuario y un string del tipo de apoyo

def lista_datos(x, database):

    # database_copia = database.drop(['user_name', 'usersurname', 'email', 'password', 'pic', 'country', 'date', 'studies'],axis=1)
    user=database.loc[database["user_id"] == x]
    tipo_apoyo = user.support_type[x-1]
    lista_user=user.values.flatten().tolist()
    return lista_user, tipo_apoyo

# Función que utiliza como argumento el string de tipo de apoyo y filtra para devolver un dataframe

def tipo_apoyo(apoyo, database):
    if apoyo == 'Orientacion sobre temas legales':
        df_temas_legales = database[(database['support_type']=='Orientacion sobre temas legales')]
        df_temas_legales = df_temas_legales[df_temas_legales['expert']=='Si']

        return df_temas_legales

    elif apoyo == 'Orientacion sobre tramites':
        df_tramites = database[(database['support_type']=='Orientacion sobre tramites')]
        df_tramites = df_tramites[df_tramites['expert']=='Si']

        return df_tramites

    elif apoyo == 'Orientacion laboral':
        df_tramites_laborales = database[(database['support_type']=='Orientacion laboral')]
        df_tramites_laborales = df_tramites_laborales[df_tramites_laborales['expert']=='Si']

        return df_tramites_laborales

    else:
        df_emocional = database[(database['support_type']=='Emocional')]
        df_emocional = df_emocional[df_emocional['expert']=='Si']

        return df_emocional

# Función que toma como argumentos la lista de datos del usuario y el dataframe de expertos segun el tipo de apoyo y devuelve un df que va para el modelo

def filtro_idioma(datos_usuario,df_support):
    if ',' in datos_usuario[df_support.columns.get_loc('mother_tongue')]:
        datos_usuario[df_support.columns.get_loc('mother_tongue')] = [datos_usuario[df_support.columns.get_loc('mother_tongue')]]
        div_idioma = datos_usuario[df_support.columns.get_loc('mother_tongue')][0].split(', ')
        df_model = df_support[(df_support.mother_tongue.str.contains(div_idioma[0])) | (df_support.mother_tongue.str.contains(div_idioma[1]))]

    else:
        df_model = df_support[(df_support.mother_tongue.str.contains(datos_usuario[df_support.columns.get_loc('mother_tongue')]))]

    return df_model


def carga_datos_expertos(database):

    df = database.copy()

    # Limpieza de datos

    # Modificar año de nacimiento a rangos de edad
    labels=['De55a65', 'De45a55', 'De35a45', 'De25a35', 'De18a25']
    df['year_birth'] = pd.cut(df['year_birth'], bins=[1957, 1967, 1977, 1987, 1997, 2005], labels=labels)
    df['year_birth'] = df['year_birth'].astype(str)

    # Elimino espacios en blanco de datos que me interesan para que sean una sola palabra
    df['area'] = df['area'].apply(lambda x: re.sub(' ', '', x))
    df['studies'] = df['studies'].apply(lambda x: re.sub(' ', '', x))

    # Unir varias columnas en una sola nueva con las palabras que me interesan para el modelo
    if (df["support_type"].unique()[0] == 'Orientacion sobre temas legales'):
        df['all_about_me'] = df['area'] + ', ' + df['year_birth'] + ', ' + df['years_in'] + ', ' + df['working']
        
    elif (df["support_type"].unique()[0] == 'Orientacion sobre tramites'):
        df['all_about_me'] = df['area'] + ', ' + df['year_birth'] + ', ' + df['years_in'] + ', ' + df['working']
        
    elif (df["support_type"].unique()[0] == 'Orientacion laboral'):
        df['all_about_me'] = df['area'] + ', ' + df['working'] + ', ' + df['studies']
        
    else:
        df['all_about_me'] = df['area'] + ', ' + df['year_birth'] + ', ' + df['about_me'] + ', ' + df['gender']        
    

    # Tokenizar las palabras de la columna all_about_me para el modelo y eliminar stopwords y signos de puntuación 
    df['all_about_me'] = df['all_about_me'].apply(lambda x: nltk.word_tokenize(x))
    df['all_about_me'] = df['all_about_me'].apply(lambda x: removeStopwords(x))
    df['all_about_me'] = df['all_about_me'].apply(lambda x: removePunctuation(x))
    df['all_about_me'] = df['all_about_me'].apply(lambda x: arrayToString(x))

    # Defino el listado de opciones(usuarios) para elegir en el modelo
    listado = df['user_id']

    # Cálculo de la matriz de frecuencias de palabras
    vectorizer = CountVectorizer()
    MatrizFrecuencias = vectorizer.fit_transform(df['all_about_me'])

    # Cálculo término frecuencia inversa de documento (TfidfTransformer())
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(MatrizFrecuencias)

    # Cálculo matriz similitudes
    tdm = tfidf.transpose()
    dtm = tfidf
    Simil = dtm.dot(tdm)

    # Visualización de la matriz de similitudes
    SimilDF = pd.DataFrame(data = Simil.toarray(), index=listado.values,columns=listado.values)

    return SimilDF

def automatizacion(ID_usuario, database):
    
    datos_usuario, apoyo = lista_datos(ID_usuario, database)

    df_support = tipo_apoyo(apoyo, database)

    df_salida = filtro_idioma(datos_usuario, df_support)

    if ID_usuario not in df_salida.user_id.values:
        df_salida = df_salida.append(database[database.user_id == ID_usuario])

    return df_salida
