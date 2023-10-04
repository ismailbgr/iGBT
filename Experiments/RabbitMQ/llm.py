"""
This module is used to get answer from LLM models you want. 

keybard="bgimLonoiGrtI2Ek1x5vIFdP1qZM0LxI0ckMz3uls08r_vaalvD9EPytBUOeblGO6-bEbQ."
keygpt3="sk-15zYoWmkbwyTx3s4KODOT3BlbkFJeP3XstKOcNLWj8K5oyYNsk-15zYoWmkbwyTx3s4KODOT3BlbkFJeP3XstKOcNLWj8K5oyYN"
"""
from bardapi import Bard
import openai
class LLM:
    def __init__(self, llm_model, api_key):
        self.model_name = llm_model
        self.api = api_key
        if self.model_name not in ["bard", "gpt3"]:
            raise Exception("Invalid LLM model")
        if self.api == "" or self.api == None:
            raise Exception("Invalid LLM api key")    


    def get_answer(self, question):
        if self.model_name == "bard":
            self.model = Bard(self.api)
            return self.model.get_answer(question)
        elif self.model_name == "gpt3":
            openai.api_key = self.api
            response = openai.Completion.create(
              model="gpt-3.5-turbo",
              prompt="Q:"+question,
              temperature=0.4,
              stop=["\n"]
            )
            return response["choices"][0].text
        else:
            raise Exception("Invalid LLM model in getting answer.")
    