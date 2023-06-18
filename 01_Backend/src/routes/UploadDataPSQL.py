from flask import Blueprint, jsonify
import json
import io
from database.db import get_connection
import time


main = Blueprint('uploadData_blueprint', __name__)


@main.route('/<size>')
def load_data_in_postgres(size):
    start_time = time.time()
    try:

        connection = get_connection()

        postgres_insert_query = "DROP TABLE IF EXISTS articles_database CASCADE;"
        connection.cursor().execute(postgres_insert_query)

        postgres_insert_query = "SET enable_seqscan = off;"
        connection.cursor().execute(postgres_insert_query)

        # now we create the table and load the entries and implement the GIN index

        connection.cursor().execute("CREATE TABLE IF NOT EXISTS articles_database(id_ TEXT , submitter TEXT, authors TEXT, title TEXT, comments_ TEXT, journal TEXT, doi TEXT, report_no TEXT, categories TEXT, license TEXT, abstract TEXT, versions TEXT, update_date TEXT, authors_parsed TEXT);")
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

                postgres_insert_query = "INSERT INTO articles_database (id_, submitter, authors, title, comments_, journal, doi, report_no, categories, license, abstract, versions, update_date, authors_parsed) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
                record_to_insert = (doc_id, doc_submitter, doc_authors, doc_title, doc_comments, doc_journal, doc_doi, doc_report_no, doc_categories, doc_license, doc_abstract, doc_versions, doc_update_date, doc_authors_par)
                connection.cursor().execute(postgres_insert_query, record_to_insert)

                counter += 1
                if counter >= int(size): 
                    break

            file.close()  

        # -- crear una nueva columna
        connection.cursor().execute("alter table articles_database add column search_txt tsvector;")

        # -- crear los vectores de terminos para el par: title, description
        connection.cursor().execute("update articles_database set search_txt = R.weight from (select id_, to_tsvector('english', abstract) as weight from articles_database) R where R.id_ = articles_database.id_;")

        # -- crear el indice
        connection.cursor().execute("create index json_idx_search on articles_database using GIN (search_txt);")


        connection.commit()
        connection.cursor().close()
        connection.close()

        end_time = time.time()
        execution_time = end_time - start_time

        result = {'mensaje': 'PostgreSQL completado con éxito', 'execution_time': round(execution_time, 3)}
        return jsonify(result)

    except Exception as ex:
        return jsonify({'message': str(ex)}), 500

