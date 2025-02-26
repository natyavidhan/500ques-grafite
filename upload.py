from pymongo import MongoClient

import os
from dotenv import load_dotenv 
import json

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))

db = client['top500']

data  = {
    "physics": json.load(open("data/physics_cleaned_cleaned.json")),
    "chemistry": json.load(open("data/chemistry_cleaned_cleaned.json")),
    "maths": json.load(open("data/maths_cleaned_cleaned.json")),
}

for key in data:
    db[key].insert_many(data[key])
    