# Proyecto 02 - Base de datos 2

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
