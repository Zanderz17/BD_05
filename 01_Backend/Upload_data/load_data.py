import psycopg2
import json
import io

def load_data_in_postgres(docs_to_read):
    try:
        conn = psycopg2.connect("dbname=db_proyect_arxiv user=postgres  password=161049") # user and password may change depending on ur settings
        
        cur = conn.cursor()

        postgres_insert_query = "DROP TABLE IF EXISTS json_to_pos CASCADE;"
        cur.execute(postgres_insert_query)

        postgres_insert_query = "SET enable_seqscan = off;"
        cur.execute(postgres_insert_query)

        # now we create the table and load the entries and implement the GIN index

        cur.execute("CREATE TABLE IF NOT EXISTS json_to_pos(id_ TEXT , submitter TEXT, authors TEXT, title TEXT, comments_ TEXT, journal TEXT, doi TEXT, report_no TEXT, categories TEXT, license TEXT, abstract TEXT, versions TEXT, update_date TEXT, authors_parsed TEXT);")
        counter = 0
        with open('./DataBase/data.json', 'r') as file:
            for line in file: # a line is a document
                line = line.rstrip()
                doc_object = json.load(io.StringIO(line)) # load the json object

                doc_id          = str(doc_object.get("id"))
                doc_submitter   = str(doc_object.get("submitter"))
                doc_authors     = str(doc_object.get("authors"))
                doc_title       = str(doc_object.get("title"))
                doc_comments    = str(doc_object.get("comments"))
                doc_journal     = str(doc_object.get("journal"))
                doc_doi         = str(doc_object.get("doi"))
                doc_report_no   = str(doc_object.get("report-no"))
                doc_categories  = str(doc_object.get("categories"))
                doc_license     = str(doc_object.get("license"))
                doc_abstract    = str(doc_object.get("abstract"))
                doc_versions    = str(doc_object.get("versions"))
                doc_update_date = str(doc_object.get("update_date"))
                doc_authors_par = str(doc_object.get("authors_parsed"))

                postgres_insert_query = "INSERT INTO json_to_pos (id_, submitter, authors, title, comments_, journal, doi, report_no, categories, license, abstract, versions, update_date, authors_parsed) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                record_to_insert = (doc_id, doc_submitter, doc_authors, doc_title, doc_comments, doc_journal, doc_doi, doc_report_no, doc_categories, doc_license, doc_abstract, doc_versions, doc_update_date, doc_authors_par)
                cur.execute(postgres_insert_query, record_to_insert)

                counter += 1
                if counter >= docs_to_read:
                    break

            file.close()  

        # now the gin index

        # -- crear una nueva columna
        cur.execute("alter table json_to_pos add column search_txt tsvector;")

        # -- crear los vectores de terminos para el par: title, description
        cur.execute("update json_to_pos set search_txt = R.weight from (select id_, setweight(to_tsvector('english', abstract), 'A') as weight from json_to_pos) R where R.id_ = json_to_pos.id_;")

        # -- crear el indice
        cur.execute("create index json_idx_search on json_to_pos using GIN (search_txt);")


        conn.commit()
        cur.close()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
