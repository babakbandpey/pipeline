from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser


def create_script(text, info):
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, api_key=text)

    output_parser = JsonOutputParser()
    template = """You are a llm which has to change the information inside the script the informations provided.
                    The returned file should be in python and well formatted.
                    SCRIPT: {text},
                    INFO: {info}"""

    prompt = PromptTemplate(
                    template=template,
                    input_variables=["text", "info"],
                    )

    chain =  prompt | llm | output_parser
    answer = chain.invoke({"text": text, "info": info})

    return answer
    