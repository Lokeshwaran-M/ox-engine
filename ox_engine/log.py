import os
import json
from datetime import datetime
from ox_engine  import do

class Log:

    def __init__(self):
        self.fd_path = os.path.join(os.path.expanduser("~"), "ox.db")
        do.mk_fd(self.fd_path)

 
    def push(self, data):
        """
        Pushes the given input to a JSON file with the current date and time.

        Args:
            data (any): The data to be logged.

        Returns:
            None
        """

        current_time = datetime.now().strftime("%I:%M:%S-%p")  # Accurate time with AM/PM
        current_date = datetime.now().strftime('%d-%m-%Y')
        log_file = f"{current_date}.json"
        filepath = os.path.join(self.fd_path, log_file)

        try:
            with open(filepath, 'r+') as file:  # Open in append mode
                content = json.load(file) if os.path.getsize(filepath) > 0 else {}
                content[current_time] = data
                file.seek(0)  # Move to the beginning of the file
                json.dump(content, file, indent=4)  # Formatted JSON

        except (FileNotFoundError, json.JSONDecodeError):  # Handle missing file or invalid JSON
            with open(filepath, 'w') as file:
                json.dump({current_time: data}, file, indent=4)

        print(f"logged data : log {current_time} {log_file}.json path={filepath}")

    def pull(self, time=None, date=datetime.now().strftime('%d-%m-%Y')):
        """
        Retrieves a specific log entry from a JSON file based on date and time.

        Args:
            time (str): The time of the log entry in the format used by push (e.g., "10:30:00-AM").
            date (str): The date of the log entry in the format used by push (e.g., "04-06-2024").

        Returns:
            any: The log data associated with the specified time and date, or None if not found.
        """

        log_file = f"{date}.json"
        filepath = os.path.join(self.fd_path, log_file)
        log_entries = [] 

        ip = datetime.now().strftime('%p')
        itime = 0
        if("-" in time):
            itime,ip = time.split("-")
        else:
            itime=time
        itime_arr= itime.split(":")
        itime_arr.append(ip)
        try:
            with open(filepath, 'r') as file:  # Open in read mode

                content = json.load(file)
               
                if not time:  
                    log_entries.extend(content.values())
                elif time in content:  
                    data =content[time]
                    log_entries.append({"key": time, "data": data})
                elif(len(time)>0) :
                    for log_key, data in content.items():
                        log_time,log_p = log_key.split("-")
                        log_h, log_m, log_s= log_time.split(":")

                        if [log_h,log_p] ==itime_arr:
                            log_entries.append({"key": log_time, "data": data})
                        if [log_h, log_m,log_p] ==itime_arr:
                            log_entries.append({"key": log_time, "data": data})
                  

                      # Log entry not found

        except (FileNotFoundError, json.JSONDecodeError):
            # Handle missing file or invalid JSON
            # Indicate log entry not found
            print(f"Unable to locate log entry for {time} on {date}.")  # Optional message for missing entry
        print(log_entries)
        return log_entries

       




