import os
import bson
import json
from datetime import datetime
from ox_engine.db.vector import Vector
from ox_engine.util import do


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
        self.set_doc()
        self.vec = Vector()

    def set_db(self, db, db_path=None):
        self.db = db
        self.db_path = (
            db_path if db_path else os.path.join(os.path.expanduser("~"), db + ".ox-db")
        )
        os.makedirs(self.db_path, exist_ok=True)  # Create directory if it doesn't exist

    def get_db(self):
        return self.db_path

    def set_doc(self, doc=None, doc_format="bson"):
        if doc is None:
            self.doc = self.doc or f"log_{datetime.now():[%d%m%Y]}"
        elif self.doc:
            if self.doc == doc:
                return self.doc
            else :
                self.doc = doc
        
            
        self.doc_path = os.path.join(self.db_path, self.doc)
        os.makedirs(self.doc_path, exist_ok=True)
        if doc_format not in ["bson", "json"]:
            raise ValueError("doc_format must be 'bson' or 'json'")
        self.doc_format = doc_format

        file_content = self.load_data(self.doc + ".index")
        if "doc_entry" not in file_content:
            file_content["doc_entry"] = 0
            self.save_data(self.doc + ".index", file_content)
        self.doc_entry = file_content["doc_entry"]

        return self.doc

    def get_doc(self):
        return self.doc or self.set_doc()

    def push(
        self,
        data,
        embeddings=None,
        data_story=None,
        key=None,
        doc=None,
    ):
        """
        Pushes data to the log file. Can be called with either data or both key and data.

        Args:
            data (any, optional): The data to be logged.
            key (str, optional): The key for the log entry. Defaults to eg: ("04-06-2024") current_date
            doc (str, optional): The doc for the log entry. Defaults to eg: ("10:30:00-AM") current_time with AM/PM

        Returns:
            None
        """
        doc = self.set_doc(doc) if doc else self.get_doc()
        uid = self.gen_uid(key, doc)


        if data == "" or data == None:
            raise ValueError("ox-db : no prompt is given")
        if not embeddings:
            embeddings = self.vec.encode(data)

        data_story = {
            "uid": uid,
            "key": key,
            "doc": doc,
            "time": datetime.now().strftime("%I:%M:%S_%p"),
            "date": datetime.now().strftime("%d_%m_%Y"),
            "vec_model":self.vec.md_name,
            "discription":"",
            "meta_data":[],
        }

        self._push(uid, data_story, doc + ".index")
        self._push(uid, data, doc)
        self._push(uid, embeddings, doc + ".ox-vec")

    def pull(self, key=None, uid=None, time=None, date=None, doc=None):
        """
        Retrieves a specific log entry from a BSON or JSON file based on date and time.

        Args:
            key (any or optional): datakey or The time of the log entry in the format used by push eg: ("10:30:00-AM").
            doc (any or optional): doc or date of the log entry in the format used by push eg: ("04-06-2024").

        Returns:
            any: The log data associated with the specified key,time and doc,date or None if not found.
        """
        all_none = all(var is None for var in [key, uid, time, date])

        doc = doc or (self.doc or "log_" + datetime.now().strftime("[%d%m%Y]"))
    

        args = [key, uid, time, date]
        for i in range(len(args)) :
            if type(args[i]) == str :
                args[i] = [args[i]]
            elif args[i]== None :
                args[i] = []
            
        [keys, uids, times, dates] = args

        log_entries = []

        content = self.load_data(doc)
        if all_none:
            for uid, data in content.items():
                if uid == "ox-db_init":
                    continue
                log_entries.append(
                {
                    "uid": uid,
                    "data": data,
                })

        if len(uids)!=0 :
            for uid in uids :
                if uid in content:
                    data = content[uid]
                    log_entries.append(
                        {
                            "uid": uid,
                            "data": data,
                        }
                    )

        if any([key, time, date]):
            log_entries.extend(self._search_by_segment(content, key, time,  date,doc))

        return log_entries

    def search(
        self,
        query,
        topn=10,
        key=None,
        uid=None,
        time=None,
        date=None,
        doc=None,
    ):
        doc = doc or (self.doc or "log_" + datetime.now().strftime("[%d%m%Y]"))
        log_entries = self.pull(key, uid, time, date, doc + ".ox-vec")
        log_entries_len = len(log_entries)
        dataset = []
        for i in range(log_entries_len):
            dataset.append(log_entries[i]["data"])

        top_idx = self.vec.search(query, dataset, topn=topn)

        uids = []

        for idx in top_idx:
            uids.append(log_entries[idx]["uid"])
        resdata = self.pull(uid=uids,doc=doc)

        return resdata

    def show(
        self,
        key=None,
        uid=None,
        time=None,
        doc=None,
        date=None,
    ):
        pass

    def embed_all(self, doc):
        pass

    def gen_uid(self, key=None, doc=None):

        time = datetime.now().strftime("%I:%M:%S_%p")
        date = datetime.now().strftime("%d_%m_%Y")

        key = key or "key"
        doc = doc or (self.doc or "log")
        uid = (
            str(self.doc_entry)
            + "-"
            + key
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

    def _get_logfile_path(self, log_file):

        self.doc_path = self.doc_path or os.path.join(self.db_path, self.doc)
        logfile_path = os.path.join(self.doc_path, f"{log_file}.{self.doc_format}")
        return logfile_path

    def _push(self, uid, data, log_file):

        if data == "" or data == None:
            raise ValueError("ox-db : no prompt is given")

        file_content = self.load_data(log_file)
        file_content[uid] = data
        if "." in log_file:
            if log_file.split(".")[1] == "index":
                file_content["doc_entry"] += 1
                self.doc_entry = file_content["doc_entry"]
        self.save_data(log_file, file_content)

        print(f"ox-db : logged data : {uid} \n{log_file}")

    def load_data(self, log_file):
        log_file_path = self._get_logfile_path(log_file)
        try:
            with open(
                log_file_path, "rb+" if self.doc_format == "bson" else "r+"
            ) as file:
                if self.doc_format == "bson":
                    file_content = file.read()
                    return bson.decode_all(file_content)[0] if file_content else {}
                else:
                    is_empty = file.tell() == 0
                    return json.load(file) if is_empty else {}
        except FileNotFoundError:
            file_content = {"ox-db_init": log_file}
            self.save_data(log_file, file_content)
            return file_content

    def save_data(self, log_file, file_content):
        log_file_path = self._get_logfile_path(log_file)

        def write_file(file, content, format):
            file.seek(0)
            file.truncate()
            if format == "bson":
                file.write(bson.encode(content))
            else:
                json.dump(content, file, indent=4)

        try:
            mode = "rb+" if self.doc_format == "bson" else "r+"
            with open(log_file_path, mode) as file:
                write_file(file, file_content, self.doc_format)
        except FileNotFoundError:
            mode = "wb" if self.doc_format == "bson" else "w"
            with open(log_file_path, mode) as file:
                write_file(file, file_content, self.doc_format)

    def _search_by_segment(self, content, key, time,  date,doc):
        log_entries = []
        itime_parts = [None, None, None, None]
        idate_parts = [
            None,
            None,
            None,
        ]

        if time:
            itime, ip = (
                time.split("_")
                if "_" in time
                else (time, datetime.now().strftime("%p"))
            )
            itime_parts = itime.split(":") + [ip]

        if date:
            idate_parts = date.split("_") if "_" in date else [date]

        for uid, data in content.items():
            if uid == "ox-db_init":
                continue
            
            log_it = False

            uid_parts = uid.split("-")
            uid_time_parts = uid_parts[3].split("_")[0].split(":") + [
                uid_parts[3].split("_")[1]
            ]
            uid_date_parts = uid_parts[4].split("_")

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
                        "data": data,
                    }
                )

        return log_entries
