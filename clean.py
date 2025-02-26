import json, sys

files = ["data/physics_cleaned.json", "data/chemistry_cleaned.json", "data/maths_cleaned.json"]
stage = sys.argv[1]

for file in files:
    data = json.load(open(file, encoding='utf-8'))
    new_data = []
    
    if stage == "1":
        for chap, questions in data.items():
            for question in questions:
                question['chapter'] = chap
                new_data.append(question)
            
        with open(file.replace(".json", "_cleaned.json"), 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4)
            
    elif stage == "2":
        for question in data:
            question['text'] = question['text'].replace("cdn-question-pool.getmarks.app", "grafite-imgs-cdn.netlify.app")
            for option in question['options']:
                option['text'] = option['text'].replace("cdn-question-pool.getmarks.app", "grafite-imgs-cdn.netlify.app")
            new_data.append(question)
            
        with open(file.replace(".json", "_cleaned.json"), 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4)