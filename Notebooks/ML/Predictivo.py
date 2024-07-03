import streamlit as st
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_squared_error

# Función para cargar datos
@st.cache_data
def load_data():
    ruta1= "..\..\Data\Parquet\Sitios.parquet"
    ruta2= "..\..\Data\Parquet\Scraping_sitios_google.parquet"
    ruta4= "..\..\Data\Parquet\Reviews_florida.parquet"
    ruta5= "..\..\Data\Parquet\review.parquet"
    ruta6= "..\..\Data\Parquet\business.parquet"
    
    dfSitios = pd.read_parquet(ruta1)
    dfScraping = pd.read_parquet(ruta2)
    dfReviewsFL = pd.read_parquet(ruta4)
    dfreview = pd.read_parquet(ruta5)
    dfbusiness = pd.read_parquet(ruta6)
    
    return dfSitios, dfScraping, dfuser, dfReviewsFL, dfreview, dfbusiness

# Cargar datos
dfSitios, dfScraping, dfuser, dfReviewsFL, dfreview, dfbusiness = load_data()

# Crear modelos
modelo_yelpdf = pd.merge(dfbusiness[['business_id', 'name', 'city', 'latitude', 'longitude', 'stars business']],
                               dfreview[['business_id', 'text', 'stars review', 'fecha review']],
                               on='business_id')

modelo_googledf = pd.merge(dfReviewsFL[['business_name', 'rating', 'city', 'gmap_id', 'date', 'text']],
                                    dfSitios[['gmap_id','latitude', 'longitude', 'avg_rating']],
                                    on='gmap_id')

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

modelo_yelpdf.rename(columns={'business_id': 'business_id', 'name': 'business_name', 'city': 'city', 'latitude': 'latitude', 'longitude': 'longitude', 'stars business': 'business_rating', 'text': 'review_text', 'stars review': 'review_stars', 'fecha review': 'review_date'}, inplace=True)

dfFinal = pd.concat([modelo_yelpdf, modelo_googledf])

# Inicializar el analizador de sentimientos de NLTK
sid= SentimentIntensityAnalyzer()

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

# Filtrar datos de Taco Bell
filtro = dfFinal["business_name"] == "Taco Bell"
dfTacoBell = dfFinal[filtro]

dfTacoBell['review_date'] = pd.to_datetime(dfTacoBell['review_date']).dt.strftime('%Y%m%d').astype(int)

features = ['review_date', 'city']
target = 'business_rating'

encoder = OneHotEncoder(handle_unknown='ignore')
city_encoded = encoder.fit_transform(dfTacoBell[['city']])

city_encoded_df = pd.DataFrame(city_encoded.toarray(), columns=encoder.get_feature_names_out(['city']))

taco_bell_data_encoded = pd.concat([dfTacoBell[['review_date']].reset_index(drop=True), city_encoded_df], axis=1)

X_train, X_test, y_train, y_test = train_test_split(taco_bell_data_encoded, dfTacoBell[target], test_size=0.2, random_state=42)

model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)

st.title("Predicción de Ratings para Taco Bell")
st.write("Mean Squared Error:", mse)

# Interfaz para ingresar ciudad y año
st.header("Predicción de rating para una ciudad y año específicos")
ciudad = st.text_input("Ingresa la ciudad")
anio = st.number_input("Ingresa el año", min_value=2023, max_value=2030, step=1)

if st.button("Predecir"):
    if ciudad and anio:
        new_data = pd.DataFrame({'review_date': [int(f"{anio}0101")], 'city': [ciudad]})
        new_city_encoded = encoder.transform(new_data[['city']])
        new_city_encoded_df = pd.DataFrame(new_city_encoded.toarray(), columns=encoder.get_feature_names_out(['city']))

        new_data_encoded = pd.concat([new_data[['review_date']], new_city_encoded_df], axis=1)

        missing_cols = set(X_train.columns) - set(new_data_encoded.columns)
        for c in missing_cols:
            new_data_encoded[c] = 0
        new_data_encoded = new_data_encoded[X_train.columns]

        new_predictions = model.predict(new_data_encoded)

        st.write(f"Predicted business_rating for Taco Bell in {ciudad} in the year {anio}: {new_predictions[0]}")


