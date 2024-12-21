import time
from watchdog.observers import Observer
from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler,PatternMatchingEventHandler
import os
import json
from read_file import preprocess_csv
import pandas as pd
import re
from collections import deque
from queue import Queue
from threading import Thread

PROCESSED_FILES_LOG = "processed_files.json"

district_dict = {} #create a dictionary 
compeleted_dist = [] #for completed district

def load_processed_files():
    if os.path.exists(PROCESSED_FILES_LOG):
        with open(PROCESSED_FILES_LOG, "r") as f:
            return json.load(f)
    return []

def save_processed_files(processed_files):
    with open(PROCESSED_FILES_LOG, "w") as f:
        json.dump(processed_files, f)

processed_files = load_processed_files()
file_queue = deque()

def process_files_if_ready(file_path):
        global file_queue
        main_file_pattern = 'Grade_[4-6]_'
        competency_file_pattern = 'Karnataka_Questions_'
        # Extract file paths from the queue
        main_file_path = None
        competency_file_path = None

        file_name = os.path.basename(file_path)
        dir_name = os.path.dirname(file_path)

        if file_path in processed_files:
            print(f"{file_name} has already been processed.")
            return

        # Detect main and competency files
        if re.search(main_file_pattern, file_name):
            print("Main file path found")
            file_name_parts = re.split(r'[_\.]', file_name)
            grade = file_name_parts[1]
            if len(file_name_parts) == 3:
                district_name = file_name_parts[2]
            else:
                district_name = " ".join([file_name_parts[2], file_name_parts[3]])
            district_name_with_extension = file_name.split("_")[2]
            print("DISTRICT FILE EXTENSION:",district_name_with_extension)
            #district_name = os.path.splitext(district_name_with_extension)[0]
            
            print(f"Processing main file for grade: {grade}")
            print(f"Processing main file for district: {district_name}")
            df_main = pd.read_csv(file_path)

            '''if district_name not in district_dict:
                district_dict[district_name] = {}

            district_dict[district_name][grade] = df'''

        
        # Find the competency file in the same directory
            for file in os.listdir(dir_name):
                if re.search(competency_file_pattern, file):
                    competency_file_path = os.path.join(dir_name, file)
                    df_comp = pd.read_csv(competency_file_path)
                    preprocess_csv(file_path, competency_file_path, grade, dir_name,district_name)
                    break
                
        
        # Mark the file as processed
            processed_files.append(file_path)
            save_processed_files(processed_files)


class MyHandler(PatternMatchingEventHandler):
    
    

    def on_modified(self,event):
        print(f"File {event.src_path} has been modified")
    def on_created(self,event):
        
        print(f"File {event.src_path} has been created")
        time.sleep(1)
        file_queue.append(os.path.abspath(event.src_path))
        file_path = event.src_path
        if not event.is_directory:
            process_files_if_ready(file_path)
        
        

        
    def on_deleted(self,event):
        print(f"File {event.src_path} has been deleted")

if __name__ == "__main__":
    event_handler = MyHandler(patterns=["*.csv"],
                              ignore_patterns=[],
                              ignore_directories=True)
    observer = Observer()
    observer.schedule(event_handler,path=r"C:\Users\sastr\Akshara_Automate",recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()








    #Identify the grade

'''file_path_list = file_path.split("\\")
        print(file_path_list)

        pattern = 'Grade[4-6]'
        grade = re.findall(pattern,file_path_list[-1])
        print("GRADE :",grade)
        full_path = os.path.abspath(event.src_path)
        if file_extension == '.csv':
            print(f"Processing CSV file: {event.src_path}")
            try:
                df = pd.read_csv(full_path)
                print(df.head())
                #preprocess_csv(full_path,grade)
            except Exception as e:
                print(f"Error reading CSV file: {e}")'''