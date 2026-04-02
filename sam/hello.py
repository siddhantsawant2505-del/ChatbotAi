import google.generativeai as genai

genai.configure(api_key="AIzaSyC5Lu-8cmfCWMTWWW13_SQDTkLQdgX1J00")

models = genai.list_models()
for model in models:
    print(model.name)
