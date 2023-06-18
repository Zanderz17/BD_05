##############
import json
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import time
import linecache as lc
import os
import io
import sys
from queue import PriorityQueue
import nltk
nltk.download('punkt')
from nltk.stem.snowball import SnowballStemmer
import math
##############

##### Principal Class and Functions ##########
cwd = os.getcwd() # get the current working directory
cwd = os.path.join(cwd, 'templates')

stoplist_filename       = "stoplist.txt" # stoplist filename
data_filename           = "arxiv-metadata.json" # data filename
inv_ind_filename        = "inv_ind" # inverted_index filename
norm_doc_filename       = "norm_doc.json" # vector norm document filename
final_inv_ind_filename  = "final_inv_ind.json"
aux_docs_to_read_file   = "docs_to_read.txt"

stoplist_path       = os.path.join(cwd + "/stoplist/"                       , stoplist_filename)
data_path           = os.path.join(cwd + "/documents/data/"                 , data_filename)
norm_doc_path       = os.path.join(cwd + "/documents/norm_doc/"             , norm_doc_filename)
final_inv_ind_path  = os.path.join(cwd + "/documents/final_inverted_index/"  , final_inv_ind_filename)
inv_ind_path        = cwd + "/documents/inverted_index/" + inv_ind_filename
path_to_clean_1     = cwd + "/documents/norm_doc"
path_to_clean_2     = cwd + "/documents/inverted_index"
path_to_clean_3     = cwd + "/documents/final_inverted_index"
data_folder_path    = cwd + "/documents/data/"
datafile_size       = os.path.getsize(data_path)
aux_docs_read_path  = cwd + "/documents/data/" + aux_docs_to_read_file


