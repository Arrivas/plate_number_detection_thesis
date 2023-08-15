import os
from pymongo import MongoClient
from tkinter import messagebox

connection_string = 'mongodb://localhost:27017'
client = MongoClient(connection_string)

if client is None:
    print("Failed to connect to MongoDB.")
    exit()

dbs = client.list_database_names()

plate_number_db = client['plate_number_db']
plate_number_collection = plate_number_db['plate_numbers']
whitelists_collection = plate_number_db['whitelists']
blacklists_collection = plate_number_db['blacklists']

def insert_detected_plate_number(name, age, reason, plate_number, time_in, image_dir, on_whitelist, classification):
    try:
        is_on_whitelist = whitelists_collection.find_one({'plate_number': plate_number})
        fetched_classfication = ''
        if is_on_whitelist == None :
            fetched_classfication = classification
        else:
            fetched_classfication = is_on_whitelist['classification']
        print(fetched_classfication, 'asd')
        new_document = {
            "name": name,
            "age": age,
            "reason": reason,
            "plate_number": plate_number,
            "time_in": time_in,
            "image_dir": image_dir,
            "on_whitelist": on_whitelist,    
            "classification": fetched_classfication
        }

        inserted_id = plate_number_collection.insert_one(new_document).inserted_id
        print("Document inserted with ID:", inserted_id)
    except Exception as e:
        print("Error inserting document:", e)

def insert_whitelist(name, plate_number, classification):
    new_document = {
        "name": name,
        "plate_number": plate_number,
        "classification": classification
    }

    try:
        inserted_id = whitelists_collection.insert_one(new_document).inserted_id
        messagebox.showinfo(title='Inserted', message="Whitelist inserted successfully")
    except Exception as e:
        print("Error inserting document:", e)


def get_plate_numbers():
    plate_numbers_detected = plate_number_collection.find()
    return list(plate_numbers_detected)

def get_whitelists():
    whitelists = whitelists_collection.find()
    return list(whitelists)

def get_plate_numbers_detected_length():
    plate_numbers_detected = plate_number_collection.find()
    return len(list(plate_numbers_detected))

def get_whitelists_length():
    whitelists = whitelists_collection.find()
    return len(list(whitelists))

def check_whitelist(plate_number):
    matched_plate_number = whitelists_collection.find_one({"plate_number": plate_number})
    if matched_plate_number:
        return True
    return False

def delete_whitelist_entry(name):
    whitelists_collection.delete_one({"name": name})
    messagebox.showinfo(title='Deleted', message="Whitelist deleted successfully")

def update_whitelist_entry(name, plate_number, classification):
    whitelists_collection.update_one(
        {"name": name},
        {"$set": {"plate_number": plate_number, "name": name, "classification":classification}}
    )
    messagebox.showinfo(title='Updated', message="Whitelist updated successfully")