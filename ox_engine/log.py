import os
import bson
import json
from datetime import datetime
from .vector import Vector

vec = Vector()

class Log:

    def __init__(self, db="",db_path=None):
        """
        Initiate instances of the db.ox-db
        
        Args:
            db (str, optional): The name of the db or path/name that gets accessed or instantiated. Defaults to "".
        
        Returns:
            None
        """
        self.set_db(db, db_path)
        self.doc = None
        self.doc_format = "bson"

    def set_db(self,db,db_path=None):
        self.db = db
        self.db_path = db_path if db_path else os.path.join(os.path.expanduser("~"), db + ".ox-db")
        os.makedirs(self.db_path, exist_ok=True)  # Create directory if it doesn't exist

    def current_db(self):
        return self.db_path

    def set_doc(self,doc,doc_format=None):
        self.doc = doc or self.doc
        self.doc_format = doc_format or self.doc_format

    def current_doc(self):
        return self.doc

    def push(self, data, key=None, doc=None, doc_format=None):
        """
        Pushes data to the log file. Can be called with either data or both key and data.
        
        Args:
            data (any, optional): The data to be logged.
            key (str, optional): The key for the log entry. Defaults to eg: ("04-06-2024") current_date
            doc (str, optional): The doc for the log entry. Defaults to eg: ("10:30:00-AM") current_time with AM/PM
        
        Returns:
            None
        """
        doc_format = doc_format or self.doc_format 
        self._validate_doc_format(doc_format)

        data = [data,vec.encode(data)]

        key = key or datetime.now().strftime("%I:%M:%S-%p")
        doc = doc or (self.doc or datetime.now().strftime("%d-%m-%Y"))
    
        log_file = self._get_logfile_path(doc, doc_format)
        try:
            with open(log_file, "rb+" if doc_format == 'bson' else "r+") as file:
                content = self._load_content(file, doc_format)
                if key in content:
                    key = self._create_unique_key(content, key)
                content[key] = data
                self._save_content(file, content, doc_format)
        except FileNotFoundError:
            with open(log_file, "wb" if doc_format == 'bson' else "w") as file:
                self._save_content(file, {key: data}, doc_format)

        print(f"logged data : {key} \n{log_file}")

    def pull(self, key=None, doc=None, doc_format=None,return_embeddings=False):
        """
        Retrieves a specific log entry from a BSON or JSON file based on date and time.
        
        Args:
            key (any or optional): datakey or The time of the log entry in the format used by push eg: ("10:30:00-AM").
            doc (any or optional): doc or date of the log entry in the format used by push eg: ("04-06-2024").
        
        Returns:
            any: The log data associated with the specified key,time and doc,date or None if not found.
        """
        doc_format = doc_format or self.doc_format
        self._validate_doc_format(doc_format)
        doc = doc or (self.doc or datetime.now().strftime("%d-%m-%Y"))
        log_file = self._get_logfile_path(doc, doc_format)
        log_entries = []
        try:
            with open(log_file, "rb" if doc_format == 'bson' else "r") as file:
                content = self._load_content(file, doc_format)
                if key is None:
                    log_entries = [{"doc": doc, "key": log_key, "data": data if return_embeddings else data[0]}
                                   for log_key, data in content.items()]
                elif key in content:
                    data = content[key]
                    log_entries.append({"doc": doc, "key": key, "data": data if return_embeddings else data[0]})
                else:
                    log_entries.extend(self._search_by_time_key(content, key, doc, return_embeddings))
        except (FileNotFoundError, bson.errors.BSONError, json.JSONDecodeError):
            print(f"Unable to locate log entry for {key} on {doc}.")

        return log_entries


    def search(self,query,topn=10,key=None, doc=None, doc_format=None):

        query = vec.encode(query)
        dataset = self.pull(key, doc, doc_format,return_embeddings=True)
        dataset_len = len(dataset)
        sim_score =dict()
        for i in range(dataset_len):
            sim_score[i]= Vector.sim(query,dataset[i]["data"][1])

        sim_score_list = list(sim_score.items())

        sorted_sim_score_list = sorted(sim_score_list, key=lambda x: x[1])
        result= []
        reslen = topn if topn < dataset_len else dataset_len
        for idx in range (reslen):
            resdata = dataset[sorted_sim_score_list[idx][0]]
            resdata["data"] = resdata["data"][0]
            resdata["sim_score"] = sorted_sim_score_list[idx][1]
            result.append(resdata)

        return result

    def _get_logfile_path(self, doc, doc_format):
        return os.path.join(self.db_path, f"{doc}.{doc_format}")

    def _validate_doc_format(self, doc_format):
        if doc_format not in ["bson", "json"]:
            raise ValueError("doc_format must be 'bson' or 'json'")
        
    def _create_unique_key(self,dictionary, key, num=0):
        new_key = key + "|" + str(num)
        if new_key not in dictionary:
            return new_key
        else:
            # Recursively call to create a new unique key with incremented number
            return self._create_unique_key(dictionary, key, num + 1)

    def _load_content(self, file, doc_format):
        if doc_format == "bson":
            file_content = file.read()
            return bson.decode_all(file_content)[0] if file_content else {}
        else:
            is_empty = file.tell() == 0
            return json.load(file) if is_empty else {}

    def _save_content(self, file, content, doc_format):
        if doc_format == "bson":
            file.seek(0)
            file.truncate()
            file.write(bson.encode(content))
        else:
            file.seek(0)
            file.truncate()
            json.dump(content, file, indent=4)

    def _search_by_time_key(self, content, key, doc, return_embeddings):
        log_entries = []
        itime, ip = key.split("-") if "-" in key else (key, datetime.now().strftime("%p"))
        itime_parts = itime.split(":") + [ip]

        for log_key, data in content.items():
            log_time_parts = log_key.split("-")[0].split(":") + [log_key.split("-")[1]]
            if log_time_parts[:len(itime_parts) - 1] == itime_parts[:-1]:
                if itime_parts[-1] == itime_parts[-1]:
                    log_entries.append({"doc": doc, "key": log_key, "data": data if return_embeddings else data[0]})
        return log_entries


