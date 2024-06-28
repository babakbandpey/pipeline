"""
Create script module
"""
"""
Create script module
"""
# Import the required classes from the LangChain library.
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def create_script(text:str, info:str, api_key:str):
    """
    Create a script by modifying the information inside the provided script based on the given information.

    Parameters:
    text (str): The script content that needs to be modified.
    info (str): The information to be integrated into the script.
    api_key (str): The API key for authenticating the ChatOpenAI model.

    Returns:
    dict: The modified script in JSON format.
    """
    
    # Initialize the ChatOpenAI model with the specified parameters.
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, api_key=api_key)

    # Initialize the JSON output parser.
    output_parser = JsonOutputParser()
    
    # Define the template for the prompt to be used by the model.
    template = """You are an LLM which has to change the information inside the script with the information provided.
                    The returned file should be in Python and well formatted.
                    SCRIPT: {text},
                    INFO: {info}"""
    
    # Create a PromptTemplate object using the defined template and input variables.
    prompt = PromptTemplate(
                    template=template,
                    input_variables=["text", "info"],
                    )
    
    # Chain the prompt, the model, and the output parser together.
    chain = prompt | llm | output_parser
    
    # Invoke the chain with the provided text and info to get the modified script.
    answer = chain.invoke({"text": text, "info": info})
    
    return answer
