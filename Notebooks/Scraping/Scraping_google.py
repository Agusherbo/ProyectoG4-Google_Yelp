import gspread
import time 
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import pandas as pd

class ScrapearGMaps:

    data = {}
    worksheet = {}


    def __init__(self) -> None:
        # Iniciamos el webdriver
        self.driver = webdriver.Chrome()

    # Funcion para scrollear
    def scroll_page (self):
        # Identificamos el objeto hacia el que queremos hacer el scroll
        section_loading = self.driver.find_element(By.CLASS_NAME, 'TFQHme ')

        # Hacer scroll en los resultados
        for _ in range(30):  # Ajustar el rango según la cantidad de scrolls que necesites
            scrollable_div = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]')
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(3)  # Esperar un poco antes de hacer el siguiente scroll

    # Funcion para obtener el nombre
    def get_name (self):
        try:
            # Por medio del Xpath extraemos el texto del nombre
            return self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[1]/h1').text
        except:
            return "SD"
        
    def get_coord (self,link):
        coordenadas = re.search(r"!3d-?\d\d?\.\d{4,8}!4d-?\d\d?\.\d{4,8}", link).group()
        coordenada = coordenadas.replace('!3d','')

        return tuple(coordenada.split('!4d'))
    
    def get_gmapid(self,link):
        patron = r'0x[0-9a-fA-F]+:0x[0-9a-fA-F]+'

        try:
            match = re.search(patron, link)

            extracted_data = match.group()
            return extracted_data

        except:
            return 'Extraccion fallida'
        

    def get_category (self):

        categoria=self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[2]/span[1]/span/button').text

        return categoria
    
    def get_rating (self):
        rating = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[1]/span[1]').text
        rating = rating.replace(',','.')
        
        return float(rating)
    
    def get_reviews (self):

        reviews = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[2]/span/span').text
        reviews = reviews.replace('.','')
        reviews = reviews.replace('(','')
        reviews = reviews.replace(')','')
        
        return int(reviews)
    
    def get_direccion (self):
            try:
                direccion = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[9]/div[3]/button/div/div[2]/div[1]').text

                return direccion
            except:
                direccion = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[11]/div[3]/button/div/div[2]/div[1]').text

                return direccion

    # Creamos una funcion para extraer la ciudad desde la direccion
    def extraer_ciudad(self, direccion):

        try:
            # Dividir la dirección en partes usando la coma como separador
            partes = direccion.split(", ")

            # Asegurarse de que haya al menos tres partes (ciudad, estado_código postal)
            if len(partes) >= 3:
                ciudad = partes[1]  # Extraer la 3ra parte como ciudad
                return ciudad
            else:
                return None # Devolver None para ciudad y estado si tiene la configuración planteada
        except IndexError:
            return None  # Devolver None para ciudad y estado si la extracción falla
    
    def get_reviews_completas ():
        i=0


    def scraping_sitios (self,link):

        name = []
        gmap_id = []
        latitud = []
        longitud = []
        categoria = []
        avg_rating = []
        reviews = []
        ciudad = []


        self.driver.get(link)

        time.sleep(5)

        self.scroll_page()

        lugares = self.driver.find_elements(By.CLASS_NAME, 'hfpxzc')
        cantidad = len(lugares)

        for i in range(0,cantidad):
            
            try:

                lugar = lugares[i]

                scrollable_div = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]')
                self.driver.execute_script("arguments[0].scrollIntoView();", lugar)

                time.sleep(2)
                lugar.click()

                time.sleep(4)

                name_temp = self.get_name()
                mapid_temp = self.get_gmapid(self.driver.current_url)
                coordenadas = self.get_coord(self.driver.current_url)
                categoria_temp = self.get_category()
                rating_temp = self.get_rating()
                reviews_temp = self.get_reviews()
                direccion = self.get_direccion()
                ciudad_temp = self.extraer_ciudad(direccion)


                name.append(name_temp)
                gmap_id.append(mapid_temp)
                latitud.append(coordenadas[0])
                longitud.append(coordenadas[1])
                categoria.append(categoria_temp)
                avg_rating.append(rating_temp)
                reviews.append(reviews_temp)
                ciudad.append(ciudad_temp)
                time.sleep(2)
            except:

                name.append(None)
                gmap_id.append(None)
                latitud.append(None)
                longitud.append(None)
                categoria.append(None)
                avg_rating.append(None)
                reviews.append(None)
                ciudad.append(None)
                time.sleep(2)


        df = pd.DataFrame({'name':name,
                            'gmap_id':gmap_id,
                            'latitude':latitud,
                            'longitude':longitud,
                            'category':categoria,
                            'avg_rating':avg_rating,
                            'num_of_reviws':reviews,
                            'city':ciudad})
            
        return df
