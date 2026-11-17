import os
from openai import OpenAI
from openai.types.chat import ChatCompletion


client = OpenAI(
    base_url="http://localhost:11434/v1/", 
    api_key="ollama"
    )

def chat(messages, tools):
    resp = client.chat.completions.create(
        model="gemma4:latest",
        messages=messages,
        tools=tools,
    )
    return resp.choices[0].message