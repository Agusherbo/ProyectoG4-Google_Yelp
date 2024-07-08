# <h1 align=center> **YELP & GOOGLE MAPS - REVIEWS Y RECOMENDACIONES** </h1>

<p align=center><img src=Imagenes/Yelp_y_google.png><p>

## Contenido

- [Contexto](#contexto)
- [Tema a desarrollar](#tema-a-desarrollar)
- [Producto Entregable](#producto-entregable)
- [Alcance](#alcance)
- [Problema a Resolver](#problema-a-resolver)
- [Planteo de objetivos](#planteo-de-objetivos)
- [Plan de trabajo](#plan-de-trabajo)
- [KPIs](#kpis)
- [Stack Tecnologico](#stack-tecnologico)
- [Deploy](#deploy)
- [Diagrama de ciclo de vida del dato](#diagrama-de-ciclo-de-vida-del-dato)
- [Participantes y Roles](#participantes-y-roles)


## Contexto 
El mercado gastronómico cada vez más competitivo y centrado en la experiencia del cliente resulta de interés para nuestro equipo de consultores. Como profesionales en el área, nuestra misión es potenciar al máximo y asegurar el éxito del negocio de nuestro cliente. 
En este caso, nuestro cliente, un grupo inversor con franquicias de Taco bell (comida mexicana) en Florida, quiere potenciar el posicionamiento de sus locales. 

## Tema a desarrollar 
Restaurantes de comida Mexicana Taco Bell 
Existe una oportunidad de potenciar la visibilidad y el impacto del negocio a través de la toma de decisiones basadas en datos para mejorar la experiencia del consumidor. Esto permitirá a nuestro cliente mantenerse competitivo en el mercado.  

## Producto Entregable
- Modelo de prediccion de rating para los locales de Taco Bell Florida segun Año y ciudad. El desarrollo de este modelo de prediccion se realiza con el objetivo de preveer el rating futuro y así planificar estrategias para mejorar la calidad del servicio o tomar decisiones de expansión.
- Dashboard interactivo en Power BI para una visualizacion completa de los insight mas significativos para el negocio. 

## Alcance 
- Locales de Taco Bell en el estado de Florida, Estados Unidos.
- Cliente: Grupo inversor con franquicias de Taco bell
- Google y yelp como fuente de datos - cruzar ambas fuentes 
- Se trabajará en el rango temporal de 2017 a 2021

## Problema a resolver 
- Determinar estratégicamente cuáles son las mejoras que se podrían aplicar a los locales de Taco Bell para mantener su competitividad en el mercado.
- Potenciar la visibilidad de los locales de Taco Bell haciendo foco en lo que más valora el consumidor. Basándonos en las reseñas de Google y Yelp, se hará una análisis profundo teniendo en cuenta: experiencia de consumo, calidad de servicio, oportunidades de mejora, mejores productos en relación precio/calidad, mejores ubicaciones geográficas.
- Conocer cual seria la ubicacion geografica mas adecuada para la apertura de una nueva sucursal.

## Planteo de objetivos
1- Desarrollar un Modelo de recomendación para el cliente a partir del análisis de las reseñas de sus locales presentes en Florida que identifique cuales son los atributos que se traducen en una mejor valoración del local.
2- Diseñar de un dashboard interactivo para visualizar insights y detectar oportunidades de negocio en el estado de Florida considerando la densidad de reseñas positivas, la competencia existente y otros factores relevantes
3- Realizar un análisis de sentimientos utilizando técnicas de procesamiento de lenguaje natural (NLP) en las reseñas de Yelp y Google Maps para comprender la percepción de los usuarios sobre los locales de Taco Bell. 

## Plan de trabajo
- *Metodologia Scrum*
- *Diagrama de gantt* 


## KPIs

**Indice de Satisfacción del cliente**
- *Definicion:* Que las reseñas positivas representan un aumento con respecto al trimestre anterior.
- *Fórmula:* (Cantidad de reseñas positivas) / (Cantidad Total de reseñas)

**Mejor calificacion que la competencia**
- *Definicion:* El promedio de la calificación del restaurante sea superior al promedio total de la competencia en el estado de Florida.
- *Fórmula:* (Calificación promedio del restaurant) - (Calificación promedio de la competencia)

**% de reseñas negativas**
- *Definicion:* Que las reseñas negativas no aumenten 
- *Fórmula:* (Calificación de reseñas negativas) / (Calificación Total de reseñas)
  

## Stack Tecnologico 

## Deploy en Streamlit

Para el deploy del modelo de ML se seleccionó la plataforma Streamlit que es una framework de aplicacion de codigo abierto para crear y ejecutar aplicaciones y sitios web, permitiendo el despliegue automático desde GitHub.
El servicio queda corriendo en [aquí](https://app-g4-giby5zg8jfkqmz6pappsdyt.streamlit.app/)

> [!NOTE]
> Para el despliegue automático, Streamlit utiliza GitHub. Con el fin de optimizar el almacenamiento del repositoriom, se realizó un repositorio exclusivo para el deploy, el cual se encuentra [aquí](https://github.com/Agusherbo/Streamlit-G4)



## Diagrama de Ciclo de vida del dado


## Participantes y roles 