class TextRetriever():
    terminos_procesados = 0
    NUMBER_OF_DOCUMENTS = 0
    AUX_FILE_NUMBER = 1
    BLOCK_SIZE = 0 # bytes
    accesos_disco_stoplist = 0
    accesos_disco_inverted_index = 0
    accesos_disco_DF = 0
    accesos_disco_merging = 0
    accesos_disco_data = 0
    accesos_a_norm_doc_for_normalization = 0
    accesos_getlines_from_inv_ind = 0
    docs_to_read = 0
    stoplist = []
    docs_ids = []
    scores = {}

    def __init__(self):#, docs_to_read):


        self.load_stoplist()

        # print("El dataset completo pesa: " + str(self.B_to_MB(datafile_size)) + " MB") # MB
        # print("Los documentos escogidos a cargar pesan: " + str(docs_to_read*2.44*0.001) + " MB")
        # aprox_bloques_por_crear, aprox_block_size = self.approximation(docs_to_read)
        # print("Se calcula la creación de aproximadamente " + str(aprox_bloques_por_crear) 
        # + " archivos (bloques), con un block_size de " + str(aprox_block_size) + " MB cada uno")
        # self.BLOCK_SIZE = self.MB_to_B(aprox_block_size*2) # to reduce the scale according to the approximation from the file size
        
    def get_disk_accesses(self):
        print("Accesos a stoplist: " + str(self.accesos_disco_stoplist))
        print("Accesos a los indices invertidos temporales: " + str(self.accesos_disco_inverted_index))
        print("Accesos a final_inverted_index: " + str(self.accesos_disco_merging + self.accesos_getlines_from_inv_ind))
        print("Accesos a dataset file: " + str(self.accesos_disco_data))
        print("Accesos al documento de normas: " + str(self.accesos_a_norm_doc_for_normalization + self.accesos_disco_DF))
        return (self.accesos_disco_stoplist + self.accesos_disco_inverted_index + self.accesos_disco_DF + self.accesos_disco_merging + self.accesos_disco_data + self.accesos_a_norm_doc_for_normalization + self.accesos_getlines_from_inv_ind)

    def approximation(self):
        aprox_bloques_por_crear = round(math.log(int(self.docs_to_read), 2),3)
        # Se aproxima de distintas fuentes que un documento pesa aproximadamente 2.44 KB, entonces: (1KB = 0.001MB)
        aprox_block_size = round((int(self.docs_to_read) / aprox_bloques_por_crear)*2.44*0.001,5) # This is a conversion from KB to MB

        return aprox_bloques_por_crear, aprox_block_size

    def MB_to_B(self, MB):
        return round(MB*1048576,3)

    def B_to_MB(self, B):
        return round(B/1048576,3)

    def procesamiento_palabra(self, word):
        new_word = ""
        abecedario = "abcdefghijklmnopqrstuvwxyz"
        for c in word:
            if c in abecedario:
                new_word = new_word + c
            else:
                new_word = new_word + '-' # in case of rare characters
        return new_word.strip('-') # we remove them


    def preprocesamiento(self, texto): # tokenization | Stopwords filter | Stemming
        # tokenizar

        palabras = nltk.word_tokenize(texto.lower())

        try:
            # filtrar stopwords
            palabras_limpias = []
            for token in palabras:
                if token not in self.stoplist:
                    palabras_limpias.append(token)

            # process each clean word
            final_clean_words = []
            for clean_token in palabras_limpias:
                word = self.procesamiento_palabra(clean_token)
                if word != "": # else it was not a word at all
                    final_clean_words.append(word)

            # reducir palabras
            stemmer = SnowballStemmer(language='english')

            for i in range(len(final_clean_words)):
                final_clean_words[i] = stemmer.stem(final_clean_words[i])
            
            return final_clean_words

        except IOError:
            print("Problem reading: " + stoplist_filename + " path.")



    def insert_document_into_local_inverted_index(self, local_inverted_index, texto, doc_id):
    # the local inverted index has the following form: [keyword] -> {doc_id_1, freq}, {doc_id_2, freq}, ...
    # a dictionary of a dictionary of integers
        for token in texto:
            if token in local_inverted_index:
                if doc_id in local_inverted_index[token]: # more than 1 appearance in the same doc
                    local_inverted_index[token][doc_id] = local_inverted_index[token][doc_id] + 1
                else: # first appearance in the document, but not first appearance of the keyword
                    local_inverted_index[token][doc_id] = 1
            else: # first appearance of the keyword
                local_inverted_index[token] = {doc_id: 1} 



    def get_size(self, obj, seen=None):
        """Recursively finds size of objects"""
        size = sys.getsizeof(obj)
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        # Important mark as seen *before* entering recursion to gracefully handle
        # self-referential objects
        seen.add(obj_id)
        if isinstance(obj, dict):
            size += sum([self.get_size(v, seen) for v in obj.values()])
            size += sum([self.get_size(k, seen) for k in obj.keys()])
        elif hasattr(obj, '__dict__'):
            size += self.get_size(obj.__dict__, seen)
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum([self.get_size(i, seen) for i in obj])
        return size



    def upload_block_to_disk(self, local_inverted_index):
        # sent
        sorted_keys = sorted(local_inverted_index.keys())
        try:
            if not os.path.exists(cwd + "/documents/inverted_index"):
                os.makedirs(cwd + "/documents/inverted_index")
            with open(inv_ind_path + str(self.AUX_FILE_NUMBER) + ".json", 'a', encoding = "utf-8") as inv_ind_file:
                self.accesos_disco_inverted_index += 1
                for keyword in sorted_keys:
                    inv_ind_file.write(json.dumps({keyword: local_inverted_index[keyword]}, ensure_ascii = False))
                    inv_ind_file.write("\n")
                inv_ind_file.close()
            local_inverted_index.clear()
            return 1
        except IOError:
            print("Problem reading: " +  str(self.AUX_FILE_NUMBER) + " path.")
            return 0



    def check_block_size(self, local_inverted_index):
        size = self.get_size(local_inverted_index)
        if size >= self.BLOCK_SIZE:
            print("uploading block " + str(self.AUX_FILE_NUMBER) + " to disk...")
            if(self.upload_block_to_disk(local_inverted_index)):
                print("block " + str(self.AUX_FILE_NUMBER) + " successfully uploaded.")
                self.AUX_FILE_NUMBER = self.AUX_FILE_NUMBER + 1
            else:
                print("Error uploading the block " + str(self.AUX_FILE_NUMBER) + " to disk.")



    def process_document_frequency(self, document_frequency, doc_id):
        sum = 0
        for key in document_frequency:
            sum = sum + ( math.log(1 + document_frequency[key], 10) * math.log(1 + document_frequency[key], 10) )
        sum = math.sqrt(sum)
        json_object = json.dumps({doc_id: sum}, ensure_ascii = False)
        return json_object


    def upload_document_frequency_to_disk(self, documents_frequencies_list):
        try:
            if not os.path.exists(cwd + "/documents/norm_doc"):
                os.makedirs(cwd + "/documents/norm_doc")
            with open(norm_doc_path, 'a', encoding = "utf-8") as norm_file:
                self.accesos_disco_DF += 1
                for document_frequency in documents_frequencies_list:
                    norm_file.write(document_frequency)
                    norm_file.write("\n")
            norm_file.close()
        except IOError:
            print("Problem reading: " + norm_doc_filename + " path.")
            return 0

    def clean_directories(self):
        self.terminos_procesados = 0
        self.NUMBER_OF_DOCUMENTS = 0
        self.AUX_FILE_NUMBER = 1
        self.BLOCK_SIZE = 0 # bytes
        self.accesos_disco_stoplist = 0
        self.accesos_disco_inverted_index = 0
        self.accesos_disco_DF = 0
        self.accesos_disco_merging = 0
        self.accesos_disco_data = 0
        self.docs_read = 0
        self.accesos_a_norm_doc_for_normalization = 0
        self.accesos_getlines_from_inv_ind = 0
        self.stoplist = []
        self.docs_ids = []
        self.scores = {}
        
        clean_dir_1 = os.listdir(path_to_clean_1) # archivos de normas
        clean_dir_2 = os.listdir(path_to_clean_2) # archivo de indices invertidos
        clean_dir_3 = os.listdir(path_to_clean_3) # Indice invertidos finales
        
        for file in clean_dir_1:
            os.remove(path_to_clean_1 + "/" + file)
        for file in clean_dir_2:
            os.remove(path_to_clean_2 + "/" + file)
        for file in clean_dir_3:
            os.remove(path_to_clean_3 + "/" + file)

    def initialize_list_of_buffers(self, buffers, active_files_index, priority_queue, buffers_line_number):
        for i in range(self.AUX_FILE_NUMBER):
            inv_ind = lc.getline(inv_ind_path + str(i+1) + ".json", 1).rstrip() # get first line from the auxiliar file. which is the keywords and a posting list of all the documents it appears, along with the document frequency of each document.
            self.accesos_getlines_from_inv_ind += 1
            if inv_ind != "":
                json_object = json.load(io.StringIO(inv_ind)) # load json object
                key = list(json_object.keys()) # get keywords from the json object
                buffer_format_list = [key[0], list(json_object.get(key[0]).items())] # list of keyword and its posting lists
                buffers.append(buffer_format_list) # append the line as a list [keyword, posting lists] to read_buffer (and the line of reading for each file)
    # buffers has 1 entry from each auxiliar file, they are in order so its getting the first from each auxiliar file
                buffers_line_number.append(2) # next line starting from 1
                priority_queue.put((buffers[i][0], i)) # append to priority_queue the keyword and the auxiliar file it is in.
                # print(buffers)
                active_files_index.append(i) # stores 0, 1, 2, 3, 4, 5, 6, ... (auxiliar files remaining)
            # print(buffers[i])
        
        
    def merge(self, buffers, active_files_index, priority_queue, buffers_line_number):
        aux_list = []
        try:
            while not priority_queue.empty():
                temp_inv_ind = {} # to store the new inverted_index keyword (but complete)
                keyword, index_file = priority_queue.get() 
                temp_inv_ind["keyword"] = keyword
                temp_inv_ind["IDF"] = 0 # temporal inverted document frequency
                temp_inv_ind["doc-ids"] = [] # list of doc id's

                if buffers[index_file][0] == temp_inv_ind["keyword"]:
                    for posting_list in buffers[index_file][1]: # getting the posting list
                        temp_inv_ind["doc-ids"].append(posting_list)
