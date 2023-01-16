import pandas as pd
import numpy as np
import nltk
import re
import string
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer






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
        text: Texto del que se desea eliminar los sigbos de puntuación.
        
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
