Voy a recolectar una muestra de datos inicial para tener datos de línea base con los cuales comparar otros datos más específicos en las próximas etapas. Para esto estoy usando Twint (https://github.com/twintproject/twint/)

Se debe especificar un contexto que se utilizará para estos análisis ya que no sería posible comparar los tweets, por ejemplo, sobre la coyuntura de Guatemala con los tweets de coyuntura gringa. Este contexto puede especificarse con un hashtag o una búsqueda en Twitter. Usando Twint se va a hacer un scrape de los tweets de cierta búsqueda o hashtag para cierto rango de tiempo. Para que sea sistemático, se hará una selección de aleatoria de períodos de tiempo. 

## Método de muestreo de línea base:

* _Tema_: Se elije un tema o hashtag de contexto para realizar una búsqueda en twitter.

* _Tiempos_: Se elije un período de 5 minutos al azar para cada hora del día, durante los días que dure el muestreo. 

* _Base de datos_: La base de datos será un archivo SQLite. Tendrá esquemas para Usuarios y Tweets. Además tendrá una tabla con metadatos de la muestra que contiene. Fecha de inicio, fecha de final, tema para la búsqueda, plan de muestreo aleatorio (los minutos elegidos aleatoriamente para cada hora), entre otras cosas.

* _Colectar tweets_: se hace la búsqueda de tweets trending y de tweets comunes durante esos 5 minutos. Se obtienen los primeros A tweets para cada período de 5 minutos. Para cada día se tendría 24*A tweets. Los datos se almacenarán en formato SQLite. 

* _Usuarios_: En el primer paso se va a recolectar una muestra inicial de tweets. En dicha muestra se va a encontrar a un conjunto de usuarios. Para cada usuario, se va a hacer un scrape de su perfil, seguidores, seguidos, últimos likes, retweets, tweets, respuestas. 

Todos estos datos se juntan en la base de datos para realizar análisis de esta muestra de línea base. Esta muestra será aleatoria y va a dar una idea de las distribuciones que pueden encontrarse entre los datos de twitter.

### Notas

En el primer intento para ejecutar lo mencionado arriba no se ha podido obtener los tweets favoritos ni el listado de seguidores y seguidos. El scrape de usuarios se ha limitado a los datos básicos del perfil (Lookup) y los últimos 50 tweets. Son +23K usuarios para datos de Nov y Dic 2020. 

La recolección de datos de usuarios ha tomado bastante tiempo y se ha obtenido un dataset de un tamaño considerable (~700MB).

### Métricas calculadas:

* días de edad de la cuenta
* distancia promedio entre tweets (en segundos)
* rt ratio
* reply ratio
* largo de palabras, de tweets (media y dev. estd.)
* media y varianza de horas de tweetear
* respuestas, likes, rt's recibidos en tweets propios (promedio y dev.estd.)
* 

## Análisis de cuentas de interés

Si se tiene una cuenta que interesa analizar se puede comenzar con lo siguiente:

## Recomendaciones

* Para evitar congestionar las APIs de Twitter y evitar ser bloqueado he utilizado retardos entre cada ciclo de la recolección de datos de 7 a 15 segundos. Esto hace que sea bastante tardado recolectar una cantidad mediana de datos. 10,000 consultas requieren entre 20 y 40 horas. Utilizando, por ejemplo, 8 servidores, se podría dividir a 2 a 5 horas. Se puede orquestar esto usando kubernetes en digitalocean o algo similar.

* 