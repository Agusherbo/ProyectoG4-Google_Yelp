#!/usr/bin/env python
# coding: utf-8

# # Ingenieria Machine Learning

# ## Librerias

# In[1]:


import pandas as pd
from pandas import json_normalize
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from gensim import corpora
from gensim.models import LdaModel
from gensim.models import CoherenceModel
import gensim
import re
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt


# ## Rutas y DataFrames

# In[2]:


#Sitios: Informacion sobre los restaurantes mexicanos en el estado de florida (Google)
#Scraping_sitios_google: Informacion extraida mediante web scraping (Yelp)
#user:  Cantidad de review por cada usuario y el promedio de estrellas (Yelp)
#Reviews_florida: Diferentes reviews de usuarios sobre los restaurantes mexicanos de florida (Google)
#reviews: Diferenetes tipos de reviews sobre restaurantes de florida (Yelp)
#business: Caracteristicas de todos los restaurantes de comida mexicana de Florida (Yelp)


# In[3]:


ruta1= r"C:\Users\juanc.DESKTOP-LGMDQP1\OneDrive\Documentos\Proyecto Henry Final\ProyectoG4-Google_Yelp\Data\Parquet\Sitios.PARQUET"
ruta2=r"C:\Users\juanc.DESKTOP-LGMDQP1\OneDrive\Documentos\Proyecto Henry Final\ProyectoG4-Google_Yelp\Data\Parquet\Scraping_sitios_google.PARQUET"
ruta3=r"C:\Users\juanc.DESKTOP-LGMDQP1\OneDrive\Documentos\Proyecto Henry Final\ProyectoG4-Google_Yelp\Data\Parquet\user.PARQUET"
ruta4=r"C:\Users\juanc.DESKTOP-LGMDQP1\OneDrive\Documentos\Proyecto Henry Final\ProyectoG4-Google_Yelp\Data\Parquet\Reviews_florida.PARQUET"
ruta5=r"C:\Users\juanc.DESKTOP-LGMDQP1\OneDrive\Documentos\Proyecto Henry Final\ProyectoG4-Google_Yelp\Data\Parquet\review.PARQUET"
ruta6=r"C:\Users\juanc.DESKTOP-LGMDQP1\OneDrive\Documentos\Proyecto Henry Final\ProyectoG4-Google_Yelp\Data\Parquet\business.PARQUET"


# In[4]:


dfSitios=pd.read_parquet(ruta1)
dfScraping=pd.read_parquet(ruta2)
dfuser=pd.read_parquet(ruta3)
dfReviewsFL=pd.read_parquet(ruta4)
dfreview=pd.read_parquet(ruta5)
dfbusiness=pd.read_parquet(ruta6)


# ## Se concatena los datos de Yelp y los de Google para dejar una sola estructura de datos

# In[5]:


modelo_yelpdf = pd.merge(dfbusiness[['business_id', 'name', 'city', 'latitude', 'longitude', 'stars business']],
                               dfreview[['business_id', 'text', 'stars review', 'fecha review']],
                               on='business_id')


# In[6]:


modelo_googledf = pd.merge(dfReviewsFL[['business_name', 'rating', 'city', 'gmap_id', 'date', 'text']],
                                    dfSitios[['gmap_id','latitude', 'longitude', 'avg_rating']],
                                    on='gmap_id')


# In[7]:


modelo_googledf = modelo_googledf.rename(columns={
    'business_id': 'business_id',
    'business_name': 'business_name',
    'city': 'city',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'avg_rating': 'business_rating',
    'text': 'review_text',
    'rating': 'review_stars',
    'date': 'review_date'
})


# In[8]:


modelo_yelpdf.rename(columns={'business_id': 'business_id', 'name': 'business_name', 'city': 'city', 'latitude': 'latitude', 'longitude': 'longitude', 'stars business': 'business_rating', 'text': 'review_text', 'stars review': 'review_stars', 'fecha review': 'review_date'}, inplace=True)


# In[9]:


#hacer un append de las tablas modelo_regresion_yelpdf y modelo_regresion_googledf y guardar el resultado en un data frame de pandas llamado modelo_regresiondf y luego pasar a un archivo parquet llamado modelo_regresion.csv
dfFinal = pd.concat([modelo_yelpdf, modelo_googledf])


# ## Analisis de sentimientos

# In[10]:


# Inicializar el analizador de sentimientos de NLTK
sid= SentimentIntensityAnalyzer()


