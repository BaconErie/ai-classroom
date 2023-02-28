import os
import openai
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

openai.api_key = ''


def ai_output(string):
    ai_things = ""
    total_input = ""
    user_input = ""

    user_input = string
    total_input += user_input
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=total_input,
        temperature=0.3,
        max_tokens=100,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
  )
    text = response['choices'][0]['text']
    ai_things = text
    try:
        while text[0] == '!': 
            text = text[1:]
        while text[0] == '.': 
            text = text[1:-1]
        while text[0] == '?': 
            text = text[1:]
        while text[0] == ',': 
            text = text[1:]
        while text[0] == ' ': 
            text = text[1:]
        while text[0] == '\n':
            text = text[1:]
    except:
        pass
    text = "\n " + text
    text += "\n"

    total_input += text
    return ai_things