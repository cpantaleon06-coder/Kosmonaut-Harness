import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(base_url="http://localhost:11434/v1/", api_key="ollama")

def chat(messages, tools):
    resp = client.chat.completions.create(
        model="gemma4",
        messages=messages,
        tools=tools,
    )
    return resp.choices[0].message