Universidad del Valle de Guatemala
Facultad de Ingeniería
Departamento de Ciencias de la Computación
CC3084 – Data Science

Semestre II – 2026

Laboratorio 1.
Series de Tiempo.

INSTRUCCIONES:

Se trabajará en este laboratorio con  los datos históricos de ingreso de viajeros internacionales a
Guatemala.  Esta  hoja  de  trabajo  se  realizará  en  Grupos  de  tres.  Para  que  se  pueda  calificar  su
laboratorio debe estar inscrito en algún grupo de canvas.

DESCRIPCIÓN DEL DATASET

El conjunto de datos contiene información mensual sobre el ingreso de viajeros, incluyendo: Año,
Mes, Vía de ingreso, Frontera, País de residencia, Región, Región OMT, Agrupación de residencia,
Tipo de viajero y Cantidad de viajeros.

Las variables que tiene este conjunto de datos son las siguientes:

•  Año: Año de ingreso al país
•  Mes cod: Codificación del mes
•  Mes: Nombre del mes
•  Vía: Vía de entrada (Aérea, Terrestre, Marítima)
•  Frontera: Frontera de ingreso
•  País: Hasta el año 2023 país de procedencia después de 2023 agrupación de mercado
•  Región: Clasificación utilizada para reportes nacionales.
•  Región dos: Agrupa varias categorías de Región en continentes o grandes áreas
•  Regiones OMT: Subregión de la Organización Mundial del Turismo
•  MCEO: Mercado o agrupación comercial estratégica. Clasificación de mercados objetivo

utilizada para análisis de turismo.

•  Agrupación Residencia: Región donde reside
•  Tipo de Viajero: Puede ser Turista, Crucerista, Excursionista, Viajero, Visitante
•  Viajero: Cantidad de viajeros

Entre 2022 y 2023 el “tipo de Viajero” excluye a los viajeros no turísticos de alta frecuencia
(comercio fronterizo, tránsito). Por eso la categoría "Viajero" disminuye fuertemente en 2023
y el total anual parece caer, pero no es caída real de turismo. Para comparar en todo el rango
use Turista + Excursionista, que sí son consistentes durante todo el período.

Algunos vínculos interesantes:

-  https://otexts.com/fpp2/
-  https://otexts.com/fpp2/arima.html
-  https://otexts.com/fpp2/accuracy.html
-  https://otexts.com/fpp3/holt-winters.html
-  https://otexts.com/fpp3/expsmooth.html



-  https://otexts.com/fpp3/simple-methods.html#seasonal-na%C3%AFve-method

NOTA: Los datos proporcionados son solo para uso académico, no corresponden a datos oficiales ni
del INGUAT ni del Instituto Guatemalteco de Migración.

EJERCICIOS

1.  Realice un análisis exploratorio del conjunto de datos. Como mínimo incluya:

a.  comportamiento temporal del número de viajeros;
b.  países con mayor cantidad de viajeros;
c.  regiones con mayor cantidad de viajeros;
d.  vías de ingreso y fronteras más utilizadas;
e.  análisis de valores faltantes, duplicados y valores atípicos;
f.  estadísticas descriptivas y visualizaciones con su respectiva interpretación.
2.  Divida  el  conjunto  de  datos  en  entrenamiento  y  prueba,  aproximadamente  70%

entrenamiento, 30% para prueba.

3.  A partir del conjunto de datos de entrenamiento construya series de tiempo mensuales,
agregando  el  número  de  viajeros  según  la  categoría  correspondiente.  Si  considera  que
necesita limpieza hágala.

a.  Serie obligatoria: Total mensual de viajeros internacionales.
b.  Además,  debe  seleccionar  dos  de  las  siguientes  categorías  de  análisis. Para  cada
categoría seleccionada deberán construir una serie por cada valor indicado.

i.  Países de residencia

Construya  una  serie  mensual  para  cada  uno  de  los  tres  países  con
mayor  número  acumulado  de  viajeros  durante  todo  el  período  de
estudio (Top 3). En total deberá obtener tres series.

ii.  Regiones geográficas

Construya  una  serie  mensual  para  las  3  regiones  que  más  viajeros
aporta de la variable Región dos. En total deberá obtener una serie para
cada región (3 series).

iii.  Vías de ingreso

Construya una serie mensual para cada vía de ingreso:

•  Aérea
•  Terrestre
•  Marítima

En total deberá obtener tres series.

iv.  Fronteras



Identifique  las  tres  fronteras  con  mayor  número  acumulado  de
viajeros  durante  todo  el  período  de  estudio  y  construya  una  serie
mensual para cada una de ellas. En total deberá obtener tres series.

v.  Tipo de viajero

Construya una serie mensual para cada tipo de viajero presente en el
conjunto de  datos (por ejemplo, Turista, Excursionista, etc.). En total
deberá obtener una serie por cada categoría existente.

Nota:  El  criterio  para  determinar  los  tres  países,  tres  regiones  y  las  tres
fronteras  principales  deberá  basarse  en  el  total  acumulado  de  viajeros
durante todo el período analizado, no en un año específico.

4.  Análisis de cada serie. Para cada serie:

a.  Especifique Inicio, fin, y frecuencia.
b.  Haga un gráfico de la serie y explique qué información puede obtener a primera

vista.

c.  Descomponga  la  serie.  Teniendo  en  cuenta  el  diagrama  de  la  serie  y  sus
componentes  discuta  si  es  posible  hablar  de  estacionariedad  en  media  y  en
varianza.

d.  Determine si es necesario transformar la serie. Explique.
e.  Explique si no es estacionaria en media. Para esto:

i.   Haga  el  gráfico  de  autocorrelación  y  úselo  para  explicar

la  no

estacionariedad en media.

