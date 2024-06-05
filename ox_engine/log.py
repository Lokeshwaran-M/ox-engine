import os
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
        key=datetime.now().strftime("%I:%M:%S-%p"),
        tag=datetime.now().strftime("%d-%m-%Y"),
    ):
        """
        Pushes data to the log file. Can be called with either data or both key and data.

        Args:
            data (any, optional): The data to be logged.
            key (str, optional): The key for the log entry. Defaults to eg: ("04-06-2024") current_date
            tag (str, optional): The tag for the log entry. Defaults to eg: ("10:30:00-AM") current_time with AM/PM
        Returns:
            None
        """

        log_file = f"{tag}.json"
        file_db_path = os.path.join(self.db_path, log_file)

        try:
            with open(file_db_path, "r+") as file:  # Open in append mode
                content = json.load(file) if os.path.getsize(file_db_path) > 0 else {}
                content[key] = data
                file.seek(0)  # Move to the beginning of the file
                json.dump(content, file, indent=4)  # Formatted JSON

        except (
            FileNotFoundError,
            json.JSONDecodeError,
        ):  # Handle missing file or invalid JSON
            with open(file_db_path, "w") as file:
                json.dump({key: data}, file, indent=4)

        print(f"logged data : {key} {log_file} \npath={file_db_path}")

    def pull(self, key=None, tag=datetime.now().strftime("%d-%m-%Y")):
        """
        Retrieves a specific log entry from a JSON file based on date and time.

        Args:
            key (any or optional): datakey or The time of the log entry in the format used by push eg: ("10:30:00-AM").
            tag (any or optional): tag or date of the log entry in the format used by push eg: ("04-06-2024").
        Returns:
            any: The log data associated with the specified key,time and tag,date or None if not found.
        """

        log_file = f"{tag}.json"
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
        try:
            with open(file_db_path, "r") as file:  # Open in read mode

                content = json.load(file)

                if key is None:
                    for log_key, data in content.items():
                        log_entries.append({"tag": tag, "key": log_key, "data": data})
                elif key in content:
                    data = content[key]
                    log_entries.append({"tag": tag, "key": key, "data": data})
                elif len(key) > 0:
                    for log_key, data in content.items():
                        log_time, log_p = log_key.split("-")
                        log_h, log_m, log_s = log_time.split(":")

                        if [log_h, log_p] == itime_arr:
                            log_entries.append({"tag": tag, "key": log_key, "data": data})
                        if [log_h, log_m, log_p] == itime_arr:
                            log_entries.append({"tag": tag, "key": log_key, "data": data})

                    # Log entry not found

        except (FileNotFoundError, json.JSONDecodeError):
            # Handle missing file or invalid JSON
            # Indicate log entry not found
            print(
                f"Unable to locate log entry for {key} on {tag}."
            )  # Optional message for missing entry

        return log_entries
