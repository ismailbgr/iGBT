"""
This module is an interface to get answer from LLM models you want.
"""

from gemini import Gemini
import openai
import requests
import json
from openai import OpenAI

"""
Could you please provide a concise and comprehensive summary of the given text? The summary should capture the main points and key details of the text while conveying the author's intended meaning accurately. Please ensure that the summary is well-organized and easy to read, with clear headings and subheadings to guide the reader through each section. The length of the summary should be appropriate to capture the main points and key details of the text, without including unnecessary information or becoming overly long.
Can you provide a comprehensive summary of the given text? The summary should cover all the key points and main ideas presented in the original text, while also condensing the information into a concise and easy-to-understand format. Please ensure that the summary includes relevant details and examples that support the main ideas, while avoiding any unnecessary information or repetition. The length of the summary should be appropriate for the length and complexity of the original text, providing a clear and accurate overview without omitting any important information.
Could you please provide a summary of the given text, including all key points and supporting details? The summary should be comprehensive and accurately reflect the main message and arguments presented in the original text, while also being concise and easy to understand. To ensure accuracy, please read the text carefully and pay attention to any nuances or complexities in the language. Additionally, the summary should avoid any personal biases or interpretations and remain objective and factual throughout.
"""
"""
I got them by using this prompt I made:

“Dear ChatGPT,

I would like to request your assistance in creating an AI-powered prompt rewriter, which can help me rewrite and refine prompts that I intend to use with you, ChatGPT, for the purpose of obtaining improved responses. To achieve this, I kindly ask you to follow the guidelines and techniques described below in order to ensure the rephrased prompts are more specific, contextual, and easier for you to understand.

Identify the main subject and objective: Examine the original prompt and identify its primary subject and intended goal. Make sure that the rewritten prompt maintains this focus while providing additional clarity.

Add context: Enhance the original prompt with relevant background information, historical context, or specific examples, making it easier for you to comprehend the subject matter and provide more accurate responses.

Ensure specificity: Rewrite the prompt in a way that narrows down the topic or question, so it becomes more precise and targeted. This may involve specifying a particular time frame, location, or a set of conditions that apply to the subject matter.

Use clear and concise language: Make sure that the rewritten prompt uses simple, unambiguous language to convey the message, avoiding jargon or overly complex vocabulary. This will help you better understand the prompt and deliver more accurate responses.

Incorporate open-ended questions: If the original prompt contains a yes/no question or a query that may lead to a limited response, consider rephrasing it into an open-ended question that encourages a more comprehensive and informative answer.

Avoid leading questions: Ensure that the rewritten prompt does not contain any biases or assumptions that may influence your response. Instead, present the question in a neutral manner to allow for a more objective and balanced answer.

Provide instructions when necessary: If the desired output requires a specific format, style, or structure, include clear and concise instructions within the rewritten prompt to guide you in generating the response accordingly.

Ensure the prompt length is appropriate: While rewriting, make sure the prompt is neither too short nor too long. A well-crafted prompt should be long enough to provide sufficient context and clarity, yet concise enough to prevent any confusion or loss of focus.

With these guidelines in mind, I would like you to transform yourself into a prompt rewriter, capable of refining and enhancing any given prompts to ensure they elicit the most accurate, relevant, and comprehensive responses when used with ChatGPT. Please provide an example of how you would rewrite a given prompt based on the instructions provided above.

Rewrite this prompt: “please generate a detailed summary of the given text
”"""


class LLM:
    def __init__(self, llm_model, api_key=None):
        self.model_name = llm_model
        self.api = api_key

        if self.model_name not in ["bard", "gpt3", "ollama", "mock"]:
            raise Exception("Invalid LLM model")

        if self.model_name == "mock":
            print("Mock model created")
        print("llm model name: ", self.model_name)
        print("api key: ", self.api)

        if self.model_name == "ollama":
            model_config = {
                "name": "summarizer",
                "modelfile": "FROM zephyr:latest\nSYSTEM Can you provide a comprehensive summary of the given video script? The summary should cover all the key points and main ideas presented in the original text, while also condensing the information into a concise and easy-to-understand format. Please ensure that the summary includes relevant details and examples that support the main ideas, while avoiding any unnecessary information or repetition. The length of the summary should be appropriate for the length and complexity of the original text, providing a clear and accurate overview without omitting any important information.",
            }
            requests.post("http://ollama:11434/api/create", json=model_config)
            print("ollama model created")

        if self.model_name == "gpt3":
            openai.api_key = self.api
            print("gpt3 model created")

        if self.model_name == "bard":
            cookies = {
                "NID": "512",
                "__Secure-1PSIDTS": "sidts-CjIBYfD7ZwvpGdmOt4PJ9ftRaWacptiLltVeCYItz6JPJ4NROMQL6-JhGX771zlOBzQ2mRAA",
                "__Secure-3PSIDTS": "sidts-CjIBYfD7ZwvpGdmOt4PJ9ftRaWacptiLltVeCYItz6JPJ4NROMQL6-JhGX771zlOBzQ2mRAA",
                "__Secure-1PSIDCC": "AKEyXzVTHF5L-1XDNTUsNnAGtRak3ULaCU_M5EfBatExpPJS3fVyWJz6NHWKzwq3Ue6NM2xXvDks",
                "__Secure-3PSIDCC": "AKEyXzVM5ZBpuZPuI-qrDqI-3bSAA51-Kk9FJ6-AvQ09FtVzB8a4ZkUNs6erSkYSgfCXKmq_on0",
            }
            self.model = Gemini(cookies=cookies)

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
                        "content": "You are a summarizing AI. Provide a comprehensive summary of the given video script? The summary should cover all the key points and main ideas presented in the original text, while also condensing the information into a concise and easy-to-understand format. Ensure that the summary includes relevant details and examples that support the main ideas, while avoiding any unnecessary information or repetition. The length of the summary should be appropriate for the length and complexity of the original text, providing a clear and accurate overview without omitting any important information. Do not mention that it is an video script.",
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

            prompt = """
You are a summarizing AI. Provide a comprehensive summary of the given video script? The summary should cover all the key points and main ideas presented in the original text, while also condensing the information into a concise and easy-to-understand format. Ensure that the summary includes relevant details and examples that support the main ideas, while avoiding any unnecessary information or repetition. The length of the summary should be appropriate for the length and complexity of the original text, providing a clear and accurate overview without omitting any important information.


"""
            print(self.model.generate_content(prompt + question))
            return self.model.generate_content(prompt + question)

        elif self.model_name == "mock":
            return """This is a long text that is a mock answer.
                    It has multiple lines and is a long answer.
                    It is a mock answer for testing purposes.
            """

        else:
            raise Exception("Invalid LLM model in getting answer.")
