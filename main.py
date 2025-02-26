from flask import Flask, render_template, redirect, url_for, request
from pymongo import MongoClient
from dotenv import load_dotenv

import os

load_dotenv()

app = Flask(__name__)

client = MongoClient(os.getenv("MONGO_URI"))
db = client['top500']


def get_chapters(sub):
    return db[sub].distinct("chapter")

def get_questions(sub, chap):
    return db[sub].find({"chapter": chap})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<sub>')
def subject(sub):
    chapters = get_chapters(sub)
    return render_template('subject.html', sub=sub, chapters=chapters)

@app.route('/<sub>/<chap>')
def chapter(sub, chap):
    chap = chap.replace("-", " ")
    questions = get_questions(sub, chap)
    return render_template('questions.html', sub=sub, chapter=chap, questions=questions)


if __name__ == "__main__":
    app.run(debug=True)