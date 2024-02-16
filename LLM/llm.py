"""
This module is an interface to get answer from LLM models you want.
"""

from bardapi import Bard
import openai
import requests
import json


class LLM:
    def __init__(self, llm_model, api_key=None):
        self.model_name = llm_model
        self.api = api_key

        if self.model_name not in ["bard", "gpt3", "ollama", "mock"]:
            raise Exception("Invalid LLM model")

        if self.model_name == "mock":
            print("Mock model created")
        elif (self.model_name != "ollama") and (self.api == "" or self.api == None):
            raise Exception("Invalid LLM api key")

        if self.model_name == "ollama":
            model_config = {
                "name": "summarizer",
                "modelfile": "FROM zephyr:latest\nSYSTEM Summarize the main points of the passage/text/article.",
            }
            requests.post("http://ollama:11434/api/create", json=model_config)
            print("ollama model created")

    def get_answer(self, question):
        print("llm model name: ", self.model_name)
        print("question: ", question)
        if self.model_name == "bard":
            self.model = Bard(self.api)
            return self.model.get_answer(question)

        elif self.model_name == "gpt3":
            openai.api_key = self.api

            response = openai.Completion.create(
                model="gpt-3.5-turbo",
                prompt="Q:" + question,
                temperature=0.4,
                stop=["\n"],
            )

            return response["choices"][0].text
        elif self.model_name == "ollama":
            data = {"model": "summarizer", "stream": False, "prompt": question}
            r = requests.post("http://ollama:11434/api/generate", json=data)
            pretty = json.loads(r.text)
            if "response" not in pretty:
                raise Exception(f"Error: {pretty}")
            if pretty["response"].endswith("<|endoftext|>"):
                return pretty["response"][:-13]
            else:
                return pretty["response"]

        elif self.model_name == "mock":
            return """This is a long text that is a mock answer.
                    It has multiple lines and is a long answer.
                    It is a mock answer for testing purposes.
            """

        else:
            raise Exception("Invalid LLM model in getting answer.")
