from functools import partial
import pathlib
from dotenv import load_dotenv
import yaml

from app.src.services.hanadb import HanaDB
from ai_api_client_sdk.models.status import Status
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration.models.template import Template, TemplateValue
from gen_ai_hub.orchestration.models.content_filter import AzureContentFilter
from gen_ai_hub.orchestration.service import OrchestrationService
load_dotenv()
from gen_ai_hub.proxy import get_proxy_client
import os

ORC_API_URL=os.environ.get("ORC_API_URL")

# Create a prompt template
prompt_1 = """
[INST]
You always answer the questions with markdown formatting. The markdown formatting you support: headings, bold, italic, links, tables, lists, code blocks, and blockquotes. You must omit that you answer the questions with markdown.

Any HTML tags must be wrapped in block quotes, for example ```<html>```. You will be penalized for not rendering code in block quotes.

When returning code blocks, specify language.

Given the document and the current conversation between a user and an assistant, your task is as follows: answer any user query by using information from the document. Always answer as helpfully as possible, while being safe. When the question cannot be answered using the context or document, output the following response: "I cannot answer that question based on the provided document.".

Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
<</SYS>>
Context:
{{?context}}
Question:
{{?query}}
[INST]
"""

class LLMService:
    def __init__(self, hdb: HanaDB) -> None:
        self.client = get_proxy_client()
        self.orchestration_service = OrchestrationService(api_url=ORC_API_URL, proxy_client=self.client)
        self.hdb = hdb

    ## Querying Hana vectordb and building the context
    def get_context(self, query: str, query_vector: str, metric='COSINE_SIMILARITY', k = 4) -> str:
        context = self.hdb.run_vector_search(query, query_vector, 'COSINE_SIMILARITY', k)
        context_text = ' '.join([doc[1] for doc in context])
        return context_text

    ## Sending request to aicore LLM
    def send_request(self, prompt, _print=True, _model='ibm--granite-13b-chat', **kwargs):
        config = OrchestrationConfig(
            llm=LLM(name=_model),
            template=Template(messages=[UserMessage(prompt)])
        )
        template_values = [TemplateValue(name=key, value=value) for key, value in kwargs.items()]
        answer = self.orchestration_service.run(config=config, template_values=template_values)
        result = answer.module_results.llm.choices[0].message.content
        if _print:
            formatted_prompt = answer.module_results.templating[0].content
            print(f"<-- PROMPT --->\n{formatted_prompt if _print else prompt}\n<--- RESPONSE --->\n{result}")   
        return result

    def generate(self, question: str, query_vector: str):
        # Getting the context by querying hana vector db
        prompt_context = self.get_context(question,query_vector, k=1)
        # Sending the request to LLM
        f_1 = partial(self.send_request, prompt=prompt_1)
        response = f_1(context=prompt_context, query=question)
        return response
