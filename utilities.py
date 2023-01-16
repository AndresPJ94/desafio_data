import pandas as pd
import numpy as np
import nltk
import re
import string





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