# In[11]:


#Analisis de sentimiento para el archivo review

# Retrona 0 si es una reseña negativa
# Retrona 1 si es una reseña nula o neutra
# Retrona 2 si es una reseña positiva

def analyze_sentiment(text):
    if text is None or pd.isna(text):
        return 1 
    else:
        
        sentiment_score = sid.polarity_scores(text)['compound']
        if sentiment_score < -0.05:
            return 0  
        elif sentiment_score > 0.05:
            return 2  
        else:
            return 1  

dfFinal['sentiment_analysis'] = dfFinal['review_text'].apply(analyze_sentiment)


# In[12]:


dfFinal


# ## Se almacena en un dataframe solo los datos de la cadena Taco Bell

# In[13]:


filtro= dfFinal["business_name"] == "Taco Bell"
dfTacoBell=dfFinal[filtro]


# In[14]:


dfTacoBell


# ## Se extraen algunos datos relevantes de Taco Bell y de la competencia 

# ### Analisis de la competencia

# In[15]:


porcentajes = (dfFinal["sentiment_analysis"].value_counts(normalize=True) * 100) 
porcentajes = porcentajes.round(2).astype(str) + '%'
porcentajes


# ### Analisis Taco Bell

# In[16]:


porcentajes2 = (dfTacoBell["sentiment_analysis"].value_counts(normalize=True) * 100) 
porcentajes2 = porcentajes2.round(2).astype(str) + '%'
porcentajes2


# ## Se extraen los topicos de todos los restaurantes

# In[17]:


stop_words = set(stopwords.words('english'))  # Puedes ajustar el idioma según tus datos
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    if isinstance(text, str):  # Verificar si el texto es una cadena válida
        text = re.sub(r'\W', ' ', text)  # Eliminar caracteres no alfanuméricos
        tokens = word_tokenize(text.lower())  # Tokenización y minúsculas
        tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]  # Lematización y eliminación de stopwords
        return tokens
    else:
        return []  # Devolver una lista vacía si no es una cadena válida

processed_reviews = [preprocess_text(review) for review in dfTacoBell["review_text"] if review is not None]

# Creación del diccionario y el corpus
dictionary = corpora.Dictionary(processed_reviews)
corpus = [dictionary.doc2bow(text) for text in processed_reviews]

# Modelado de tópicos usando LDA
lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=5, random_state=42, passes=10)

# Visualización de tópicos
for idx, topic in lda_model.print_topics():
    print(f'Tópico {idx}: {topic}')

# Calcular la coherencia del modelo (opcional, para evaluar la calidad de los tópicos)
coherence_model_lda = CoherenceModel(model=lda_model, texts=processed_reviews, dictionary=dictionary, coherence='c_v')
coherence_lda = coherence_model_lda.get_coherence()
print(f'\nCoherencia del modelo LDA: {coherence_lda}')


# ## Se realiza un modelo para predecir el promedio de estrellas de los restaurantes Taco Bell en los proximos años segun la ciudad

# In[18]:


# Convertir la columna review_date a formato numérico
dfTacoBell['review_date'] = pd.to_datetime(dfTacoBell['review_date']).dt.strftime('%Y%m%d').astype(int)

# Filtrar los datos para los restaurantes Taco Bell
taco_bell_data = dfTacoBell[dfTacoBell['business_name'].str.contains('Taco Bell', case=False)]

# Seleccionar las características y la variable objetivo
features = ['review_date', 'city']
target = 'business_rating'

# Codificar la columna 'city' utilizando one-hot encoding
encoder = OneHotEncoder(handle_unknown='ignore')
city_encoded = encoder.fit_transform(taco_bell_data[['city']])

# Convertir el resultado de one-hot encoding a un DataFrame
city_encoded_df = pd.DataFrame(city_encoded.toarray(), columns=encoder.get_feature_names_out(['city']))

# Concatenar las características codificadas con las otras características
taco_bell_data_encoded = pd.concat([taco_bell_data[['review_date']].reset_index(drop=True), city_encoded_df], axis=1)

# Dividir los datos en conjunto de entrenamiento y conjunto de prueba
X_train, X_test, y_train, y_test = train_test_split(taco_bell_data_encoded, taco_bell_data[target], test_size=0.2, random_state=42)

# Crear el modelo de regresión de bosque aleatorio
model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

# Realizar predicciones en el conjunto de prueba
y_pred = model.predict(X_test)