# replace the buffer read
                    inv_ind = lc.getline(inv_ind_path + str(index_file+1) + ".json", buffers_line_number[index_file]).rstrip()
                    self.accesos_getlines_from_inv_ind += 1 
                    buffers_line_number[index_file] = buffers_line_number[index_file] + 1
                    if inv_ind == "": # end of the file has been reached
                        active_files_index.remove(index_file)
                        os.remove(inv_ind_path + str(index_file+1) + ".json")
                    else:
                        json_object = json.load(io.StringIO(inv_ind)) # load json object
                        key = list(json_object.keys()) # get keywords from the json object
                        buffers[index_file] = [key[0], list(json_object.get(key[0]).items())] # list of keyword and its posting lists
                        priority_queue.put((buffers[index_file][0], index_file)) # add next keyword to priority queue from document
                else:
                    print("ERROR DE MAGNITUD DESPROPORCIONADA!")

                while not priority_queue.empty():
                    other_keyword, other_index_file = priority_queue.get()
                    if other_keyword == keyword:
                        for posting_list in buffers[other_index_file][1]: # getting the posting list
                            temp_inv_ind["doc-ids"].append(posting_list) 
# replace the buffer read
                        inv_ind = lc.getline(inv_ind_path + str(other_index_file+1) + ".json", buffers_line_number[other_index_file]).rstrip() 
                        self.accesos_getlines_from_inv_ind += 1
                        buffers_line_number[other_index_file] = buffers_line_number[other_index_file] + 1
                        if inv_ind == "": # end of the file has been reached
                            active_files_index.remove(other_index_file)
                            os.remove(inv_ind_path + str(other_index_file+1) + ".json")
                        else:
                            json_object = json.load(io.StringIO(inv_ind)) # load json object
                            key = list(json_object.keys()) # get keywords from the json object
                            buffers[other_index_file] = [key[0], list(json_object.get(key[0]).items())] # list of keyword and its posting lists
                            priority_queue.put((buffers[other_index_file][0], other_index_file)) # add next keyword to priority queue from document
                    else:
                        # print("Se acabo el keyword " + str(keyword) + ", ahora estamos en " + str(other_keyword))
                        priority_queue.put((other_keyword, other_index_file))
                        break

        # at this point, 1 keyword has been succesfully processed (it means we have the complete posting lists for that keyword)
        # to avoid many accesses to disk, we store it into a list and when it reaches a specific size, we upload it to disk (as a block)

                temp_inv_ind["IDF"] = round(math.log(self.NUMBER_OF_DOCUMENTS/len(temp_inv_ind["doc-ids"]), 10), 5) # log_10(number_documents / document frequency)
            
                aux_list.append(temp_inv_ind)
                
                if len(aux_list) > 1000: # procesamos de 1000 en 1000   
                    if not os.path.exists(cwd + "/documents/final_inverted_index"):
                        os.makedirs(cwd + "/documents/final_inverted_index")                
                    with open(final_inv_ind_path, 'a', encoding="utf-8") as final_inv_ind:
                        self.accesos_disco_merging += 1
                        for inv_ind in aux_list:
                            final_inv_ind.write(json.dumps(inv_ind, ensure_ascii=False)) # write to file
                            final_inv_ind.write("\n")
                            self.terminos_procesados = self.terminos_procesados + 1 # number of terms processed + 1
                        aux_list.clear()
                    final_inv_ind.close()

        # upload last block of merged terms
            if not os.path.exists(cwd + "/documents/final_inverted_index"):
                os.makedirs(cwd + "/documents/final_inverted_index")
            with open(final_inv_ind_path, 'a', encoding="utf-8") as final_inv_ind:
                self.accesos_disco_merging += 1
                for inv_ind in aux_list:
                    final_inv_ind.write(json.dumps(inv_ind, ensure_ascii=False)) # write to file
                    final_inv_ind.write("\n")
                    self.terminos_procesados = self.terminos_procesados + 1 # number of terms processed + 1
                aux_list.clear()
            final_inv_ind.close()

            print("Se procesaron " + str(self.terminos_procesados) + " terminos, en un total de " + str(self.NUMBER_OF_DOCUMENTS) + " documentos")
            return 1

        except IOError:
            print("Problem reading: " + final_inv_ind_filename + " path.")
            return 0

    def load_stoplist(self):
        with open(stoplist_path, encoding='latin-1') as f:
            self.accesos_disco_stoplist += 1
            for line in f:
                self.stoplist.append(line.strip())
        f.close()

        self.stoplist += [',', '!', '.', '?', '-', ';','"','¿',')','(','[',']','>>','<<','\'\'','``', '%', '$','_','-','{','}',"'"]
            

    def load(self):
        counter = 0
        factor = 1
        print("Processing only a total of " + str(self.docs_to_read) + " documents. (parameter specified)")
        local_inverted_index = {}
        documents_frequencies_list = []
        try:
            with open(data_path, 'r') as f:
                self.accesos_disco_data += 1
                for line in f: # a line is a document
                    document_frequency = {}
                    line = line.rstrip()
                    doc_object = json.load(io.StringIO(line)) # load the json object

    # separate the attributes needed (the id and the abstract) // maybe also the title
                    doc_id = doc_object.get("id") 
                    texto_procesado = self.preprocesamiento(doc_object.get("abstract"))
                    self.insert_document_into_local_inverted_index(local_inverted_index, texto_procesado, doc_id)

    # update the document_frequency
                    for token in texto_procesado:
                        if token in document_frequency:
                            document_frequency[token] = document_frequency[token] + 1
                        else:
                            document_frequency[token] = 1

    # insert into documents_frequencies_list, we do this to avoid accessing to disk each time a document is read, instead we send a block of frequency documents
                    blocks_for_DF = int(math.log(int(self.docs_to_read), 2))
                    document_frequency = self.process_document_frequency(document_frequency, doc_id)
                    documents_frequencies_list.append(document_frequency)
                    if len(documents_frequencies_list) >= int(self.docs_to_read)/blocks_for_DF:
                        self.upload_document_frequency_to_disk(documents_frequencies_list)
                        # for document_frequency in documents_frequencies_list:
                        #     self.upload_document_frequency_to_disk(document_frequency) 
                        documents_frequencies_list.clear() 

    # checking local_inverted_index size, if it exceeds the block size, we store it into an auxiliar file, else, we continue
    # we avoid doing the cheking after every word insertion to avoid a lot of computation and to handle the 'leftovers' from a document (the id's)
                    self.check_block_size(local_inverted_index) # here the local_inverted_index is sent to disk and cleaned or not

                    self.NUMBER_OF_DOCUMENTS = self.NUMBER_OF_DOCUMENTS + 1

                    counter += 1

                    if counter > 1000*factor:
                        print(counter)
                        factor += 1
                    

                    # STOPPER: JUST FOR TESTING
                    if self.NUMBER_OF_DOCUMENTS >= int(self.docs_to_read):
                        break

            f.close()
    # uploading last block of document_frequencies
            self.upload_document_frequency_to_disk(documents_frequencies_list)
            documents_frequencies_list.clear() 

    # check the last block (it probably has not exceed the BLOCK_SICE limits)
            size = self.get_size(local_inverted_index)
            if size > 0:
                print("uploading block " + str(self.AUX_FILE_NUMBER) + " to disk...")
                if(self.upload_block_to_disk(local_inverted_index)):
                    print("block " + str(self.AUX_FILE_NUMBER) + " successfully uploaded.")
                else:
                    print("Error uploading the block " + str(self.AUX_FILE_NUMBER) + " to disk.")

    # at this points, all documents have been processed
            print("Se crearon " + str(self.AUX_FILE_NUMBER) + " archivos que contienen indices invertidos.")
            print("Se procesaron un total de " + str(self.NUMBER_OF_DOCUMENTS) + " documentos del dataset.")

    # merging process
    # essential variables 
            buffers = [] # this buffer reads from each inv_ind_file. It is a list of buffers
            priority_queue = PriorityQueue() # to keep the buffers ordered
            active_files_index = [] # keep track of the inv_ind files that are completed or not (to remove the files)
            buffers_line_number = []

            print("Merging files...")
            self.initialize_list_of_buffers(buffers, active_files_index, priority_queue, buffers_line_number) # reading the first line from each inv_ind_file
            if(self.merge(buffers, active_files_index, priority_queue, buffers_line_number)):
                print("The files were successfully merged.")
            else:
                print("Error merging the files.")
        except IOError:
            print("Problem reading: " + data_filename + " path.")


    def binary_search(self, query_doc_frequency, query_keyword_inv_ind):
        for keyword in query_doc_frequency:
            low = 1
            high = self.terminos_procesados
            while low <= high:
                mid = (low + high) // 2
                candidate = lc.getline(final_inv_ind_path, mid).rstrip()
                self.accesos_getlines_from_inv_ind += 1
                candidate_json = json.load(io.StringIO(candidate))
                token = candidate_json.get("keyword") # get token from the line read
                if token < keyword:
                    low = mid + 1
                elif token > keyword:
                    high = mid - 1
                else:
                    query_keyword_inv_ind[keyword] = dict(candidate_json)
                    break

    def tf_idf_weight_and_cosine_score(self, query_keyword_inv_ind, query_doc_frequency):
        for keyword in query_keyword_inv_ind:
            query_tf_idf_weight = math.log(query_doc_frequency[keyword] + 1, 10) * query_keyword_inv_ind[keyword]["IDF"]
            for doc_id, frequency in query_keyword_inv_ind[keyword]["doc-ids"]:
                if doc_id not in self.scores:
                    self.scores[doc_id] = 0.0 # Valor temporal. Solo para que el se cree el término en el diccionario
                    self.docs_ids.append(doc_id)
                document_tf_idf_weight = math.log(frequency + 1, 10) * query_keyword_inv_ind[keyword]["IDF"]
                
                self.scores[doc_id] += query_tf_idf_weight * document_tf_idf_weight


    def score_normalization(self):
        query_norms = {}
        
        print(self.docs_to_read)
        print(type(self.docs_to_read))
        try:
            if not os.path.exists(cwd + "/documents/norm_doc"):
                os.makedirs(cwd + "/documents/norm_doc")
            with open(norm_doc_path, 'r', encoding="utf-8") as norm_doc:
                counter = 0
                self.accesos_a_norm_doc_for_normalization += 1
                for line in norm_doc:
                    json_object = json.load(io.StringIO(line))
                    key = list(json_object.keys())
                    if key[0] in self.docs_ids:
                        query_norms[key[0]] = json_object.get(key[0])
                    counter += 1
                    if counter >= int(self.docs_to_read):
                        print(counter)
                        break
                norm_doc.close()
            for doc_id in self.scores:
                self.scores[doc_id] = self.scores[doc_id] / query_norms[doc_id] # normalization

        except IOError:
            print("Problem reading: " + norm_doc_filename + " path.")

    def get_documents(self, documents_retrieved):
        try:
            with open(data_path, 'r', encoding="utf-8") as datafile:
                self.accesos_disco_data += 1
                counter = 0
                for document in datafile:
                    json_object = json.load(io.StringIO(document))
                    counter = counter + 1
                    doc_id = str(json_object.get("id"))
                    if doc_id in self.scores:
                        documents_retrieved[doc_id] = json_object 
                    if counter >= int(self.docs_to_read):
                        break
                datafile.close()
        except IOError:
            print("Problem reading: " + data_filename + " path.")


    def score(self, query, k):
        if self.NUMBER_OF_DOCUMENTS == 0:
            print("No documents were found. (0 documents loaded)")
            return 0
        # Procesar query
        query = self.preprocesamiento(query)
        
        # Variables
        query_doc_frequency = {}
        query_keyword_inv_ind = {}
        documents_retrieved = {}

        for token in query:
            if token in query_doc_frequency:
                query_doc_frequency[token] = query_doc_frequency[token] + 1
            else:
                query_doc_frequency[token] = 1
        
        print("Realizando busqueda binaria de los keyword en query.")
        self.binary_search(query_doc_frequency, query_keyword_inv_ind) # we get all posting lisit from keyword in query into query_keywords_inverted_index

        print("Calculando pesos TF_IDF y Cosine Score.")
        self.tf_idf_weight_and_cosine_score(query_keyword_inv_ind, query_doc_frequency)

        print("Normalizando vectores.")
        self.score_normalization()
 
        print("Ordenando scores.")
        self.scores = dict(sorted(self.scores.items(), key=lambda item: item[1], reverse = True)) # order the scores in descending order
        self.docs_ids = list(self.scores.keys())

        print("Buscando documentos en el dataset.")
        self.get_documents(documents_retrieved)

        print("El query ha retornado un total de " + str(len(documents_retrieved)) + " documentos")
        
        return k, documents_retrieved

    def retrieve(self, k, documents_retrieved):
        k = int(k) # parsing, bc we receive strings from the frontend
        documents_to_retrieve = []

        for i in range(k):
            if i < len(self.docs_ids):
                temp_doc = {}
                temp_doc["id"] = self.docs_ids[i]
                temp_doc["score"] = self.scores[self.docs_ids[i]]
                temp_doc["submitter"] = documents_retrieved[self.docs_ids[i]].get("submitter")
                temp_doc["authors"] = documents_retrieved[self.docs_ids[i]].get("authors")
                temp_doc["title"] = documents_retrieved[self.docs_ids[i]].get("title")
                temp_doc["comments"] = documents_retrieved[self.docs_ids[i]].get("comments")
                temp_doc["journal-ref"] = documents_retrieved[self.docs_ids[i]].get("journal-ref")
                temp_doc["doi"] = documents_retrieved[self.docs_ids[i]].get("doi")
                temp_doc["report-no"] = documents_retrieved[self.docs_ids[i]].get("report-no")
                temp_doc["categories"] = documents_retrieved[self.docs_ids[i]].get("categories")
                temp_doc["license"] = documents_retrieved[self.docs_ids[i]].get("license")
                temp_doc["abstract"] = documents_retrieved[self.docs_ids[i]].get("abstract")
                temp_doc["versions"] = documents_retrieved[self.docs_ids[i]].get("versions")
                temp_doc["update_date"] = documents_retrieved[self.docs_ids[i]].get("update_date")
                temp_doc["authors_parsed"] = documents_retrieved[self.docs_ids[i]].get("authors_parsed")
                documents_to_retrieve.append(temp_doc)
            else:
                break
        
        return documents_to_retrieve
        
    def load_data(self):

        time1 = time.time()
        self.load() 
        time2 = time.time()
        print("Document loading took " + str(round((time2 - time1) * 1000)) + " ms.")




    def search(self, query, k):

        time1 = time.time()
        k, documents_retrieved = self.score(query, k)
        time2 = time.time()
        tiempo_f1 = str(round((time2 - time1) * 1000))
        print("Query processing, score similarity and fetching similar documents took " + tiempo_f1 + " ms.")

        time1 = time.time()
        docs = self.retrieve(k, documents_retrieved)
        time2 = time.time()
        tiempo_f2 = str(round((time2 - time1) * 1000))
        print("Retrieving only the k documents took " + tiempo_f2 + " ms.")

        accesos = self.get_disk_accesses()
        print("se accedio a disco un total de: " + str(accesos))

        return docs, str(int(tiempo_f1) + int(tiempo_f2))
####################################################################
