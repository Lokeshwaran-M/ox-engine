import os
import bson
import json
from datetime import datetime
from .vector import Vector
from ox_engine import do

vec = Vector()


class Log:

    def __init__(self, db="", db_path=None):
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

    def set_db(self, db, db_path=None):
        self.db = db
        self.db_path = (
            db_path if db_path else os.path.join(os.path.expanduser("~"), db + ".ox-db")
        )
        os.makedirs(self.db_path, exist_ok=True)  # Create directory if it doesn't exist

    def get_db(self):
        return self.db_path

    def set_doc(self, doc=None, doc_format="bson"):
        self.doc = doc or self.doc
        if doc_format not in ["bson", "json"]:
            raise ValueError("doc_format must be 'bson' or 'json'")
        self.doc_format = doc_format

    def get_doc(self):
        return [self.doc,self.doc_format]

    def push(self, data, embeddings=None, key=None, doc=None,):
        """
        Pushes data to the log file. Can be called with either data or both key and data.

        Args:
            data (any, optional): The data to be logged.
            key (str, optional): The key for the log entry. Defaults to eg: ("04-06-2024") current_date
            doc (str, optional): The doc for the log entry. Defaults to eg: ("10:30:00-AM") current_time with AM/PM

        Returns:
            None
        """
        if data == "" or data==None:
            raise ValueError("ox-db : no prompt is given")
        data_store = {"data": data, "embeddings": embeddings}

        doc = doc or self.doc
        uid = self.gen_uid(key, doc)
        splited_uid = uid.split("-")
        doc_name = doc if doc else "lgd-" + splited_uid[3]

        log_file = self._get_logfile_path(doc_name)
        try:
            with open(log_file, "rb+" if self.doc_format == "bson" else "r+") as file:
                content = self._load_content(file)
                if uid in content:
                    uid = self.gen_uid(key, doc)
                content[uid] = data_store
                self._save_content(file, content)
        except FileNotFoundError:
            with open(log_file, "wb" if self.doc_format == "bson" else "w") as file:
                self._save_content(file, {uid: data_store})

        print(f"ox-db : logged data : {uid} \n{log_file}")

    def pull(self, key=None, uid=None, time=None, doc=None, date=None):
        """
        Retrieves a specific log entry from a BSON or JSON file based on date and time.

        Args:
            key (any or optional): datakey or The time of the log entry in the format used by push eg: ("10:30:00-AM").
            doc (any or optional): doc or date of the log entry in the format used by push eg: ("04-06-2024").

        Returns:
            any: The log data associated with the specified key,time and doc,date or None if not found.
        """
        all_none = all(var is None for var in [key, uid, time, doc, date])

        doc = doc or (self.doc or "lgd-" + datetime.now().strftime("%d_%m_%Y"))
        log_file = self._get_logfile_path(doc)

        log_entries = []

        try:
            with open(log_file, "rb" if self.doc_format == "bson" else "r") as file:
                content = self._load_content(file)
                if all_none:
                    log_entries = [
                        {
                            "uid": uid,
                            "doc": doc,
                            "data": data_store["data"],
                            "embeddings": data_store["embeddings"],
                        }
                        for uid, data_store in content.items()
                    ]
          
                elif uid in content:
                    data_store = content[uid]
                    log_entries.append(
                        {
                            "uid": uid,
                            "doc": doc,
                            "data": data_store["data"],
                            "embeddings": data_store["embeddings"],
                        }
                    )
              
                else:
                    log_entries.extend(
                        self._search_by_segment(content, key, time, doc, date)
                    )

        except (FileNotFoundError, bson.errors.BSONError, json.JSONDecodeError):
            print(f"ox-db : unable to locate log entry for {key} on {doc}.")

        return log_entries
    
    def update(self, uid, data, embeddings=None,  doc=None,):
     
        data_store = {"data": data, "embeddings": embeddings}

        doc = doc or self.doc

        splited_uid = uid.split("-")
        doc_name = doc if doc else "lgd-" + splited_uid[3]

        log_file = self._get_logfile_path(doc_name)
        try:
            with open(log_file, "rb+" if self.doc_format == "bson" else "r+") as file:
                content = self._load_content(file)
                if uid in content:
                    content[uid] = data_store
                self._save_content(file, content)
        except FileNotFoundError:
            with open(log_file, "wb" if self.doc_format == "bson" else "w") as file:
                self._save_content(file, {uid: data_store})

        print(f"ox-db : updated data  {uid} \n{log_file}")

    def search(
        self,
        query,
        topn=10,
        key=None,
        uid=None,
        time=None,
        doc=None,
        date=None,
        return_embaddings=False,
    ):

        query = vec.encode(query)
        dataset = self.pull(key, uid, time, doc, date)
        dataset_len = len(dataset)
        sim_score = dict()
        for i in range(dataset_len):
            embaddings = dataset[i]["embeddings"]
            if not embaddings:
                embaddings = vec.encode(dataset[i]["data"])
            sim_score[i] = Vector.sim(query, embaddings)

        sim_score_list = list(sim_score.items())

        sorted_sim_score_list = sorted(sim_score_list, key=lambda x: x[1])
        result = []
        reslen = topn if topn < dataset_len else dataset_len
        for idx in range(reslen):
            resdata = dataset[sorted_sim_score_list[idx][0]]

            resdata["sim_score"] = sorted_sim_score_list[idx][1]

            if not return_embaddings:
                resdata["embeddings"] = None
            result.append(resdata)

        return result

    def show(
        self,
        key=None,
        uid=None,
        time=None,
        doc=None,
        date=None,
        return_embaddings=False,
    ):
        dataset = self.pull(key, uid, time, doc, date)
        if return_embaddings:
            return dataset
        dataset_len = len(dataset)
        result = []
        for i in range(dataset_len):
            resdata = dataset[i]
            resdata["embeddings"] = None
            result.append(resdata)
        return result
    
    def embed_all(self,doc):
               
        doc = doc or (self.doc or "lgd-" + datetime.now().strftime("%d_%m_%Y"))
        log_file = self._get_logfile_path(doc)

        try:
            with open(log_file, "rb" if self.doc_format == "bson" else "r") as file:
                content = self._load_content(file)
                for uid, data_store in content.items():
                    if not data_store["embeddings"]:
                        content[uid]["embeddings"] = vec.encode(data_store["data"])

        except (FileNotFoundError, bson.errors.BSONError, json.JSONDecodeError):
            print(f"Unable to locate log entry for on {doc}.")  


    def _get_logfile_path(self, doc):
        doc_format = self.doc_format
        return os.path.join(self.db_path, f"{doc}.{doc_format}")



    def gen_uid(self, key=None, doc=None):

        time = datetime.now().strftime("%I:%M:%S_%p")
        date = datetime.now().strftime("%d_%m_%Y")

        key = key if key else "key"
        doc = doc if doc else "lgd"
        uid = (
            key
            + "-"
            + doc
            + "-"
            + time
            + "-"
            + date
            + "-"
            + do.generate_random_string()
        )

        return uid

    def _load_content(self, file):
        doc_format = self.doc_format
        if doc_format == "bson":
            file_content = file.read()
            return bson.decode_all(file_content)[0] if file_content else {}
        else:
            is_empty = file.tell() == 0
            return json.load(file) if is_empty else {}

    def _save_content(self, file, content):
        doc_format = self.doc_format
        if doc_format == "bson":
            file.seek(0)
            file.truncate()
            file.write(bson.encode(content))
        else:
            file.seek(0)
            file.truncate()
            json.dump(content, file, indent=4)

    def _search_by_segment(self, content, key, time, doc, date):
        log_entries = []
        itime_parts = [None,None,None,None]
        idate_parts = [None,None,None,]

        if time:
            itime, ip = (
                time.split("_")
                if "_" in time
                else (time, datetime.now().strftime("%p"))
            )
            itime_parts = itime.split(":") + [ip]

        if date:
            idate_parts = date.split("_") if "_" in date else date
       
        for uid, data_store in content.items():
            log_it = False

            uid_parts = uid.split("-")
            uid_time_parts = uid_parts[2].split("_")[0].split(":") + [
                uid_parts[2].split("_")[1]
            ]
            uid_date_parts = uid_parts[3].split("_")

            if uid_time_parts[: len(itime_parts) - 1] == itime_parts[:-1]:
                if uid_time_parts[-1] == itime_parts[-1]:
                    log_it = True
              
            elif uid_date_parts[: len(idate_parts)] == idate_parts:
                log_it = True
          
            elif key == uid_parts[0]:
                log_it = True

            else:
                log_it = False

            if log_it:
                log_entries.append(
                    {
                        "uid": uid,
                        "doc": doc,
                        "data": data_store["data"],
                        "embeddings": data_store["embeddings"],
                    }
                )

        return log_entries