# Calcular el error cuadrático medio
mse = mean_squared_error(y_test, y_pred)
print("Mean Squared Error:", mse)


# In[19]:


# Ejemplo de uso: predecir el business_rating para Taco Bell en los próximos años
new_data = pd.DataFrame({'review_date': [20230101, 20240101, 20250101], 'city': ['Miami', 'Orlando', 'Tampa']})

# Codificar la columna 'city' del nuevo conjunto de datos utilizando el mismo encoder
new_city_encoded = encoder.transform(new_data[['city']])

# Convertir el resultado de one-hot encoding a un DataFrame
new_city_encoded_df = pd.DataFrame(new_city_encoded.toarray(), columns=encoder.get_feature_names_out(['city']))

# Concatenar las características codificadas con la columna 'review_date'
new_data_encoded = pd.concat([new_data[['review_date']], new_city_encoded_df], axis=1)

# Asegurarse de que las columnas del nuevo conjunto de datos coincidan con las del conjunto de entrenamiento
missing_cols = set(X_train.columns) - set(new_data_encoded.columns)
for c in missing_cols:
    new_data_encoded[c] = 0
new_data_encoded = new_data_encoded[X_train.columns]

# Realizar predicciones con el modelo
new_predictions = model.predict(new_data_encoded)

print("Predicted business_rating for Taco Bell in the next years:")
for year, prediction in zip([2023, 2024, 2025], new_predictions):
    print(f"Year {year}: {prediction}")


# ## Se divide en dos dataframes las reseñas positivas y negativas de todos los restaurantes mexicanos de Florida

# In[20]:


#Almacenamos en un df las reseñas positivas y en otro las negativas de todos los restaurantes mexicanos de Florida
filx=dfFinal["sentiment_analysis"] == 2
dfRestapositiv= dfFinal[filx] 

filz=dfFinal["sentiment_analysis"] == 0
dfRestanegat= dfFinal[filz] 


# ## Se divide en dos dataframes las reseñas positivas y negativas de todos los restaurantes Taco Bell de Florida

# In[21]:


#Almacenamos en un df las reseñas positivas y en otro las negativas de todos los restaueantes de Taco Bell
filt=dfTacoBell["sentiment_analysis"] == 2
dfPostivTacoB= dfTacoBell[filt] 

film=dfTacoBell["sentiment_analysis"] == 0
dfNegativTacoB= dfTacoBell[film] 


# ## Se hace una extraccion de las palabaras mas repetidas en las reseñas positivas de todos los restaurantes mexicanos de Florida

# In[22]:


#Hacemos una extraccion de las palabras mas relevantes en las reseñas positivas de los restaurantes mexicanos de florida

stop_words = set(stopwords.words('english'))  # Puedes ajustar el idioma según tus datos
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    if isinstance(text, str):  # Verificar si el texto es una cadena válida
        text = re.sub(r'\W', ' ', text)  # Eliminar caracteres no alfanuméricos
        tokens = word_tokenize(text.lower())  # Tokenización y minúsculas
        tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]  # Lematización y eliminación de stopwords
        return tokens
    else:
        return []  # Devolver una lista vacía si no es una cadena válida

processed_reviews = [preprocess_text(review) for review in dfRestapositiv["review_text"] if review is not None]

# Creación del diccionario y el corpus
dictionary = corpora.Dictionary(processed_reviews)
corpus = [dictionary.doc2bow(text) for text in processed_reviews]

# Modelado de tópicos usando LDA
lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=5, random_state=42, passes=10)

# Visualización de tópicos
for idx, topic in lda_model.print_topics():
    print(f'Tópico {idx}: {topic}')

# Calcular la coherencia del modelo (opcional, para evaluar la calidad de los tópicos)
coherence_model_lda = CoherenceModel(model=lda_model, texts=processed_reviews, dictionary=dictionary, coherence='c_v')
coherence_lda = coherence_model_lda.get_coherence()
print(f'\nCoherencia del modelo LDA: {coherence_lda}')


# ## Se hace una extraccion de las palabaras mas repetidas en las reseñas negativas de todos los restaurantes mexicanos de Florida

# In[23]:


#Hacemos una extraccion de las palabras mas relevantes en las reseñas negativas de los restaurantes mexicanos de florida

