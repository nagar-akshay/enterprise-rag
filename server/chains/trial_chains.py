from server.db.db_utils import retriever
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from server.models.llm import llm

# Function to format document content
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Function to classify query types
QUERY_TYPES = {
    "Data Retrieval": '''Involves retrieving or lookup of facts or data from text documents. Eg: 
    What is the name of company providing fire service. 
    What is the process to modify company logo.
    ''',
    "Data Computation": '''Involves numerical computation on some tables or numerical data to arrive on answer. Eg: 
    Who are the top 5 most profitable customers based on sales from July to June.
    Which department has highest profit to sales ratio in Delhi.
    ''',
}

def get_query_types(query):
    return '\n'.join([f"{query_type}: {description}" for (query_type, description) in QUERY_TYPES.items()])

# Function to format CSV file names and descriptions
def format_csv_file_names(data):
    return "\n".join([f"{file_data['name']}:{file_data['description']}" for file_data in data])

# Function to get relevant CSV files
def get_csv_files(query):
    return [
        {"name": "Sales.csv", "description": "Data on sales of EV in Delhi."},
        {"name": "Operations.csv", "description": "Data on quality control operations in Gurgaon plant."},
    ]

def get_csv_file_descriptions(query):
    return format_csv_file_names(get_csv_files(query))

query_classification_prompt = PromptTemplate.from_template("""
Classify the below query into one of the query types. You need to return only the name of the query type, do not return anything else.

Query:
{query}

Query Types:
{query_types}
""")

document_selection_prompt = PromptTemplate.from_template("""
Given the below query and csv files with their description, find the list most relevant csv files that will be able to answer the query. Just return the list filenames in python list form [file1, file2, ..., file3] and nothing else. Even if there is a single file, return it in list form.

Query:
{query}

Files:
{file_descriptions}

Relevant Files: 
""")


query_classification_chain = (
    {"query_types" : get_query_types ,"query": RunnablePassthrough()}
    | query_classification_prompt
    | llm
    | StrOutputParser()
)

document_selection_chain = (
    {"file_descriptions": get_csv_file_descriptions, "query": RunnablePassthrough()}
    | document_selection_prompt
    | llm
    | StrOutputParser()
)



if __name__ == "__main__":
    print(query_classification_chain.invoke("Which team handles zoom dashboard integrations ?"))
    print(query_classification_chain.invoke("Which are the top 5 customers by percentage of sales ?"))
    print(query_classification_chain.invoke("What is the process for hiring a candidate ?"))
    print(query_classification_chain.invoke("Is it worth it to invest in EV sales to reduce pressure on Delhi units ?"))
