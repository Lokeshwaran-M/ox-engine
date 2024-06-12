import os
import bson
import json
from datetime import datetime


class Log:

    def __init__(self, db=""):
        self.db_path = os.path.join(os.path.expanduser("~"), db + ".ox-db")
        os.makedirs(self.db_path, exist_ok=True)  # Create directory if it doesn't exist

    def _get_logfile_path(self, doc, doc_format):
        return os.path.join(self.db_path, f"{doc}.{doc_format}")

    def _validate_doc_format(self, doc_format):
        if doc_format not in ["bson", "json"]:
            raise ValueError("doc_format must be 'bson' or 'json'")

    def push(self, data, key=None, doc=None, doc_format="bson"):
        self._validate_doc_format(doc_format)

        if key is None:
            key = datetime.now().strftime("%I:%M:%S-%p")
        if doc is None:
            doc = datetime.now().strftime("%d-%m-%Y")

        log_file = self._get_logfile_path(doc, doc_format)

        try:
            with open(log_file, "rb+" if doc_format == 'bson' else "r+") as file:
                content = self._load_content(file, doc_format)
                content[key] = data
                self._save_content(file, content, doc_format)

        except FileNotFoundError:
            with open(log_file, doc_format + "wb" if doc_format == 'bson' else doc_format + "w") as file:
                self._save_content(file, {key: data}, doc_format)

        print(f"logged data : {key} \n{log_file}")

    def pull(self, key=None, doc=None, doc_format="bson"):
        self._validate_doc_format(doc_format)

        if doc is None:
            doc = datetime.now().strftime("%d-%m-%Y")
        log_file = self._get_logfile_path(doc, doc_format)
        log_entries = []

        ip = datetime.now().strftime("%p")
        itime = ""
        if key is None:
            pass
        elif "-" in key:
            itime, ip = key.split("-")
        else:
            itime = key
        itime_arr = itime.split(":")
        itime_arr.append(ip)


        try:
            with open(log_file, "rb" if doc_format == 'bson' else  "r") as file:
                content = self._load_content(file, doc_format)

                if key is None:
                    for log_key, data in content.items():
                        log_entries.append({"doc": doc, "key": log_key, "data": data})
                elif key in content:
                    data = content[key]
                    log_entries.append({"doc": doc, "key": key, "data": data})
                elif len(key) > 0:
                    for log_key, data in content.items():
                        log_time, log_p = log_key.split("-")
                        log_h, log_m, log_s = log_time.split(":")

                        if [log_h] == itime_arr[0]:
                            log_entries.append({"doc": doc, "key": log_key, "data": data})
                        if [log_h, log_p] == itime_arr:
                            log_entries.append({"doc": doc, "key": log_key, "data": data})
                        if [log_h, log_m, log_p] == itime_arr:
                            log_entries.append({"doc": doc, "key": log_key, "data": data})
                        if [log_h, log_m,log_s,log_p] == itime_arr:
                            log_entries.append({"doc": doc, "key": log_key, "data": data})   
                        



                # Log entry not found

        except (FileNotFoundError, bson.errors.BSONError, json.JSONDecodeError):
            # Handle missing file or invalid format
            print(f"Unable to locate log entry for {key} on {doc}.")

        return log_entries

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
