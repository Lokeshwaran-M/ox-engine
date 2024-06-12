import os
import bson
import json
from datetime import datetime
from ox_engine import do


class Log:

    def __init__(self, db=""):
        """
        Initiate instances of the db.ox-db

        Args:
            db (str, optional): The name of the db or path/name that gets accessed or instantiated. Defaults to "".
        Returns:
            None
        """
        self.db_path = os.path.join(os.path.expanduser("~"), db + ".ox-db")
        do.mk_fd(self.db_path)

    def push(
        self,
        data,
        key=None,
        doc=None,
        doc_format="bson"
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
        if key==None:
            key=datetime.now().strftime("%I:%M:%S-%p")
        if doc==None:
            doc=datetime.now().strftime("%d-%m-%Y")
        if doc_format not in ["bson", "json"]:
            raise ValueError("doc_format must be 'bson' or 'json'")

        log_file = f"{doc}.{doc_format}"
        file_db_path = os.path.join(self.db_path, log_file)

        if doc_format == "bson":

            try:
                with open(file_db_path, "rb+") as file:  # Open in read/write binary mode
                    file_content = file.read()
                    if file_content:
                        content = bson.decode_all(file_content)[0]  # Assuming there's only one document in the BSON file
                    else:
                        content = {}
                    
                    content[key] = data
                    
                    file.seek(0)  # Move to the beginning of the file
                    file.truncate()  # Ensure no leftover data
                    file.write(bson.encode(content))  # Wrap content in a list before encoding
            except FileNotFoundError:  # Handle missing file
                with open(file_db_path, "wb") as file:
                    file.write(bson.encode({key: data}))  # Wrap data in a dictionary before encoding
                    
        else:
            try:
                with open(file_db_path, "r+") as file:  # Open in read/write text mode
                    content = json.load(file) if os.path.getsize(file_db_path) > 0 else {}
                    content[key] = data
                    file.seek(0)  # Move to the beginning of the file
                    json.dump(content, file, indent=4)  # Formatted JSON
                    file.truncate()  # Ensure no leftover data
            except (FileNotFoundError, json.JSONDecodeError):  # Handle missing file or invalid JSON
                with open(file_db_path, "w") as file:
                    json.dump({key: data}, file, indent=4)

        print(f"logged data : {key} {log_file}")

    def pull(self, key=None, doc=None, doc_format="bson"):
        """
        Retrieves a specific log entry from a BSON or JSON file based on date and time.

        Args:
            key (any or optional): datakey or The time of the log entry in the format used by push eg: ("10:30:00-AM").
            doc (any or optional): doc or date of the log entry in the format used by push eg: ("04-06-2024").
        Returns:
            any: The log data associated with the specified key,time and doc,date or None if not found.
        """
        if doc==None:
            doc=datetime.now().strftime("%d-%m-%Y")
        if doc_format not in ["bson", "json"]:
            raise ValueError("doc_format must be 'bson' or 'json'")

        log_file = f"{doc}.{doc_format}"
        file_db_path = os.path.join(self.db_path, log_file)
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

        if doc_format == "bson":

            try:
                with open(file_db_path, "rb") as file:  # Open in binary read mode
                    content = bson.decode_all(file.read())[0] 

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
                            
                            if [log_h, log_p] == itime_arr:
                                log_entries.append({"doc": doc, "key": log_key, "data": data})
                            if [log_h, log_m, log_p] == itime_arr:
                                log_entries.append({"doc": doc, "key": log_key, "data": data})

                        # Log entry not found

            except (FileNotFoundError,  bson.errors.BSONError):
                # Handle missing file or invalid BSON
                # Indicate log entry not found
                print(f"Unable to locate log entry for {key} on {doc}.")  # Optional message for missing entry


        else:
            try:
                with open(file_db_path, "r") as file:  # Open in read mode
                    content = json.load(file)
                    content_dict = {k: {"_id": k, "data": v} for k, v in content.items()}

                    if key is None:
                        for log_key, data in content_dict.items():
                            log_entries.append({"doc": doc, "key": log_key, "data": data['data']})
                    elif key in content_dict:
                        data = content_dict[key]['data']
                        log_entries.append({"doc": doc, "key": key, "data": data})
                    elif len(key) > 0:
                        for log_key, data in content_dict.items():
                            log_time, log_p = log_key.split("-")
                            log_h, log_m, log_s = log_time.split(":")

                            if [log_h, log_p] == itime_arr:
                                log_entries.append({"doc": doc, "key": log_key, "data": data['data']})
                            if [log_h, log_m, log_p] == itime_arr:
                                log_entries.append({"doc": doc, "key": log_key, "data": data['data']})

                        # Log entry not found

            except (FileNotFoundError, json.JSONDecodeError):
                # Handle missing file or invalid JSON
                # Indicate log entry not found
                print(
                    f"Unable to locate log entry for {key} on {doc}."
                )  # Optional message for missing entry

        return log_entries
