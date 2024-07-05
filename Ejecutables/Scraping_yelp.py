import gspread
import time 
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ScrapearYelp:

    def __init__(self) -> None:
        
        self.driver = webdriver.Chrome()

    # Funcion para encontrar el business id
    def get_business_id (self, business):
        try:
            # Encontrar el elemento por su selector CSS
            element = business.driver.find_element(By.CSS_SELECTOR, 'h3.y-css-hcgwj4 > a.y-css-12ly5yx')

            # Obtener el atributo href del elemento
            href = element.get_attribute('href')
            
            # Usar una expresión regular para encontrar el valor de 'ad_business_id'
            match = re.search(r'ad_business_id=([^&]+)', href)

            if match:
                ad_business_id = match.group(1)
            else:
                ad_business_id = href.split('/biz/')[-1].split('?')[0]
            
            return ad_business_id
                
        except:

            return None
        
    # Funcion para encontrar el business name
    def get_business_name (self):

        try:
            # Por medio del Xpath halla el nombre del business y extrae el texto
            name = self.driver.find_element(By.XPATH, '/html/body/yelp-react-root/div[1]/div[4]/div[1]/div[1]/div/div/div[1]/h1').text
            return name
        except:
            return None
        
    # Funcion para extraer la ciudad
    def get_city (self):
        # Creamos una lista con las ciudades que vamos a usar
        ciudades = ['Orlando', 'Miami','Tampa','Clearwater', 'Saint Petesburg', 'Brandon', 'Largo', 'Palm Harbor', 'Dunedin', 'Pinellas Park']

        try:
            # Encontrar el elemento por su selector CSS
            element = self.driver.find_element(By.XPATH, '//*[@id="location-and-hours"]/section/div[2]/div[1]/div/div/div/div[1]/address/p[2]')
            # Obtener el texto del elemento
            text = element.text

            # Asumimos que la ciudad es la primera posicion
            city = text.split(',')[0]
            # Analisamos si se encuentra dentro de nuestro listado de ciudades ya que la informacion tiene dos posibles rutas en las que se puede encontrar
            if city not in ciudades:
                try:
                     
                    element = self.driver.find_element(By.XPATH, '//*[@id="location-and-hours"]/section/div[2]/div[1]/div/div/div/div[1]/address/p[3]')
                    # Obtener el texto del elemento
                    text = element.text

                    # Asumimos que la ciudad es la primera palabra
                    city = text.split(',')[0]
                except:
                    return None
            return city    
        
        except:
            return None

    # Funcion para obtener el estado   
    def get_state (self):
        # unicamente se retorna Florida por que en este caso unicamente se buscaran en ciudades que estan dentro de este estado
        return 'Florida'
    
    # Funcion para extraer la latitud y longitud
    def get_coord (self):
        try:
            # Encontrar el elemento por su selector CSS
            element = self.driver.find_element(By.CSS_SELECTOR, 'div.container__09f24__fZQnf.y-css-9q7a37 > img')

            # Obtener el atributo src del elemento
            src = element.get_attribute('src')

            # Usar una expresión regular para encontrar los valores de latitud y longitud en el parámetro 'center'
            match = re.search(r'center=([-+]?[0-9]*\.?[0-9]+)%2C([-+]?[0-9]*\.?[0-9]+)', src)

            # Hacemos el match y devolvemos como flotantes en dos variables distintas
            if match:
                latitude = match.group(1)
                longitude = match.group(2)

                return float(latitude), float(longitude)
            
        except:
            return None, None
        
    # Funcion para extraer el rating promedio de el business
    def get_stars (self):
        try:
            # Por medio del Xpath encuentra el dato y toma el texto
            stars = self.driver.find_element(By.XPATH, '/html/body/yelp-react-root/div[1]/div[4]/div[1]/div[1]/div/div/div[2]/div[2]/span[1]').text
            # Se transforma a formato float
            return float(stars)
        
        except:
            return None
        
    # Funcion oara extraer la cantidad de reviews por negocio
    def get_reviews_count (self):
        try:
            # Usa el Xpath para extraer el texto y luego usando 'Replace', se elimina lo que no es numerico
            reviews = self.driver.find_element(By.XPATH, '/html/body/yelp-react-root/div[1]/div[4]/div[1]/div[1]/div/div/div[2]/div[2]/span[2]').text
            reviews = reviews.replace('(', '').replace(' reviews)', '').replace(',','')
            # Se retorna en formato int
            return int(reviews)
        
        except:
            return None

    # Funcion para extraer la fecha de la reseña      
    def get_date (self, reseña):
        try:
            # Espera hasta que el elemento con la clase 'y-css-wfbtsu' esté presente
            element = reseña.find_element(By.CLASS_NAME, 'y-css-wfbtsu')

            # Extrae el texto del elemento
            date_text = element.text

            # Convierte el texto a un objeto datetime
            date_format = "%b %d, %Y"  # Formato de fecha en inglés: 'Jun 27, 2024'
            date_object = datetime.strptime(date_text, date_format)

            return date_object

        except:
            return None
    
    # Funcion para hacer el Scraping
    def scraping (self, link):

        #try:
        # Abrimos el link
        self.driver.get(link)

        time.sleep(3)
        # Hallamos el cuadro de texto para buscar la categoria que necesitamos
        category = self.driver.find_element(By.XPATH, '//*[@id="search_description"]')
        # Limpiamos y llenamos el espacio con la info necesaria
        category.clear()
        category.click()
        category.send_keys('Mexican Food')
        time.sleep(1)
        # Buscamos el recuadro para buscar la ubicacion deseada
        ciudad = self.driver.find_element(By.XPATH, '//*[@id="search_location"]')
        # Limpiamos y llenamos con la informacion necesaria
        ciudad.clear()
        ciudad.click()
        ciudad.send_keys('Orlando, FL, EEUU')
        time.sleep(1)
        # Hacemos Click en el boton de buscar
        buscar = self.driver.find_element(By.XPATH, '//*[@id="header_find_form"]/div[3]/button')

        buscar.click()

        siguiente = True

        while siguiente == True:

            # Listas de las columnas para el DF de sitios
            business_id = []
            name = []
            city = []
            state = []
            latitude = []
            longitude = []
            stars = []
            reviews = []

            # Listas para el DF de reviews

            user_id_review = []
            business_id2 = []
            stars_review = []
            date_review = []

            sitios_df = pd.read_parquet('../../Data/Parquet/Sitios_nuevo_yelp.parquet')
            reviews_df = pd.read_parquet('../../Data/Parquet/Reviews_nuevo_yelp.parquet')

            # Hacemos una lista de los restaurantes en la pagina actual
            restaurantes = self.driver.find_elements(By.CSS_SELECTOR, 'div.y-css-1he6azc[data-testid="serp-ia-card"]')
            cantidad = len(restaurantes)
            try:
                for i in range(2, cantidad-1):

                    restaurante = restaurantes[i]

                    element = restaurante.find_element(By.CSS_SELECTOR, 'h3.y-css-hcgwj4 > a.y-css-12ly5yx')

                    # Obtener el atributo href del elemento
                    href = element.get_attribute('href')
                    
                    # Usar una expresión regular para encontrar el valor de 'ad_business_id'
                    match = re.search(r'ad_business_id=([^&]+)', href)

                    if match:
                        idrestaurant = match.group(1)
                    else:
                        idrestaurant = href.split('/biz/')[-1].split('?')[0]

                    if idrestaurant not in sitios_df['business_id'].values:

                        restaurante2 = restaurante.find_element(By.CLASS_NAME, 'y-css-hcgwj4')
                        restaurante2.click()
                        time.sleep(4)

                        self.driver.switch_to.window(self.driver.window_handles[1])

                        try:
                            baner = self.driver.find_element(By.XPATH, '//*[@id="modal-portal-container"]/div[1]/div/div/div')
                            cerrar = baner.find_element(By.XPATH, '//*[@id="modal-portal-container"]/div[1]/div/div/div/div[1]/button/span')
                            cerrar.click()
                            time.sleep(2)
                        except:
                            None
                        
                        name_tmp = self.get_business_name()
                        city_tmp = self.get_city()
                        state_tmp = self.get_state()
                        latitud_tmp, longitud_tmp = self.get_coord()
                        rate_tmp = self.get_stars()
                        reviews_tmp = self.get_reviews_count()

                        business_id.append(idrestaurant)
                        name.append(name_tmp)
                        city.append(city_tmp)
                        state.append(state_tmp)
                        latitude.append(latitud_tmp)
                        longitude.append(longitud_tmp)
                        stars.append(rate_tmp)
                        reviews.append(reviews_tmp)

                        time.sleep(5)
                        lista_reseñas = self.driver.find_element(By.XPATH, '//*[@id="reviews"]/section/div[2]/ul')
                        reseñas = lista_reseñas.find_elements(By.CLASS_NAME, 'y-css-1jp2syp')
                        cantidad_reseñas = len(reseñas)

                        for i in range(0,cantidad_reseñas):
                            # Por medio de exprecion regular extraemos la fecha del review
                            date = reseñas[i].find_element(By.CLASS_NAME, 'y-css-wfbtsu').text
                            date_format = "%b %d, %Y"
                            date_object = datetime.strptime(date, date_format)
                            date_object = date_object.date()
                            # Extraemos por medio de un atributo la calificacion de la review
                            calificacion = reseñas[i].find_element(By.CLASS_NAME, 'y-css-9tnml4')
                            calificacion = calificacion.get_attribute('aria-label')
                            star_rating = int(calificacion.split(' ')[0])
                            # Extraemos el user ID
                            userid = reseñas[i].find_element(By.CLASS_NAME, 'y-css-12ly5yx')
                            userid2 = userid.get_attribute('href')
                            user_id = userid2.split('userid=')[1]

                            user_id_review.append(user_id)
                            business_id2.append(idrestaurant)
                            stars_review.append(star_rating)
                            date_review.append(date_object)

                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        time.sleep(1)

            except:
                for i in range(3, cantidad-1):

                    restaurante = restaurantes[i]
                    idrestaurant = self.get_business_id()
                    if idrestaurant not in sitios_df['business_id'].values:
                        restaurante2 = restaurante.find_element(By.CLASS_NAME, 'y-css-hcgwj4')
                        restaurante2.click()
                        restaurante2.click()
                        time.sleep(4)

                        self.driver.switch_to.window(self.driver.window_handles[1])
                        
                        name_tmp = self.get_business_name()
                        city_tmp = self.get_city()
                        state_tmp = self.get_state()
                        latitud_tmp, longitud_tmp = self.get_coord()
                        rate_tmp = self.get_stars()
                        reviews_tmp = self.get_reviews_count()

                        business_id.append(idrestaurant)
                        name.append(name_tmp)
                        city.append(city_tmp)
                        state.append(state_tmp)
                        latitude.append(latitud_tmp)
                        longitude.append(longitud_tmp)
                        stars.append(rate_tmp)
                        reviews.append(reviews_tmp)

                        time.sleep(5)
                        lista_reseñas = self.driver.find_element(By.XPATH, '//*[@id="reviews"]/section/div[2]/ul')
                        reseñas = lista_reseñas.find_elements(By.CLASS_NAME, 'y-css-1jp2syp')
                        cantidad_reseñas = len(reseñas)

                        for i in range(0,cantidad_reseñas):
                            # Por medio de exprecion regular extraemos la fecha del review
                            date = reseñas[i].find_element(By.CLASS_NAME, 'y-css-wfbtsu').text
                            date_format = "%b %d, %Y"
                            date_object = datetime.strptime(date, date_format)
                            date_object = date_object.date()
                            # Extraemos por medio de un atributo la calificacion de la review
                            calificacion = reseñas[i].find_element(By.CLASS_NAME, 'y-css-9tnml4')
                            calificacion = calificacion.get_attribute('aria-label')
                            star_rating = int(calificacion.split(' ')[0])
                            # Extraemos el user ID
                            userid = reseñas[i].find_element(By.CLASS_NAME, 'y-css-12ly5yx')
                            userid2 = userid.get_attribute('href')
                            user_id = userid2.split('userid=')[1]

                            user_id_review.append(user_id)
                            business_id2.append(idrestaurant)
                            stars_review.append(star_rating)
                            date_review.append(date_object)

                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        time.sleep(1)
            finally:
                sitios_extraido = pd.DataFrame({'business_id': business_id,
                                'name': name,
                                'city':city,
                                'state':state,
                                'latitude':latitude,
                                'longitude':longitude,
                                'stars': stars,
                                'reviews':reviews})
                sitios_cocatenados = sitios_extraido, sitios_df
                sitios_ultimo = pd.concat(sitios_cocatenados)
                
                reviews_extraido = pd.DataFrame({'user_id': user_id_review,
                                        'business_id':business_id2,
                                        'stars_review': stars_review,
                                        'date': date_review})
                reviews_concatenados = reviews_extraido, reviews_df
                reviews_ultimo = pd.concat(reviews_concatenados)
                
                sitios_ultimo.to_parquet('../../Data/Parquet/Sitios_nuevo_yelp.parquet')
                reviews_ultimo.to_parquet('../../Data/Parquet/Reviews_nuevo_yelp.parquet')
                
                try:
                    siguiente_pagina = self.driver.find_element(By.XPATH, '//*[@id="main-content"]/ul/li[22]/div/div/div[11]')
                    siguiente_pagina.click()
                    time.sleep(7)
                except:
                    siguiente = False  

        #except:
         #   print('Se produjo un error en la extraccion de datos')


link = 'https://www.yelp.com/'
scraping = ScrapearYelp()
scraping.scraping(link)