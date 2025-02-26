from pymongo import MongoClient

import os
from dotenv import load_dotenv 
import json

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))

db = client['top500']

data  = {
    "physics": json.load(open("data/physics.json")),
    "chemistry": json.load(open("data/chemistry.json")),
    "maths": json.load(open("data/maths.json")),
}

for key in data:
    db[key].insert_many(data[key])
    