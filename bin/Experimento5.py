"""Clasifica el conjunto de entrada usando el mejor clasificador encontrado

Nota: Asumimos que el .so generado (sentiment.cpython....so) está en la carpeta
`notebooks/`

"""
# Estas dos líneas permiten que python encuentre la librería sentiment en notebooks/
import sys
sys.path.append("../notebooks/")

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sentiment import PCA, KNNClassifier
from nltk.corpus import stopwords
import numpy as np
from sklearn.metrics import accuracy_score
import pickle

def agregar_negaciones(text_train):
    negaciones = ["no","nor","not","none","without","never","nobody","never","barely","hardly","seldom","less","little","rarely","scarcely"]
    #ademas considero las palabras que terminan en n't
    finalizadores = [".",",",";","<br/>","<br>"]
    for i in range(len(text_train)):
        text_train[i] = "<br/>".join(text_train[i].split("<br />"))
        por_palabras = text_train[i].split(" ")
        for num_palabra in range(len(por_palabras)):
            if por_palabras[num_palabra] in negaciones or "n't" in por_palabras[num_palabra]:
                j = 1
                while num_palabra+j < len(por_palabras) and por_palabras[num_palabra+j] not in finalizadores and por_palabras[num_palabra+j][-1] not in finalizadores:
                    por_palabras[num_palabra+j] = "_NOT"+por_palabras[num_palabra+j]
                    j += 1
        text_train[i] = " ".join(por_palabras)
    return text_train

def vectorizar(text_train, label_train, text_test, label_test, BINARIO, IDF, NEGACIONES, STOP_WORDS):
    if STOP_WORDS:
        stopwords_nuestras = stopwords.words('english')
        stopwords_nuestras.append("br")
        vectorizer = TfidfVectorizer(ngram_range = (1,3), binary = BINARIO, strip_accents = 'unicode', stop_words = stopwords_nuestras, use_idf = IDF, smooth_idf = IDF, max_df = 0.9, min_df = 0.001, max_features = 5000)
    else:
        vectorizer = TfidfVectorizer(ngram_range = (1,3), binary = BINARIO, strip_accents = 'unicode', use_idf = IDF, smooth_idf = IDF, max_df = 0.9, min_df = 0.001, max_features = 5000)
    if NEGACIONES:
        text_train = agregar_negaciones(text_train)
        text_test = agregar_negaciones(text_test)
    vectorizer.fit(text_train)
    X_train, y_train = vectorizer.transform(text_train), np.array(label_train)
    X_test, y_test = vectorizer.transform(text_test), np.array(label_test)
    print(X_train.shape)
    return X_train, y_train, X_test, y_test

def get_instances(df, SIZE_TRAIN, SIZE_TEST):
    text_train = df[df.type == 'train']["review"].tolist()[:SIZE_TRAIN]
    label_train = df[df.type == 'train']["label"].tolist()[:SIZE_TRAIN]

    text_test = df[df.type == 'test']["review"].tolist() #tomamos un conjunto de test al azar
    label_test = df[df.type == 'test']["label"].tolist()
    indices_test = np.arange(0,len(text_test))
    np.random.shuffle(indices_test)
    indices_test = np.array(indices_test)
    text_test = np.array(text_test)[indices_test[:SIZE_TEST]]
    label_test = np.array(label_test)[indices_test[:SIZE_TEST]]

    print("Cantidad de instancias de entrenamiento = {}".format(len(text_train)))
    print("Cantidad de instancias de test = {}".format(len(text_test)))
    return text_train, label_train, text_test, label_test

if __name__== '__main__':

    BINARIO = True
    IDF = True
    NEGACIONES = True
    TEST_SIZE = 1000
    STOP_WORDS = True

    print("--------------------------------------------------------")
    print("Test empezado con:")
    print("Test size:",TEST_SIZE)
    print("Negaciones:",NEGACIONES)
    print("Binario:",BINARIO)
    print("Stop words:",STOP_WORDS)
    print("IDF:",IDF)

    df = pd.read_csv("../data/imdb_small.csv")
    df['label'] = (df['label'] == 'pos').astype('int')

    TOTAL_TRAIN = 6000
    text_train, label_train, text_test, label_test = get_instances(df,TOTAL_TRAIN,TEST_SIZE)

    print("Vectorizando...")
    X_train, y_train, X_test, y_test = vectorizar(text_train, label_train, text_test, label_test, BINARIO, IDF, NEGACIONES, STOP_WORDS)

    TRAIN = 1000
    saltoTRAIN = 1000
    mAcc = []
    while TRAIN <= 6000:
        print(TRAIN)
        clf = KNNClassifier(1)
        clf.fit(X_train[:TRAIN], y_train[:TRAIN])
        mat = []
        mat = clf.testearK(X_test)
        vAcc = []
        for i in range(len(mat[0])):
            a = mat[:, i]
            acc = accuracy_score(y_test, a)
            vAcc.append(acc)

        mAcc.append(vAcc)

        TRAIN += saltoTRAIN

    fout = open("resultados_exp5.pkl","wb")
    pickle.dump(mAcc,fout)
    fout.close()
