# Proyecto 02 - Base de datos 2

# Resumen
El presente proyecto tiene como objetivo desarrollar un motor de búsqueda para arXiv, un repositorio en línea que alberga millones de artículos académicos en STEM. Este motor de búsqueda estará diseñado para facilitar la recuperación eficaz de artículos académicos a través de consultas de texto libre, por lo que la propuesta del proyecto es construir un índice invertido en memoria secundaria usando la estrategia de Blocked Sort-Based Indexing (BSBI), así como rankear los resultados de búsqueda mediante un score basado en la similitud de cosenos y la normalización de términos. 
Además, este proyecto también realizará una comparación del rendimiento del motor de búsqueda implementado en Python contra el de Postgres. 

# Dominio de datos
Se hará uso de un [dataset](https://www.kaggle.com/datasets/Cornell-University/arxiv) de más de 1.7 millones de artículos académicos de arXiv. Cada artículo dentro del repositorio se encuentra descrito de acuerdo a la siguiente información:

- **Id**: Número de identificación del artículo académico en arXiv
- **submitter**: Nombre de quién subió el artículo académico
- **authors**: Autores del artículo académico
- **title:** Título del artículo académico
- **comments**: Información adicional, como número de páginas y figuras
- **journal**: información sobre la revista en la que se publicó el artículo académico
- **doi**: Identificador de Objeto Digital (enlace permanente de la ubicación del artículo en Internet)
- **report-no**: Número de informe técnico o número de preimpresión asociado con el artículo académico
- **categories**: Categorías en los que es clasificado el artículo académico según arXiv
- **license**: Indica si el artículo académico cuenta con licencia de distribución
- **abstract**: Resumen del artículo académico
- **versions**: El historial de versiones del artículo académico
- **update_date**: Fecha de la última actualización
- **authors_parsed**: Lista de los autores del artículo académico

Cabe señalar que, para la construcción de nuestro índice invertido, consideramos pertinente extraer solo los campos más relevantes de cada documento: el id y el abstract.

# Backend
## 1. Construcción del índice invertido en memoria secundaria aplicando la estrategia de Blocked Sort-Based Indexing (BSBI):

Para ello explicaremos la función load(self):
- **Carga de los artículos y preprocesamiento:** La función inicia recorriendo el archivo de datos para leer todos los artículos del dataset. Para la construcción de nuestro índice invertido, solo se extrajo los campos más relevantes de cada documento: el id y el abstract. Posteriormente, se realiza el preprocesamiento del abstract de cada documento lo que implicó realizar el proceso de tokenización, filtrado de stopwords y la reducción de palabras mediante Stemming.

- **Inserción en el índice invertido local:** Después, la función inserta los términos preprocesados en un índice invertido local. Cabe señalar que, este índice invertido tendrá la siguiente forma: [keyword] = {doc_id_1, freq}, {doc_id_2, freq}, ...., debido a que también se almacenará la frecuencia del término en cada documento en el que aparezca (TF), un recurso que será utilizado en el cálculo de nuestro Scoring. Si el tamaño del índice invertido local supera el tamaño de bloque definido, se guarda en un archivo auxiliar y se limpia para futuras inserciones.

- **Cálculo de la frecuencia del documento (DF):** La función actualiza un diccionario `document_frequency` que almacena la cantidad de documentos que contienen un token, lo cual nos permitirá calcular el Scoring posteriormente.

- **Merge:** Finalmente, la función inicializa buffers para cada archivo de índice invertido y utiliza una cola de prioridad para fusionar los archivos de forma ordenada en un índice invertido global llamando a la función merge(self, buffers, active_files_index, priority_queue, buffers_line_number).


## 2. Cálculo del Scoring aplicando la técnica de similitud de coseno:


# Frontend

## Generalized Inverted Index (GIN)

El Generalized Inverted Index (GIN) es un tipo especial de índice diseñado para manejar búsquedas de texto. Aunque se puede usar con trigramas una implementación más optima resulta cuando se aplica sobre variables del tipo tsvector. Ya que cuando se crea un índice GIN en una columna de tipo tsvector, PostgreSQL genera un índice invertido que mapea cada palabra única en el tsvector a los documentos donde aparece. Esto permite una búsqueda eficiente de palabras clave y una clasificación de relevancia para la recuperación de documentos.

## Diseño del índice con PostgreSQL

### Creación de la base de datos

La estructura de nuestra tabla, la se cargó los datos de los json de **arXiv Dataset** es la siguiente:

```psql
CREATE TABLE IF NOT EXISTS articles_database(
  id_ TEXT,
  submitter TEXT,
  authors TEXT,
  title TEXT,
  comments_ TEXT,
  journal TEXT,
  doi TEXT,
  report_no TEXT,
  categories TEXT,
  license TEXT,
  abstract TEXT,
  versions TEXT,
  update_date TEXT,
  authors_parsed TEXT
);
```

Asimismo, creó el índice GIN en una nueva columna denominada **search_txt** que contiene los vectores caracteristicos del abstract del artículo. Aquí se muestra el código utilizado para su creación:

```psql
alter table articles_database add column search_txt tsvector;

update articles_database set search_txt = R.weight from (select id_, to_tsvector('english', abstract) as weight from articles_database) R where R.id_ = articles_database.id_;

create index json_idx_search on articles_database using GIN (search_txt);
```

Cabe resaltar que estas consultas query están implementadas en nuestro backend mediante las siguientes funciones hechas en python:

```py
def load_data_in_postgres(size) # Cargar data en Postgres
def get_news_query(self, query, top_k): # Realizar la consulta del top-k
```

### Conexión del Backend con la base de datos

La conexión con la base de datos se hace mediante el paquete **psycopg2**, es así que la query utilizada para realizar las búsquedas es la siguiente:

```py
""" SELECT id_, title, ts_rank_cd(search_txt, query) AS score
                        FROM articles_database, phraseto_tsquery('english','{query}') query
                        WHERE query @@ search_txt
                        ORDER BY score DESC
                        LIMIT {top_k};"""
```

Se puede observar que los parámetros que varían son {query} y {top_k} que básicamente son datos que se traerán del frontend. Asimismo, se debe recalcar que se utiliza la función **phraseto_tsquery** para convertir la query en su vector caracteristico y así obtener un mejor resultado en la búsqueda. Por otro lado, también se implementa la función **ts_rank_cd** para obtener el grado de similitud de las conultas y obtener las k más relevantes, las cuales son señaladas con el parámetro **top_k**.

## Screenshots de la GUI

### Ruta principal

En esta ruta principalmente tenemos la carga de los índices tanto para nuestro índice invertido en python como en PostgreSQL

![Home](./00_Imagenes_Informe/home.png)

### Consultas en Python

![Texto alternativo](./00_Imagenes_Informe/python.png)

### Consultas en Postgres

![Texto alternativo](./00_Imagenes_Informe/postgres.png)

# Análisis de datos
## Carga de datos

Se testeó la carga de datos/documentos para cantidades rangos distintos de datos:
- rango1: [5,000: 50,000] en intervalos de 5,000 
- rango2: [100,000: 500,000] en intervalos de 100,000. 

El rango de [5,000: 50,000] evidenciaría el crecimiento de la complejidad computacional en cantidades de datos pequeñas, mientras que el rango de [100,000: 500,000] evidenciaría el crecimiento de la complejidad computacional en cantidades de datos grandes.
El procedimiento de carga se datos se realizó tanto en Postgres como en el algoritmo creado en Python.

### Rango [5,000: 50,000], int = 5,000

|  | Python | Postgres |
|-----------|-------|----------------|
| 500	|19,53 |1,977 |
|1.000|34,98 |4,601 |
|1.500|56,70 |5,100 |
|2.000|74,65 |6,446 |
|2.500|91,13 |8,080 |
|3.000|103,62|9,616 |
|3.500|129,69|11,163|
|4.000|139,73|13,358|
|4.500|172,66|15,051|
|5.000|175,58|17,241|

<img src="./00_Imagenes_Informe/Carga1.png"  width="65%">

<img src="./00_Imagenes_Informe/Carga2.png"  width="65%">

### Rango [100,000: 500,000], int = 100,000

|  | Python | Postgres |
|-----------|-------|----------------|
|100.000|1850,83  |171,72 |
|200.000|4675,33  |403,63 |
|300.000|12041,23 |1182,05 |
|400.000|31138,03 |2801,95 |
|500.000|81176,83 |7945,27 |

## Búsqueda

Las búsquedas se realizaron sobre las mismas cantidades de datos cargadas de modo que los intervalos [5,000: 50,000] y [100,000: 500,000] se mantienen.
El procedimiento de búsqueda se realizó tanto en Postgres como en el algoritmo creado en Python.

### Rango [5,000: 50,000], int = 5,000

|  | Python | Postgres |
|-----------|-------|----------------|
| 500	|0,133|0,020	|
|1.000|0,420|0,012	|
|1.500|0,516|0,019	|
|2.000|0,643|0,022	|
|2.500|0,991|0,029	|
|3.000|1,120|0,031	|
|3.500|1,507|0,031	|
|4.000|1,547|0,036	|
|4.500|1,657|0,038  |
|5.000|1,671|0,051	|

<img src="./00_Imagenes_Informe/Busqueda1.png"  width="65%">

<img src="./00_Imagenes_Informe/Busqueda2.png"  width="65%">

### Rango [100,000: 500,000], int = 100,000

|  | Python | Postgres |
|-----------|-------|----------------|
|100.000|9,061   |0,254 |
|200.000|27,366  |0,596 |
|300.000|56,941  |1,853 |
|400.000|127,441 |3,357 |
|500.000|301,655 |6,441 |