stop_words = set(stopwords.words('english'))  # Puedes ajustar el idioma según tus datos
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    if isinstance(text, str):  # Verificar si el texto es una cadena válida
        text = re.sub(r'\W', ' ', text)  # Eliminar caracteres no alfanuméricos
        tokens = word_tokenize(text.lower())  # Tokenización y minúsculas
        tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]  # Lematización y eliminación de stopwords
        return tokens
    else:
        return []  # Devolver una lista vacía si no es una cadena válida

processed_reviews = [preprocess_text(review) for review in dfRestanegat["review_text"] if review is not None]

# Creación del diccionario y el corpus
dictionary = corpora.Dictionary(processed_reviews)
corpus = [dictionary.doc2bow(text) for text in processed_reviews]

# Modelado de tópicos usando LDA
lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=5, random_state=42, passes=10)

# Visualización de tópicos
for idx, topic in lda_model.print_topics():
    print(f'Tópico {idx}: {topic}')

# Calcular la coherencia del modelo (opcional, para evaluar la calidad de los tópicos)
coherence_model_lda = CoherenceModel(model=lda_model, texts=processed_reviews, dictionary=dictionary, coherence='c_v')
coherence_lda = coherence_model_lda.get_coherence()
print(f'\nCoherencia del modelo LDA: {coherence_lda}')


# ## Se hace una extraccion de las palabaras mas repetidas en las reseñas positivas de todos los restaurantes Taco Bell de Florida

# In[24]:


#Hacemos una extraccion de las palabras mas relevantes en las reseñas positivas de los restaurantes Taco Bell

stop_words = set(stopwords.words('english'))  # Puedes ajustar el idioma según tus datos
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    if isinstance(text, str):  # Verificar si el texto es una cadena válida
        text = re.sub(r'\W', ' ', text)  # Eliminar caracteres no alfanuméricos
        tokens = word_tokenize(text.lower())  # Tokenización y minúsculas
        tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]  # Lematización y eliminación de stopwords
        return tokens
    else:
        return []  # Devolver una lista vacía si no es una cadena válida

processed_reviews = [preprocess_text(review) for review in dfPostivTacoB["review_text"] if review is not None]

# Creación del diccionario y el corpus
dictionary = corpora.Dictionary(processed_reviews)
corpus = [dictionary.doc2bow(text) for text in processed_reviews]

# Modelado de tópicos usando LDA
lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=5, random_state=42, passes=10)

# Visualización de tópicos
for idx, topic in lda_model.print_topics():
    print(f'Tópico {idx}: {topic}')

# Calcular la coherencia del modelo (opcional, para evaluar la calidad de los tópicos)
coherence_model_lda = CoherenceModel(model=lda_model, texts=processed_reviews, dictionary=dictionary, coherence='c_v')
coherence_lda = coherence_model_lda.get_coherence()
print(f'\nCoherencia del modelo LDA: {coherence_lda}')


# ## Se hace una extraccion de las palabaras mas repetidas en las reseñas negativas de todos los restaurantes Taco Bell de Florida

# In[25]:


#Hacemos una extraccion de las palabras mas relevantes en las reseñas negativas de los restaurantes Taco Bell

stop_words = set(stopwords.words('english'))  # Puedes ajustar el idioma según tus datos
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    if isinstance(text, str):  # Verificar si el texto es una cadena válida
        text = re.sub(r'\W', ' ', text)  # Eliminar caracteres no alfanuméricos
        tokens = word_tokenize(text.lower())  # Tokenización y minúsculas
        tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]  # Lematización y eliminación de stopwords
        return tokens
    else:
        return []  # Devolver una lista vacía si no es una cadena válida

processed_reviews = [preprocess_text(review) for review in dfNegativTacoB["review_text"] if review is not None]

# Creación del diccionario y el corpus
dictionary = corpora.Dictionary(processed_reviews)
corpus = [dictionary.doc2bow(text) for text in processed_reviews]

# Modelado de tópicos usando LDA
lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=5, random_state=42, passes=10)

# Visualización de tópicos
for idx, topic in lda_model.print_topics():
    print(f'Tópico {idx}: {topic}')

# Calcular la coherencia del modelo (opcional, para evaluar la calidad de los tópicos)
coherence_model_lda = CoherenceModel(model=lda_model, texts=processed_reviews, dictionary=dictionary, coherence='c_v')
coherence_lda = coherence_model_lda.get_coherence()
print(f'\nCoherencia del modelo LDA: {coherence_lda}')


# In[28]:


import streamlit as st


# In[29]:


st.write("Hello World")