ii.   Básese  en  los  valores  de  estadísticos  como  la  prueba  de  Dickey-Fuller
Aumentada  para  corroborar  la  no  estacionariedad  en  media.  ¿Qué  es
necesario hacer para hacerla estacionaria en media en caso de que no lo
sea?

f.  Una vez analizada la serie, elija los parámetros p, q y d del modelo ARMA o ARIMA
que  utilizará  para  predecir.  Explique  en  qué  se  basó  para  darle  valor  a  estos
parámetros, teniendo en cuenta las funciones de autocorrelación y autocorrelación
parcial. Si usa la función autoarima de R o auto_arima del módulo pmdarima de
python, determine y explique si tiene sentido el modelo propuesto.

g.  Haga varios modelos ARIMA, y diga cuál es el mejor de ellos para estimar los datos

de la serie. Para esto analice los residuos y las métricas AIC y/ BIC.

h.  Haga  un  modelo  usando  cada  uno  de  los  siguientes  algoritmos:  prophet  de
Facebook,  holt-winters,  suavizamiento  exponencial  o  seasonal  naive.  Compárelo
con los modelos del inciso anterior. ¿Cuál funcionó mejor?

i.  Haga una predicción de los valores de la serie con el mejor modelo para el conjunto

de pruebas.

j.  Compare  los  modelos  mediante  MAE  (Mean  Absolute  Error),  RMSE  (Root  Mean

Square Error) para ARIMA, AIC y BIC.

k.  Seleccione el mejor modelo teniendo en cuenta las métricas.

5.  Análisis comparativo. Responda con evidencia estadística:

a.  Para cada categoría seleccionada:



i.  ¿Cuál de las series presenta mayor estacionalidad?
ii.  ¿Cuál presenta mayor tendencia de crecimiento?
iii.  ¿Cuál presenta mayor volatilidad?
iv.  ¿Cuál fue la más afectada por la pandemia?

b.  En general:

i.  ¿Qué descubrimientos de los que hizo al analizar las series cree que serían

más útiles para que el INGUAT pueda tomar decisiones?

EVALUACIÓN

NOTA: La evaluación de cada integrante del grupo será de acuerdo con sus contribuciones al
trabajo grupal
(15 puntos) Análisis exploratorio:
-

Se elaboró un análisis exploratorio en el que se explican los cruces de variables, hay gráficos
explicativos y análisis que permiten comprender el conjunto de datos.
Se crearon las series de tiempo correspondientes a las instrucciones.
Para cada una de las series se informa inicio, fin y frecuencia.
Se explora el comportamiento de la serie durante y después de la pandemia.

-
-
-
 (15 puntos) Análisis de las series de tiempo
-

Para cada una de las series creadas se analiza:

o  El gráfico de la serie y sus componentes.
o  Si la serie presenta estacionalidad o no y que implica que sí tenga.
o  Si la serie presenta tendencia o no y esto que significa.

(20 puntos) Determinación de Estacionariedad.
-

Para cada una de las series creadas:

o  Se  analiza  si  es  estacionaria  en  varianza  y  en  caso  de  no  serlo  se  aplica  una

transformación adecuada.

o  Se  analiza  si  es  estacionaria  en  media,  para  esto  se  basa  en  la  función  de
autocorrelación  y  en  la  prueba  de  Dickey-Fuller  aumentada.  Se  determina  la
cantidad de diferenciaciones que hay que hacer en caso de que no sea estacionaria
en media.
(20 puntos) Generación de modelos
-

Para cada una de las series creadas:

o  Se  determinan  los  valores  de  los  parámetros  p,  q,  y  d.  Para  esto  se  basa  en  las

funciones de autocorrelación y autocorrelación parcial.

o  Se  explica  la elección  de  los  parámetros  y  de  los  modelos.  Se  deben explicar los
parámetros, aunque sean propuestos de forma automática por R (en caso de usar
este lenguaje) o python.

o  Se  generan  los  modelos  con  los  algoritmos  prophet,  holt  winters,  suavizamiento

exponencial y seasonal naive.

o  Se comparan los modelos de acuerdo con el comportamiento de los residuos, las

métricas de error y las métricas AIC y BIC.

(15 puntos) Predicción con los modelos generados.
-

Para cada una de las series creadas:

o  Se crean los conjuntos de entrenamiento y prueba siguiendo las instrucciones.



o  Se  explica  que  tan  bueno  es  el  modelo  prediciendo  los  volúmenes  de  entrada

migratoria para el conjunto de prueba.

o  Se comparan los modelos generados con los diferentes algoritmos.

(15 puntos) Análisis comparativo.
-
Para categoría seleccionada

o  Se responden las preguntas planteadas y las respuestas con claras y  están basadas

en evidencia estadística y gráfica.

-

En general

o  Se plantean varios descubrimientos basados en los análisis realizados que pueden

servirle a INGUAT para toma de decisiones.

MATERIAL A ENTREGAR

-  Archivo .pdf con el informe que contenga, los resultados de los análisis y las explicaciones (No

se aceptará código en el informe).
Script de R (.r o .rmd) o de Python que utilizó para hacer su análisis exploratorio y predicciones.
Link del repositorio usado para versionar el código.

-
-

- 23 de julio de 2026 17:20:

FECHAS DE ENTREGA

.1.  [Avances]  Análisis  Exploratorio,  análisis  de  al  menos  dos  de  las  series  de  tiempo

seleccionadas.

- 26 de julio de 2026 23:59

.1.  Documento completo con todos los análisis.
.2.  Archivos de código.

NOTA: Para poder tener nota completa debe entregar las asignaciones en el tiempo adecuado. No
se calificará el laboratorio si no fue entregado el avance en tiempo, aunque esté en el repositorio.

