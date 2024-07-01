import gspread
import time 
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import pandas as pd

class ScrapearGMaps:


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
            # Retornamos SD de sin datos en el caso de que la extraccion sea fallida
            return "SD"
        
    # Funcion para extraer las coordenadas      
    def get_coord (self,link):
        # Usamos expresion regular para extraer las coordenadas desde el link 
        coordenadas = re.search(r"!3d-?\d\d?\.\d{4,8}!4d-?\d\d?\.\d{4,8}", link).group()
        # Separamos para que queden unicamente los datos numericos y separados
        coordenada = coordenadas.replace('!3d','')
        # Retornamos una tupla con los dos datos
        return tuple(coordenada.split('!4d'))
    
    # Funcion para obtener el Gmap_id
    def get_gmapid(self,link):
        # Guardamos como variable el patron encontrado para hallar el Gmap_id
        patron = r'0x[0-9a-fA-F]+:0x[0-9a-fA-F]+'

        try:
            # Usando expresion regular extraemos el Gmap_id usando el patron encontrado
            match = re.search(patron, link)
            # Agrupamos los datos y los retornamos
            extracted_data = match.group()
            return extracted_data

        except:
            # En caso de no ser excitosa la extraccion retornara un mensaje de extraccion fallida
            return 'Extraccion fallida'
        
    # Funcion para hallar la categoria del restaurante
    def get_category (self):
        # Por medio del Xpath se busca la parte que contenga texto y se guarda en una variable
        categoria=self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[2]/span[1]/span/button').text
        # Se retorna la categoria extraida
        return categoria
    
    # Funcion para obtener el Rating del lugar
    def get_rating (self):
        # Usamos el Xpath para hallar el texto dentro de la ubicacion
        rating = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[1]/span[1]').text
        # Reemplazamos las comas por puntos para poder transformalo en formato Float
        rating = rating.replace(',','.')
        # Retornamos el valor tipo float
        return float(rating)
    
    # Funcion para hallar la cantidad de reviews por sitio
    def get_reviews (self):
        # Usando el Xpath extraemos la cantidad de reviews que tiene cada sitio
        reviews = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[2]/span/span').text
        # Usando Replace eliminamos algunos elementos para poder convertirlo en int
        reviews = reviews.replace('.','')
        reviews = reviews.replace('(','')
        reviews = reviews.replace(')','')
        # Retornamos el valor numerico
        return int(reviews)
    
    # Funcion para hallar la direccion del lugar
    def get_direccion (self):
            try:
                # Intenta extraer la direccion por medio de la ruta dada y retornarla en tipo texto
                direccion = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[9]/div[3]/button/div/div[2]/div[1]').text

                return direccion
            except:
                # Genera una excepcion con la otra posible ruta de la direccion y la retorna en tipo texto
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
        
    # Funcion para extraer el Id de usuario
    def extraer_id_usuario (self,link):

        try:
            # Usar una expresión regular para encontrar la parte numérica
            match = re.search(r'/(\d+)/reviews', link)

            # Extraer y mostrar la parte numérica si se encuentra
            numeric_part = match.group(1)
            return int(numeric_part)
        except:
            return None              
    
    # Funcion que realiza el scraping
    def scraping (self,link):

        sitios = pd.read_parquet('../../Data/Parquet/Sitios_nuevo.parquet')
        busquedas = ['Restaurantes mexicanos, Pinellas Park, EEUU']
        
        # Se crean las listas para almacenar los datos del dataframe sitios
        name = []
        gmap_id = []
        latitud = []
        longitud = []
        categoria = []
        avg_rating = []
        reviews = []
        ciudad = []

        # Se crean las listas que  van a almacenar los datos del dataframe reviews
        reviewid = []
        userid = []
        username = []
        rating = []
        text = []
        gmap_idreseña = []
        businessname = []
        categoriareview = []
        ciudadreview = []

        # Usando el driver se accede al link
        self.driver.get(link)
        # Se da una espera de 5 segundos para que cargue la pagina
        time.sleep(5)
        buscador = self.driver.find_element(By.XPATH, '//*[@id="searchboxinput"]')
        for i in range (0,len(busquedas)):
            buscador.clear()
            buscador.click()
            buscador.send_keys(busquedas[i])

            buscar = self.driver.find_element(By.XPATH, '//*[@id="searchbox-searchbutton"]')
            buscar.click()
            time.sleep(2)
            # Se llama la funcion que hace scroll 
            self.scroll_page()
            # Se guarda en una variable las rutas de todos los lugares encontrados
            lugares = self.driver.find_elements(By.CLASS_NAME, 'hfpxzc')
            cantidad = len(lugares)
            # Por medio de un ciclo se itera la lista anteriormente creada permitiendo entrar sitio por sitio para extraer la informacion
            for i in range(0,cantidad):
                
                try:
                    # Se ubica en el lugar segun el ciclo
                    lugar = lugares[i]
                    # Se escrolea hasta el sitio
                    scrollable_div = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]')
                    self.driver.execute_script("arguments[0].scrollIntoView();", lugar)
                    # Se esperan dos segundos y se da click para abrir la informacion del lugar
                    time.sleep(2)
                    lugar.click()
                    # Se esperan 4 segundos para que la informacion cargue correctamente
                    time.sleep(4)
                    mapid_temp = self.get_gmapid(self.driver.current_url)
                    if mapid_temp not in sitios['gmap_id'].values :
                        # Se llaman todas las funciones que extraen la informacion necesaria y se guardan en variables temporales
                        name_temp = self.get_name()
                        
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

                        try:
                            # Se busca el apartado de reseñas y se da click
                            opiniones = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[3]/div/div/button[2]/div[2]/div[2]')
                            opiniones.click()
                            # Se esperan 2 segundos y se busca el boton para ordenarlos por mas recientes
                            time.sleep(4)
                            ordenar = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]/div[7]/div[2]/button/span')
                            ordenar.click()
                            time.sleep(4)
                            # Despues de esperar 2 segundos se busca el boton de ordenar por mas recientes y se le da click
                            orden = self.driver.find_element(By.XPATH, '//*[@id="action-menu"]/div[2]')
                            orden.click()
                            # Se esperan 2 segundos y se escrollea un poco para extraer las reviews mas recientes
                            time.sleep(2)
                            scrollable_div = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]')
                            for i in range (0,2):
                                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
                                time.sleep(3)
                            # Se guarda como variable las rutas de las reseñas encontradas
                            reseñas = self.driver.find_elements(By.CLASS_NAME, 'jJc9Ad ')
                            cantidad_reviews = len(reseñas)

                            for i in range (0,cantidad_reviews):
                                    
                                buton = reseñas[i].find_element(By.CLASS_NAME, 'WEBjve')
                                data_review_id = buton.get_attribute('data-review-id')

                                try:
                                    # Localizar el botón usando su clase (puedes usar cualquier otro selector adecuado)
                                    element = reseñas[i].find_element(By.CLASS_NAME, 'al6Kxe')

                                    # Obtener el valor del atributo data-href
                                    data_href = element.get_attribute('data-href')

                                    # Extraer la parte numérica del enlace usando una expresión regular
                                    match = re.search(r'\d+', data_href)
                                    if match:
                                        userid_temp = match.group(0)  
                                    else:
                                        userid_temp = None
                                except:
                                    userid_temp = None

                                # Intentamos extraer el nombre del usuario
                                try:
                                    nombreuser_temp = reseñas[i].find_element(By.CLASS_NAME, 'd4r55 ').text
                                except:
                                    nombreuser_temp = None
                                
                                # intentamos extraer el rating dado en la reseña
                                try:
                                    # Localizar el elemento que contiene las estrellas
                                    elemento=reseñas[i].find_element(By.CLASS_NAME, 'kvMYJc')
                                    # Localiza el elemento por su clase

                                    # Obtener el valor del atributo aria-label
                                    aria_label = elemento.get_attribute('aria-label')

                                    # Extraer el número de estrellas del aria-label
                                    calificacion_temp = int(aria_label.split()[0])  # Asumiendo que el formato es siempre 'X estrellas'
                                except:
                                    calificacion_temp = None

                                # Tratamos de extraer el texto del review
                                botonmas = self.driver.find_element(By.CLASS_NAME, 'w8nwRe')
                                botonmas.click()

                                try:
                                    texto_temp = reseñas[i].find_element(By.CLASS_NAME, 'wiI7pd').text
                                except:
                                    texto_temp = None
                                
                                reviewid.append(data_review_id)
                                userid.append(userid_temp)
                                username.append(nombreuser_temp)
                                rating.append(calificacion_temp)
                                text.append(texto_temp)
                                gmap_idreseña.append(mapid_temp)
                                businessname.append(name_temp)
                                categoriareview.append(categoria_temp)
                                ciudadreview.append(ciudad_temp)

                        except:

                            reviewid.append(None)
                            userid.append(None)
                            username.append(None)
                            rating.append(None)
                            text.append(None)
                            gmap_idreseña.append(None)
                            businessname.append(None)
                            categoriareview.append(None)
                            ciudadreview.append(None)
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
                



        sitios = pd.DataFrame({'name':name,
                            'gmap_id':gmap_id,
                            'latitude':latitud,
                            'longitude':longitud,
                            'category':categoria,
                            'avg_rating':avg_rating,
                            'num_of_reviews':reviews,
                            'city':ciudad})
        
        reviews = pd.DataFrame({'review_id':reviewid,
                            'user_id':userid,
                            'user_name':username,
                            'rating':rating,
                            'text':text,
                            'gmap_id':gmap_idreseña,
                            'business_name':businessname,
                            'category':categoriareview,
                            'city':ciudadreview})
            
        return sitios, reviews


link = 'https://www.google.com/maps/search/Restaurantes,+Florida,+EEUU/@28.4613115,-91.2139021,6z/data=!4m2!2m1!6e5?entry=ttu'

gscraping = ScrapearGMaps()

sitios, reviews = gscraping.scraping(link)

