# BD_02

# Generalized Inverted Index (GIN)
El Generalized Inverted Index (GIN) es un tipo especial de índice diseñado para manejar búsquedas de texto. Para su implementación en Postgres se hace uso del operador **gin_trgm_ops** el cuál usa trigramas para dvidir los datos de una columa. Un trigrama es una estructura que divide una palabra en conjuntos de 3 letras. Es así que Postgres divide el texto de cada columna en trigramas y sobre ello aplica el índice para poder búscarlos.

## Ejemplo de trigramas
La palabra foo tiene los trigramas: "f", "fo", "foo", "oo"
La palalabra cat tiene los trigramas: "c", "ca", "cat", y "at"

**Para poder ver los trigramas en PostgreSQL podemos usar el siguiente comando: 

```psql
SELECT show_trgm("foo");
```

## Índice GIN y estructura BTree

El índice GIN es implementado usando un BTree. La diferencia es que un Btree estándar es de uno a uno, esto significa que cada record tiene un nodo en un índice Btree, y cada nodo mapea a un solo record. Con el índice GIN si el registro se dividen en 10 trigramas, este aparecerá en 10 lugares en el índice GIN, y cada nodo en el índice GIN puede apuntar a varios registros. Tal como podemos apreciar en el siguiente gŕafico de una versión simplificado de la estructura del BTree del indice GIN: 

```
                        +-------------------+
                        |       Nodo A      |
                        |-------------------|
                        |       [abc]       |
                        |    /         \    |
                        |   /           \   |
                        |  /             \  |
                        | /               \ |
                        |/                 \|
   +-------------------+ V                   V +-------------------+
   |     Nodo B        |                       |     Nodo C        |
   |-------------------|                       |-------------------|
   |    [aab] [aba]    |                       |    [bca] [bcd]    |
   |                   |                       |                   |
   +-------------------+                       +-------------------+

```

Como se puede ver el Nodo A contiene la clave **[abc]** que representa el trigrama indezado en ese nivel. Asimismo tambien posee dos punteros salientes que apuntas a los nodos hijos, el nodo B y el nodo C. Es así que la si se buscara una clave, la cual previamente es convertida a trigrama, se tendría que empezar en el nodo A preguntando si la clave a buscar es menor a mayor que el trigrama en el nodo A, si es menor se deberá ir por el nodo B, caso contrario por el nodo C. 

## Diseño del índice con PostgreSQL
### Creación de la base de datos
La estructura de nuestra tabla, la se cargó los datos de los csv de **All the News** es la siguiente:

```psql
CREATE TABLE articles (
  number_db INTEGER,
  id INTEGER,
  title TEXT,
  publication TEXT,
  author TEXT,
  date_publication DATE NULL,
  year_publication NUMERIC NULL,
  moth_publication NUMERIC NULL,
  url_article TEXT,
  content TEXT
);
```

Asimismo, creó el índice en una nueva columna denominada **search_txt** que contiene los vectores caracteristicos del titulo de la noticia y el cuerpo de la noticia, cada uno con un peso diferente. Aquí se muestra el código utilizado para su creación:

```psql
create index articles_idx_search on articles using gin (search_txt);
```

## Conexión del Backend con la base de datos
La conexión con la base de datos se hace mediante el paquete **psycopg2**, es así que la query utilizada para realizar las búsquedas es la siguiente:
```py
""" SELECT id, title, ts_rank_cd(search_txt, query) AS score
FROM articles, phraseto_tsquery('english','{query}') query
WHERE query @@ search_txt
ORDER BY score DESC
LIMIT {top_k}; """
```
Se puede observar que los parámetros que varían son {query} y {top_k} que básicamente son datos que se traerán del frontend. Asimismo, se debe recalcar que se utiliza la función **phraseto_tsquery** para convertir la query en su vector caracteristico y así obtener un mejor resultado en la búsqueda. Por otro lado, también se implementa la función **ts_rank_cd** para obtener el grado de similitud de las conultas y obtener las k más relevantes, las cuales son señaladas con el parámetro **top_k**.
