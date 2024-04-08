"""
This module is an interface to get answer from LLM models you want.
"""

import openai
import requests
import json
from openai import OpenAI
import google.generativeai as genai


class LLM:
    def __init__(self, llm_model, api_key=None):
        self.model_name = llm_model
        self.api = api_key
        self.llm_prompt = "You are a summarizing AI. Provide a comprehensive summary of the given video script? The summary should cover all the key points and main ideas presented in the original text, while also condensing the information into a concise and easy-to-understand format. Ensure that the summary includes relevant details and examples that support the main ideas, while avoiding any unnecessary information or repetition. The length of the summary should be appropriate for the length and complexity of the original text, providing a clear and accurate overview without omitting any important information. Do not mention that it is an video script. Answer only English text."

        if self.model_name not in ["bard", "gpt3", "ollama", "mock"]:
            raise Exception("Invalid LLM model")

        if self.model_name == "mock":
            print("Mock model created")
        print("llm model name: ", self.model_name)
        print("api key: ", self.api)

        if self.model_name == "ollama":
            model_config = {
                "name": "summarizer",
                "modelfile": "FROM mistral:7b-instruct\nSYSTEM " + self.llm_prompt,
                "options": {
                    "num_ctx": 20000,
                },
            }
            requests.post("http://ollama:11434/api/create", json=model_config)
            print("ollama model created")

        if self.model_name == "gpt3":
            openai.api_key = self.api
            print("gpt3 model created")

        if self.model_name == "bard":

            genai.configure(api_key="API_KEY")
            generation_config = {
                "temperature": 1,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 1000000,
            }
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
            ]

            self.model = genai.GenerativeModel(
                model_name="gemini-1.0-pro",
                generation_config=generation_config,
                safety_settings=safety_settings,
            )

    def get_finance_answer(self, question):

        genai.configure(api_key="API_KEY")
        generation_config = {
            "temperature": 1,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 1000000,
        }
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
        ]

        finance_model = genai.GenerativeModel(
            model_name="gemini-1.0-pro",
            generation_config=generation_config,
            safety_settings=safety_settings,
        )

        convo = finance_model.start_chat()

        convo.send_message(
            "Is this a finance text? Answer only one of these options: 'Yes', 'No' \n\n"
            + question
        )
        print(convo.last.text)

        # return if contains yes in the answer
        return "yes" in convo.last.text.lower()

    def get_answer(self, question):
        print("llm model name: ", self.model_name)
        print("question: ", question)
        # if self.model_name == "bard":
        #     self.model = Bard(self.api)
        #     return self.model.get_answer(question)

        if self.model_name == "gpt3":

            client = OpenAI(api_key=self.api)

            completion = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[
                    {
                        "role": "system",
                        "content": self.llm_prompt,
                    },
                    {
                        "role": "user",
                        "content": question,
                    },
                ],
            )
            print(completion.choices[0].message)
            message_str = str(completion.choices[0].message.content)
            return message_str
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

        elif self.model_name == "bard":

            convo = self.model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [self.llm_prompt],
                    },
                    {
                        "role": "model",
                        "parts": [
                            "Okay, I will provide a comprehensive summary of the given video script. Please provide the text you would like me to summarize."
                        ],
                    },
                ]
            )

            convo.send_message(question)
            print(convo.last.text)

            return convo.last.text
        elif self.model_name == "mock":
            return """This is a long text that is a mock answer.
                    It has multiple lines and is a long answer.
                    It is a mock answer for testing purposes.
            """

        else:
            raise Exception("Invalid LLM model in getting answer.")
