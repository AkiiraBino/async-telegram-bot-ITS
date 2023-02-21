import json

def get_standart_phrase(type_text):
    file = open("data\\standart_phrase.json", encoding='utf-8')
    text = json.load(file)
    return text[type_text]

def get_answers(type_text):
    file = open("data\\answers.json", encoding='utf-8')
    text = json.load(file)
    return text[type_text]

def get_speciality(type_text):
    file = open("data\\speciality.json", encoding='utf-8')
    text = json.load(file)
    return text[type_text]

def get_test(type_text):
    file = open("data\\test.json", encoding='utf-8')
    text = json.load(file)
    return text[type_text]